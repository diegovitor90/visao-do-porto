from threading import get_ident
from time import sleep

import cv2
import numpy as np
import pytest

from vision.metrics import Metrics
from vision.sources import BufferedSource, FileSource, RtspSource, WebcamSource


@pytest.fixture
def video(tmp_path):
    path = tmp_path / "teste.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 25, (64, 48))
    assert writer.isOpened()
    try:
        for i in range(24):
            writer.write(np.full((48, 64, 3), i * 5, dtype=np.uint8))
    finally:
        writer.release()
    return path


@pytest.mark.parametrize("sem_descarte", [False, True])
def test_worker_preserva_ordem_e_libera_video(video, sem_descarte):
    source = FileSource(video)
    metrics = Metrics()
    with BufferedSource(source, sem_descarte) as frames:
        ids = []
        for frame in frames:
            sleep(0.015)
            ids.append(frame.frame_id)
            metrics.record(frame.capturado_em)
    assert ids == sorted(set(ids))
    assert ids[-1] == 23
    assert len(ids) + frames.dropped == 24
    if sem_descarte:
        assert ids == list(range(24))
    else:
        assert frames.dropped > 0
    assert not source._capture.isOpened()
    assert not frames._thread.is_alive()
    result = metrics.snapshot(frames.dropped)
    assert 0 < result["latencia_mediana_ms"] <= result["latencia_p95_ms"]
    assert result["fps"] > 0


def test_encerra_produtor_esperando_consumidor(video):
    source = FileSource(video)
    with BufferedSource(source, sem_descarte=True) as frames:
        next(iter(frames))
    assert not frames._thread.is_alive()
    assert not source._capture.isOpened()


@pytest.mark.parametrize("source", [WebcamSource(0), RtspSource("rtsp://127.0.0.1/live")])
def test_captura_ao_vivo_abre_le_e_libera_na_mesma_thread(monkeypatch, source):
    caller = get_ident()
    operations = []

    class Capture:
        def __init__(self, *args):
            operations.append(("create", get_ident()))

        def isOpened(self):
            return True

        def open(self, *args):
            operations.append(("open", get_ident()))
            return True

        def read(self):
            operations.append(("read", get_ident()))
            return False, None

        def release(self):
            operations.append(("release", get_ident()))

    monkeypatch.setattr(cv2, "VideoCapture", Capture)
    with BufferedSource(source, sem_descarte=True) as frames:
        assert list(frames) == []
    assert operations[0][0] == "create"
    assert operations[-2][0] == "read"
    assert operations[-1][0] == "release"
    assert {thread for _, thread in operations} == {frames._thread.ident}
    assert frames._thread.ident != caller
