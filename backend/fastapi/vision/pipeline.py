from collections.abc import Callable
from dataclasses import dataclass

import cv2
from numpy import ndarray

from .association import EpiDetection, associar
from .events import EventoVisao, SourceType, save_event
from .rules import Rules
from .sources import Frame
from .state import Compliance, ItemState, TemporalState
from .tracker import PersonTracker, TrackedPerson
from .zones import Zone, ZonePresence

COLORS = {
    Compliance.CONFORME: (60, 200, 70),
    Compliance.NAO_CONFORME: (60, 60, 220),
    Compliance.INDETERMINADO: (160, 160, 160),
}


@dataclass(frozen=True)
class ProcessedFrame:
    image: ndarray
    states: dict[int, dict[str, ItemState]]
    events: list[EventoVisao]


class Pipeline:
    def __init__(self, tracker: PersonTracker, detect_epi: Callable | None = None,
                 zones: list[Zone] | None = None, camera_id: str = "CAM-LAB-01",
                 source: SourceType = SourceType.ARQUIVO,
                 record_event: Callable = save_event):
        self.tracker = tracker
        self.detect_epi = detect_epi
        self.state = TemporalState()
        self.presence = ZonePresence(zones or [])
        self.rules = Rules(camera_id, tracker.session_id, source)
        self.record_event = record_event

    def process(self, frame: Frame) -> ProcessedFrame:
        people = self.tracker.track(frame.imagem)
        image = frame.imagem.copy()
        states = self._evaluate(frame, people) if self.detect_epi is not None else {}
        for person in people:
            items = states.get(person.track_id, {})
            status = [item.status for item in items.values()]
            color = (240, 180, 60)
            if status:
                overall = (Compliance.NAO_CONFORME if Compliance.NAO_CONFORME in status else
                           Compliance.INDETERMINADO if Compliance.INDETERMINADO in status else
                           Compliance.CONFORME)
                color = COLORS[overall]
            x1, y1, x2, y2 = map(round, person.bbox)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            label = str(person.track_id)
            if items:
                label += " " + " ".join(f"{key}: {item.status}" for key, item in items.items())
            cv2.putText(image, label, (x1, max(16, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, color, 2)
        presence = self.presence.update(people, image)
        events = [self.record_event(event, image) for event in
                  self.rules.evaluate(presence, people, states, frame.timestamp)]
        return ProcessedFrame(image, states, events)

    def _evaluate(self, frame: Frame, people: list[TrackedPerson]) -> dict[int, dict[str, ItemState]]:
        epis = [
            EpiDetection(item["class_name"], tuple(item["bbox"][k] for k in ("x1", "y1", "x2", "y2")),
                         item["confidence"])
            for item in self.detect_epi(frame.imagem)
        ]
        return self.state.update(frame.frame_id, frame.timestamp, frame.imagem.shape[1::-1],
                                 people, associar(people, epis))
