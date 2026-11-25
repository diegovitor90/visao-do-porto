from dataclasses import dataclass
from threading import Lock
from uuid import uuid4

from numpy import ndarray

from .config import PERSON_MODEL, local_weight
from .detector import carregar_peso

BBox = tuple[float, float, float, float]
_track_lock = Lock()


@dataclass(frozen=True)
class TrackedPerson:
    track_id: int
    bbox: BBox
    confidence: float


def _load_tracker():
    model = carregar_peso(local_weight(PERSON_MODEL))
    from ultralytics.trackers.basetrack import BaseTrack

    return model, BaseTrack


class PersonTracker:
    def __init__(self):
        self.session_id = uuid4()
        self._model = None
        self._counter = None
        self._last_id = 0

    def track(self, image: ndarray) -> list[TrackedPerson]:
        if self._model is None:
            self._model, self._counter = _load_tracker()
        with _track_lock:
            # A versão fixada do ByteTrack mantém um contador global para todos os modelos.
            previous = self._counter._count
            self._counter._count = self._last_id
            try:
                results = self._model.track(image, persist=True, tracker="bytetrack.yaml",
                                            classes=[0], device="cpu", verbose=False)
                self._last_id = self._counter._count
            finally:
                self._counter._count = previous

        people = []
        for result in results:
            if result.boxes is None or result.boxes.id is None:
                continue
            for box, track_id in zip(result.boxes, result.boxes.id.tolist()):
                people.append(TrackedPerson(int(track_id), tuple(box.xyxy[0].tolist()), float(box.conf[0])))
        return people
