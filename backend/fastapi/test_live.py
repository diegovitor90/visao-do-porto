import asyncio
from datetime import datetime, timezone
from threading import Event
from time import monotonic, perf_counter, sleep
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import numpy as np
from fastapi.testclient import TestClient

import main
from vision import service
from vision.sources import Frame


class FakeSource:
    def __init__(self, disconnect=None):
        self.disconnect = disconnect or Event()
        self.closed = False
        self.index = 0

    def read(self):
        if self.disconnect.wait(0.01):
            return None
        frame = Frame(self.index, datetime.now(timezone.utc), np.zeros((32, 32, 3), dtype=np.uint8),
                      perf_counter())
        self.index += 1
        return frame

    def close(self):
        self.closed = True


def wait_for(condition, seconds=3):
    deadline = monotonic() + seconds
    while monotonic() < deadline:
        if result := condition():
            return result
        sleep(0.01)
    raise AssertionError("A fonte simulada não atingiu o estado esperado.")


def test_reconexao_e_fontes_independentes(caplog):
    first_disconnect = Event()
    a_opened = Event()
    sources = []
    pipeline_sessions = {}

    def open_source(config):
        first_a = config.camera_id == "CAM-A" and not a_opened.is_set()
        if first_a:
            a_opened.set()
        source = FakeSource(first_disconnect if first_a else None)
        sources.append(source)
        return source

    def pipeline(tracker, _, zones, camera, *rest):
        pipeline_sessions.setdefault(camera, []).append(tracker.session_id)
        return SimpleNamespace(process=lambda frame: SimpleNamespace(image=frame.imagem))

    zones = Mock(**{"get.return_value": []})
    publisher = Mock()
    registry = service.SourceService(zones, publisher)

    def live(name, source="WEBCAM"):
        options = {"rtsp_url": "rtsp://userteste:segredoteste@127.0.0.1/live"} if source == "RTSP" else {}
        session = service.LiveSession(service.SourceRequest(camera_id=name, source=source, **options),
                                      zones, publisher, open_source, pipeline, retry_initial=0.01)
        session.thread.start()
        return session

    a = live("CAM-A", "RTSP")
    b = live("CAM-B")
    try:
        before = wait_for(lambda: a.snapshot()["session_id"])
        second = wait_for(lambda: b.snapshot()["session_id"])
        wait_for(lambda: a.snapshot()["status"] == b.snapshot()["status"] == "ATIVA")

        async def get_packet():
            async with asyncio.timeout(2):
                stream = a.stream()
                try:
                    return await anext(stream)
                finally:
                    await stream.aclose()

        packet = asyncio.run(get_packet())
        assert packet.startswith(b"--frame\r\nContent-Type: image/jpeg")
        assert b"\xff\xd8" in packet
        first_disconnect.set()
        after = wait_for(lambda: (current if (current := a.snapshot()["session_id"]) != before else None))
        assert after != before and after != second
        assert b.snapshot()["session_id"] == second
        assert len(pipeline_sessions["CAM-A"]) == 2
        assert len(pipeline_sessions["CAM-B"]) == 1
        assert "segredoteste" not in caplog.text
    finally:
        assert registry.stop(a)
        assert registry.stop(b)
    assert all(source.closed for source in sources)
    assert not a.thread.is_alive() and not b.thread.is_alive()


def test_rotas_e_sigilo_rtsp(monkeypatch, caplog):
    live_class = service.LiveSession
    publisher = Mock()
    publisher.__enter__ = Mock(return_value=publisher)
    publisher.__exit__ = Mock(return_value=False)
    zones = Mock(**{"get.return_value": []})

    def failing(config):
        raise OSError(config.rtsp_url.get_secret_value())

    def new_session(config, zones, publisher):
        return live_class(config, zones, publisher, source_factory=failing, retry_initial=0.03)

    monkeypatch.setattr(service, "LiveSession", new_session)
    monkeypatch.setattr(main, "EventPublisher", lambda: publisher)
    monkeypatch.setattr(main, "ZoneProvider", lambda: zones)
    secret = "credencial-sentinela"
    valid = {"source": "RTSP", "camera_id": "CAM-A", "rtsp_url": f"rtsp://usuario:{secret}@127.0.0.1/live"}
    with TestClient(main.app) as client:
        bad = client.post("/api/v1/sources", json={**valid, "camera_id": "../invalida"})
        assert bad.status_code == 422 and secret not in bad.text
        created = client.post("/api/v1/sources", json=valid)
        assert created.status_code == 201 and secret not in created.text
        sid = created.json()["id"]
        wait_for(lambda: "Falha na fonte da câmera CAM-A" in caplog.text)
        status = client.get("/api/v1/vision/status")
        assert status.json()["sources"][0]["id"] == sid
        assert "model_loaded" in status.json() and "fps" in status.json()
        assert secret not in status.text and secret not in caplog.text
        assert client.delete(f"/api/v1/sources/{sid}").status_code == 204
        assert client.get(f"/api/v1/sources/{sid}/stream").status_code == 404
        assert client.delete(f"/api/v1/sources/{sid}").status_code == 404


def test_evidencia_valida_e_travessia(tmp_path, monkeypatch):
    root = tmp_path / "evidencias"
    root.mkdir()
    ref = f"{uuid4()}.jpg"
    (root / ref).write_bytes(b"\xff\xd8JPEG")
    (tmp_path / "externo.jpg").write_bytes(b"segredo")
    monkeypatch.setattr(main, "EVIDENCE_DIR", root)
    client = TestClient(main.app)
    content = client.get(f"/api/v1/evidencias/{ref}")
    assert content.status_code == 200 and content.headers["content-type"] == "image/jpeg"
    for path in ("externo.jpg", "..%2Fexterno.jpg", "..%5Cexterno.jpg", f"{uuid4()}.jpg"):
        assert client.get(f"/api/v1/evidencias/{path}").status_code == 404


def test_evidencia_link_externo(tmp_path, monkeypatch):
    root = tmp_path / "evidencias"
    root.mkdir()
    outside_dir = tmp_path / "evidencias-externas"
    outside_dir.mkdir()
    outside = outside_dir / "externo.jpg"
    outside.write_bytes(b"\xff\xd8privado")
    ref = f"{uuid4()}.jpg"
    candidate = root / ref
    try:
        candidate.symlink_to(outside)
    except OSError as exc:
        if getattr(exc, "winerror", None) not in {5, 1314} and not isinstance(exc, PermissionError):
            raise
        # Sem privilégio no Windows, simula apenas o resultado da resolução do link.
        resolve = type(root).resolve

        def resolve_link(path, *args, **kwargs):
            return resolve(outside if path == candidate else path, *args, **kwargs)

        monkeypatch.setattr(type(root), "resolve", resolve_link)
    assert candidate.resolve(strict=True) == outside.resolve(strict=True)
    monkeypatch.setattr(main, "EVIDENCE_DIR", root)
    response = TestClient(main.app).get(f"/api/v1/evidencias/{ref}")
    assert response.status_code == 404
    assert b"privado" not in response.content
