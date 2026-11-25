from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from statistics import mean

from .association import ITEMS, Signal, SignalType
from .config import StateConfig
from .tracker import TrackedPerson


class Compliance(StrEnum):
    CONFORME = "CONFORME"
    NAO_CONFORME = "NAO_CONFORME"
    INDETERMINADO = "INDETERMINADO"


@dataclass(frozen=True)
class ItemState:
    status: Compliance = Compliance.INDETERMINADO
    confidence: float | None = None


@dataclass
class TrackHistory:
    first_seen: datetime
    last_frame: int
    signals: dict[str, deque[Signal]]
    states: dict[str, ItemState] = field(default_factory=dict)
    changes: int = 0
    observations: int = 0


class TemporalState:
    def __init__(self, config: StateConfig = StateConfig()):
        self.config = config
        self._tracks: dict[int, TrackHistory] = {}

    def update(self, frame_id: int, timestamp: datetime, size: tuple[int, int],
               people: list[TrackedPerson],
               signals: dict[int, dict[str, Signal]]) -> dict[int, dict[str, ItemState]]:
        cfg = self.config
        self._tracks = {key: track for key, track in self._tracks.items()
                        if frame_id - track.last_frame <= cfg.expire_frames}
        missing = self._tracks.keys() - {person.track_id for person in people}
        for track_id in missing:
            for history in self._tracks[track_id].signals.values():
                history.append(Signal())
        width, height = size
        result = {}
        for person in people:
            track = self._tracks.get(person.track_id)
            if track is None:
                track = TrackHistory(timestamp, frame_id, {item: deque(maxlen=cfg.window) for item in ITEMS})
                self._tracks[person.track_id] = track
            track.last_frame = frame_id
            track.observations += 1
            x1, y1, x2, y2 = person.bbox
            quality = (y2 - y1 >= cfg.min_height * height
                       and min(x1, width - x2) >= cfg.border * width
                       and min(y1, height - y2) >= cfg.border * height)
            states = {}
            for item, history in track.signals.items():
                history.append(signals[person.track_id][item] if quality else Signal())
                state = ItemState()
                if quality and track.observations >= cfg.min_observations:
                    for signal, status in ((SignalType.POSITIVO, Compliance.CONFORME),
                                           (SignalType.NEGATIVO, Compliance.NAO_CONFORME)):
                        confidences = [value.confidence for value in history
                                       if value.type == signal and value.confidence is not None]
                        if len(confidences) / len(history) >= cfg.agreement:
                            confidence = mean(confidences)
                            if confidence >= cfg.min_confidence:
                                state = ItemState(status, confidence)
                            break
                previous = track.states.get(item)
                if previous is not None and previous.status != state.status:
                    track.changes += 1
                states[item] = state
            track.states = states
            result[person.track_id] = states
        return result

    def oscillations(self, track_id: int, timestamp: datetime) -> tuple[int, float]:
        track = self._tracks[track_id]
        minutes = (timestamp - track.first_seen).total_seconds() / 60
        return track.changes, track.changes / minutes if minutes > 0 else 0
