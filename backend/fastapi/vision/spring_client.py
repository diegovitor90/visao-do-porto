from contextlib import closing
from hashlib import sha256
import logging
import re
import sqlite3
from tempfile import NamedTemporaryFile
from threading import Event, Thread
from time import time
from pathlib import Path

import httpx
from numpy import ndarray

from .config import EVENT_QUEUE, SPRING_BASE_URL, ZONES_CACHE
from .events import CAMERA_PATTERN, EventoVisao, append_event, save_evidence
from .zones import ZONE_LIST, Zone, load_zones

logger = logging.getLogger(__name__)


class ZoneProvider:
    def __init__(self, cache: Path = ZONES_CACHE, base_url: str = SPRING_BASE_URL,
                 transport: httpx.BaseTransport | None = None):
        self.cache = cache
        self.base_url = base_url
        self.transport = transport

    def get(self, camera_id: str) -> list[Zone]:
        if not re.fullmatch(CAMERA_PATTERN, camera_id):
            raise ValueError("Identificador de câmera inválido.")
        # Um mesmo diretório Windows pode tratar nomes que só diferem em caixa como iguais.
        digest = sha256(camera_id.encode("ascii")).hexdigest()
        cache_file = self.cache / f"camera-{digest}.json"
        try:
            with httpx.Client(base_url=self.base_url, timeout=2, transport=self.transport, trust_env=False) as http:
                response = http.get(f"/api/v1/cameras/{camera_id}/zonas")
                response.raise_for_status()
                zones = ZONE_LIST.validate_json(response.content)
        except (httpx.HTTPError, ValueError):
            logger.warning("Zonas do Spring indisponíveis para câmera %s; consultando o cache.", camera_id)
            try:
                if cache_file.is_file():
                    return load_zones(cache_file)
                legacy_name = f"{camera_id}.json"
                for entry in self.cache.iterdir():
                    if entry.name == legacy_name and not entry.is_reserved():
                        return load_zones(entry)
            except (OSError, ValueError):
                pass
            logger.warning("Cache de zonas indisponível para câmera %s.", camera_id)
            return []
        tmp = None
        try:
            self.cache.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=self.cache, suffix=".tmp", delete=False) as temporary:
                tmp = Path(temporary.name)
                temporary.write(ZONE_LIST.dump_json(zones))
            tmp.replace(cache_file)
        except OSError:
            logger.warning("Falha ao salvar o cache de zonas da câmera %s.", camera_id)
        finally:
            if tmp is not None and tmp.exists():
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    logger.warning("Falha ao remover o cache temporário da câmera %s.", camera_id)
        return zones


class EventPublisher:
    def __init__(self, path: Path = EVENT_QUEUE, base_url: str = SPRING_BASE_URL,
                 transport: httpx.BaseTransport | None = None, clock=time):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.http = httpx.Client(base_url=base_url, timeout=2, transport=transport, trust_env=False)
        self.clock = clock
        self._wake = Event()
        self._stop = Event()
        self._thread = Thread(target=self._run, name="visao-publicador", daemon=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS pendentes (
                    ordem INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
                    tentativas INTEGER NOT NULL DEFAULT 0, proxima REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rejeitados (
                    event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, codigo INTEGER NOT NULL
                );
            """)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *_):
        self._stop.set()
        self._wake.set()
        self._thread.join()
        self.http.close()

    def enqueue(self, event: EventoVisao) -> None:
        event_id = str(event.event_id)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("""
                INSERT OR IGNORE INTO pendentes (event_id, payload, proxima)
                SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM rejeitados WHERE event_id = ?)
                """, (event_id, event.model_dump_json(), self.clock(), event_id))
        self._wake.set()

    def record(self, event: EventoVisao, image: ndarray) -> EventoVisao:
        saved = save_evidence(event, image)
        try:
            self.enqueue(saved)
        finally:
            try:
                append_event(saved)
            except OSError:
                logger.warning("Falha ao gravar JSONL do evento %s.", saved.event_id)
        return saved

    def publish_once(self) -> float:
        with closing(sqlite3.connect(self.path)) as db:
            with db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT event_id, payload, tentativas, proxima FROM pendentes ORDER BY ordem LIMIT 1"
                ).fetchone()
                if row is None:
                    return 60
                event_id, payload, attempts, due = row
                now = self.clock()
                if due > now:
                    return due - now
                # Reserva curta para evitar dois envios simultâneos pelo CLI e pela API.
                lease = now + 15
                db.execute("UPDATE pendentes SET proxima = ? WHERE event_id = ?", (lease, event_id))

            try:
                response = self.http.post("/api/v1/eventos", content=payload,
                                          headers={"Content-Type": "application/json"})
                code = response.status_code
            except httpx.RequestError:
                code = None

            with db:
                if code in (200, 201):
                    db.execute("DELETE FROM pendentes WHERE event_id = ? AND proxima = ?", (event_id, lease))
                elif code is None or code in (408, 429) or 500 <= code < 600:
                    delay = min(60, 2 ** min(attempts, 6))
                    db.execute("""
                        UPDATE pendentes SET tentativas = ?, proxima = ?
                        WHERE event_id = ? AND proxima = ?
                        """, (attempts + 1, self.clock() + delay, event_id, lease))
                    logger.warning("Envio do evento %s adiado após falha de comunicação.", event_id)
                    return delay
                else:
                    removed = db.execute("DELETE FROM pendentes WHERE event_id = ? AND proxima = ?", (event_id, lease))
                    if removed.rowcount:
                        db.execute("INSERT INTO rejeitados VALUES (?, ?, ?)", (event_id, payload, code))
                        logger.warning("Evento %s rejeitado pelo Spring (HTTP %s).", event_id, code)
        return 0

    def _run(self) -> None:
        while not self._stop.is_set():
            self._wake.clear()
            try:
                delay = self.publish_once()
            except sqlite3.Error:
                logger.warning("Falha ao acessar a fila local; nova tentativa em 1 s.")
                delay = 1
            self._wake.wait(min(delay, 1))
