from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np

from vision import tracker


def test_bytetrack_isolado_por_fonte_e_reinicio(monkeypatch):
    counter = SimpleNamespace(_count=90)
    loaded = []

    def load():
        ids = []

        def track(*args, **kwargs):
            if not ids:
                counter._count += 1
                ids.append(counter._count)
            return [SimpleNamespace(boxes=Boxes(ids))]

        model = Mock()
        model.track.side_effect = track
        loaded.append(model)
        return model, counter

    class Boxes(list):
        def __init__(self, ids):
            super().__init__([SimpleNamespace(xyxy=np.array([[1, 2, 3, 4]]), conf=[0.9])])
            self.id = np.array(ids)

    monkeypatch.setattr(tracker, "_load_tracker", load)
    a, b, reiniciada = (tracker.PersonTracker() for _ in range(3))
    assert len({a.session_id, b.session_id, reiniciada.session_id}) == 3
    image = np.zeros((32, 32, 3))
    assert a.track(image)[0].track_id == b.track(image)[0].track_id == 1
    assert a.track(image)[0].track_id == reiniciada.track(image)[0].track_id == 1
    assert counter._count == 90
    assert len(loaded) == 3
    assert loaded[0].track.call_args.kwargs == {
        "persist": True, "tracker": "bytetrack.yaml", "classes": [0], "device": "cpu", "verbose": False,
    }
