from contextlib import closing
import sqlite3
from threading import Event, Thread

import httpx
import numpy as np
import pytest

from test_rules import setup
from test_zones import zone
from vision import events, spring_client
from vision.spring_client import EventPublisher, ZoneProvider
from vision.zones import ZONE_LIST


def test_cache_spring_validado_e_fallback(tmp_path, caplog):
    area = zone([(0, 0), (1, 0), (0, 1)])

    def online(request):
        assert request.url.path == "/api/v1/cameras/CAM-A/zonas"
        return httpx.Response(200, json=[area.model_dump(mode="json")])

    cache = tmp_path / "cache"
    assert ZoneProvider(cache, transport=httpx.MockTransport(online)).get("CAM-A") == [area]

    def offline(request):
        raise httpx.ConnectError("offline")

    provider = ZoneProvider(cache, transport=httpx.MockTransport(offline))
    assert provider.get("CAM-A") == [area]
    assert provider.get("CAM-B") == []
    with pytest.raises(ValueError):
        provider.get("../fora")
    assert "consultando o cache" in caplog.text


@pytest.mark.parametrize("failure", [503, 408, 429, None])
def test_fila_persiste_reenvia_em_ordem_e_rejeita(tmp_path, failure, caplog):
    first, = setup()(0)
    second, = setup()(0)
    third, = setup()(0)
    fourth, = setup()(0)
    path = tmp_path / "fila.sqlite3"
    received = []
    codes = iter([failure, 201, 200, 409, 201])
    now = [100]

    def send(request):
        assert request.url.path == "/api/v1/eventos"
        from vision.events import EventoVisao
        event = EventoVisao.model_validate_json(request.content)
        received.append(event.event_id)
        code = next(codes)
        if code is None:
            raise httpx.ReadTimeout("offline")
        return httpx.Response(code)

    publisher = EventPublisher(path, clock=lambda: now[0], transport=httpx.MockTransport(send))
    for event in [first, second, first, third, fourth]:
        publisher.enqueue(event)
    assert publisher.publish_once() == 1
    publisher.http.close()

    restarted = EventPublisher(path, clock=lambda: now[0], transport=httpx.MockTransport(send))
    assert restarted.publish_once() == 1
    now[0] += 1
    for _ in range(4):
        assert restarted.publish_once() == 0
    assert restarted.publish_once() == 60
    restarted.enqueue(third)
    assert restarted.publish_once() == 60
    restarted.http.close()
    assert received == [first.event_id, first.event_id, second.event_id, third.event_id, fourth.event_id]
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("SELECT event_id, codigo FROM rejeitados").fetchall() == [(str(third.event_id), 409)]
    assert first.explanation not in caplog.text


def test_publicacao_em_thread_e_encerramento(tmp_path):
    delivered = Event()

    def send(_):
        delivered.set()
        return httpx.Response(201)

    with EventPublisher(tmp_path / "fila.sqlite3", transport=httpx.MockTransport(send)) as publisher:
        event, = setup()(0)
        publisher.enqueue(event)
        assert delivered.wait(2)
    assert not publisher._thread.is_alive()

def test_cli_e_api_nao_enviam_o_mesmo_evento_ao_mesmo_tempo(tmp_path):
    started, release = Event(), Event()
    path = tmp_path / "fila.sqlite3"

    def send(_):
        started.set()
        assert release.wait(3)
        return httpx.Response(201)

    transport = httpx.MockTransport(send)
    first = EventPublisher(path, clock=lambda: 100, transport=transport)
    second = EventPublisher(path, clock=lambda: 100, transport=transport)
    event, = setup()(0)
    first.enqueue(event)
    background = Thread(target=first.publish_once)
    background.start()
    try:
        assert started.wait(2)
        assert second.publish_once() == 15
    finally:
        release.set()
        background.join(3)
        first.http.close()
    assert not background.is_alive()
    assert second.publish_once() == 60
    second.http.close()


def test_cache_separa_ids_do_windows_e_le_formato_anterior(tmp_path):
    original = zone([(0, 0), (1, 0), (0, 1)])
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "Legada.json").write_text(ZONE_LIST.dump_json([original]).decode(), encoding="utf-8-sig")

    def online(request):
        camera = request.url.path.split("/")[-2]
        return httpx.Response(200, json=[original.model_copy(update={"nome": camera}).model_dump(mode="json")])

    provider = ZoneProvider(cache, transport=httpx.MockTransport(online))
    for camera in ("CAM-A", "cam-a", "CON"):
        assert provider.get(camera)[0].nome == camera
    provider.transport = httpx.MockTransport(lambda _: httpx.Response(503))
    for camera in ("CAM-A", "cam-a", "CON"):
        assert provider.get(camera)[0].nome == camera
    assert provider.get("Legada") == [original]
    assert provider.get("legada") == []


def test_falha_no_jsonl_nao_descarta_evento_da_fila(tmp_path, monkeypatch, caplog):
    event, = setup()(0)
    received = []
    publisher = EventPublisher(tmp_path / "fila.sqlite3", transport=httpx.MockTransport(
        lambda request: received.append(events.EventoVisao.model_validate_json(request.content)) or httpx.Response(201)))
    monkeypatch.setattr(spring_client, "save_evidence", lambda item, image: events.save_evidence(item, image, tmp_path))
    monkeypatch.setattr(spring_client, "append_event", lambda item: events.append_event(item, tmp_path))
    try:
        saved = publisher.record(event, np.zeros((8, 8, 3), dtype=np.uint8))
        assert publisher.publish_once() == 0
        assert received == [saved]
        assert (tmp_path / saved.evidence_ref).exists()
        assert "Falha ao gravar JSONL" in caplog.text
    finally:
        publisher.http.close()
