from dataclasses import dataclass
from enum import StrEnum

from .config import AssociationConfig
from .tracker import BBox, TrackedPerson


class SignalType(StrEnum):
    POSITIVO = "POSITIVO"
    NEGATIVO = "NEGATIVO"
    SEM_EVIDENCIA = "SEM_EVIDENCIA"


@dataclass(frozen=True)
class Signal:
    type: SignalType = SignalType.SEM_EVIDENCIA
    confidence: float | None = None


@dataclass(frozen=True)
class EpiDetection:
    class_name: str
    bbox: BBox
    confidence: float


ITEMS = ("CAPACETE", "COLETE")
CLASSES = {
    "helmet": ("CAPACETE", SignalType.POSITIVO),
    "no_helmet": ("CAPACETE", SignalType.NEGATIVO),
    "vest": ("COLETE", SignalType.POSITIVO),
    "no_vest": ("COLETE", SignalType.NEGATIVO),
}


def _overlap(box: BBox, area: BBox) -> float:
    return (max(0, min(box[2], area[2]) - max(box[0], area[0]))
            * max(0, min(box[3], area[3]) - max(box[1], area[1])))


def associar(pessoas: list[TrackedPerson], epis: list[EpiDetection],
             cfg: AssociationConfig = AssociationConfig()) -> dict[int, dict[str, Signal]]:
    scores: dict[tuple[int, str, SignalType], float] = {}
    for epi in epis:
        if epi.class_name not in CLASSES:
            continue
        item, signal = CLASSES[epi.class_name]
        x1, y1, x2, y2 = epi.bbox
        if x1 >= x2 or y1 >= y2:
            continue
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        candidates = []
        for person in pessoas:
            px1, py1, px2, py2 = person.bbox
            height = py2 - py1
            if px1 >= px2 or height <= 0:
                continue
            if item == "CAPACETE":
                if not (px1 <= cx <= px2 and py1 <= cy <= py1 + cfg.head_fraction * height):
                    continue
                overlap = _overlap(epi.bbox, (px1, py1, px2, py1 + cfg.head_fraction * height))
            else:
                torso = (px1, py1 + cfg.torso_top * height, px2, py1 + cfg.torso_bottom * height)
                overlap = _overlap(epi.bbox, torso)
                if overlap < cfg.vest_min_overlap * (x2 - x1) * (y2 - y1):
                    continue
            candidates.append((overlap, -person.track_id))
        if candidates:
            _, reverse_id = max(candidates)
            key = (-reverse_id, item, signal)
            scores[key] = max(scores.get(key, 0), epi.confidence)

    result = {}
    for person in pessoas:
        signals = {}
        for item in ITEMS:
            positive = scores.get((person.track_id, item, SignalType.POSITIVO))
            negative = scores.get((person.track_id, item, SignalType.NEGATIVO))
            if positive is None and negative is None:
                signals[item] = Signal()
            elif positive is not None and negative is not None and abs(positive - negative) + 1e-9 < cfg.conflict_gap:
                signals[item] = Signal()
            elif negative is None or (positive is not None and positive > negative):
                signals[item] = Signal(SignalType.POSITIVO, positive)
            else:
                signals[item] = Signal(SignalType.NEGATIVO, negative)
        result[person.track_id] = signals
    return result
