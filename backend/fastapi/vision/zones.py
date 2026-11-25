from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

import cv2
import numpy as np
from numpy import ndarray
from pydantic import BaseModel, Field, TypeAdapter, field_validator

from .config import ZoneConfig
from .tracker import TrackedPerson


class RuleType(StrEnum):
    EPI_OBRIGATORIO = "EPI_OBRIGATORIO"
    AREA_RESTRITA = "AREA_RESTRITA"


Coordinate = Annotated[float, Field(ge=0, le=1)]


class Zone(BaseModel):
    zone_id: UUID
    nome: str = Field(min_length=1, max_length=120)
    polygon: list[tuple[Coordinate, Coordinate]] = Field(min_length=3, max_length=16)
    required_ppe: list[Literal["CAPACETE", "COLETE"]]
    rule_type: RuleType
    rule_id: str = Field(min_length=1, max_length=120)
    rule_version: int = Field(ge=1)
    ativa: bool

    @field_validator("polygon")
    @classmethod
    def validate_polygon(cls, points):
        if len(set(points)) != len(points):
            raise ValueError("Vértices repetidos.")
        edges = list(zip(points, points[1:] + points[:1]))
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in edges)
        if abs(area) < 1e-10:
            raise ValueError("Área do polígono deve ser positiva.")
        for (i, (a, b)), (j, (c, d)) in combinations(enumerate(edges), 2):
            if j == i + 1 or (i == 0 and j == len(edges) - 1):
                continue
            if _intersect(a, b, c, d):
                raise ValueError("Os lados do polígono não podem se cruzar.")
        for a, b, c in zip(points, points[1:] + points[:1], points[2:] + points[:2]):
            if _orientation(a, b, c) == 0 and sum((x - y) * (z - y) for x, y, z in zip(a, b, c)) > 0:
                raise ValueError("Lados adjacentes sobrepostos.")
        return points

    def pixels(self, size: tuple[int, int]) -> ndarray:
        return (np.asarray(self.polygon) * size).astype(np.float32)


def _orientation(a, b, c) -> int:
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 0 if abs(cross) < 1e-10 else 1 if cross > 0 else -1


def _intersect(a, b, c, d) -> bool:
    if any(max(a[i], b[i]) < min(c[i], d[i]) or max(c[i], d[i]) < min(a[i], b[i])
           for i in range(2)):
        return False
    return (_orientation(a, b, c) * _orientation(a, b, d) <= 0
            and _orientation(c, d, a) * _orientation(c, d, b) <= 0)


ZONE_LIST = TypeAdapter(list[Zone])


def load_zones(path: Path) -> list[Zone]:
    return ZONE_LIST.validate_json(path.read_text(encoding="utf-8-sig"))


@dataclass
class PresenceHistory:
    inside: bool = False
    consecutive_in: int = 0
    consecutive_out: int = 0


@dataclass(frozen=True)
class Presence:
    track_id: int
    zone: Zone
    inside: bool
    pes_incertos: bool


class ZonePresence:
    def __init__(self, zones: list[Zone], config: ZoneConfig = ZoneConfig()):
        self.zones = {zone.zone_id: zone for zone in zones if zone.ativa}
        if len(self.zones) != sum(zone.ativa for zone in zones):
            raise ValueError("zone_id ativo repetido.")
        self.config = config
        self._tracks: dict[tuple[int, UUID], PresenceHistory] = {}

    def update(self, people: list[TrackedPerson], image: ndarray) -> list[Presence]:
        size = image.shape[1::-1]
        result = []
        seen = set()
        for zone in self.zones.values():
            polygon = zone.pixels(size)
            cv2.polylines(image, [polygon.round().astype(np.int32)], True, (180, 135, 55), 2)
            cv2.putText(image, zone.nome, tuple(map(round, polygon[0])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (180, 135, 55), 1)
            for person in people:
                key = (person.track_id, zone.zone_id)
                seen.add(key)
                history = self._tracks.setdefault(key, PresenceHistory())
                x1, _, x2, y2 = person.bbox
                uncertain = y2 >= size[1] * (1 - self.config.feet_border)
                if uncertain:
                    history.consecutive_in = history.consecutive_out = 0
                elif cv2.pointPolygonTest(polygon, ((x1 + x2) / 2, y2), False) >= 0:
                    history.consecutive_in += 1
                    history.consecutive_out = 0
                    if history.consecutive_in >= self.config.enter_frames:
                        history.inside = True
                else:
                    history.consecutive_out += 1
                    history.consecutive_in = 0
                    if history.consecutive_out >= self.config.exit_frames:
                        history.inside = False
                result.append(Presence(person.track_id, zone, history.inside, uncertain))
        for key in self._tracks.keys() - seen:
            history = self._tracks[key]
            history.consecutive_in = 0
            history.consecutive_out += 1
            if history.consecutive_out >= self.config.exit_frames:
                del self._tracks[key]
            elif history.inside:
                track_id, zone_id = key
                result.append(Presence(track_id, self.zones[zone_id], True, True))
        return result
