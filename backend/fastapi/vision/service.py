import asyncio
import logging
from enum import StrEnum
import re
from threading import Event, Lock, Thread
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import cv2
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from .config import LIVE_RETRY_INITIAL, LIVE_RETRY_MAX, LIVE_STOP_TIMEOUT
from .detector import detectar_epi
from .events import CAMERA_PATTERN, SourceType
from .metrics import Metrics
from .pipeline import Pipeline
from .sources import BufferedSource, RtspSource, WebcamSource
from .spring_client import EventPublisher, ZoneProvider
from .tracker import PersonTracker

logger = logging.getLogger(__name__)


class LiveType(StrEnum):
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"


class SourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: LiveType
    camera_id: str = Field(pattern=CAMERA_PATTERN)
    webcam_index: int | None = Field(default=None, ge=0, le=255)
    rtsp_url: SecretStr | None = None

    @model_validator(mode="after")
    def validate_source(self):
        if self.source == LiveType.WEBCAM:
            if self.rtsp_url is not None:
                raise ValueError("Parâmetros inválidos para webcam.")
        else:
            if self.webcam_index is not None or self.rtsp_url is None:
                raise ValueError("Parâmetros inválidos para RTSP.")
            value = self.rtsp_url.get_secret_value()
            parsed = urlsplit(value)
            if (parsed.scheme not in {"rtsp", "rtsps"} or not parsed.hostname
                    or len(value) > 2048 or re.search(r"[\x00-\x20\x7f]", value)):
                raise ValueError("Endereço RTSP inválido.")
            _ = parsed.port
        return self


def _open_source(config: SourceRequest):
    if config.source == LiveType.WEBCAM:
        return WebcamSource(config.webcam_index or 0)
    return RtspSource(config.rtsp_url.get_secret_value())


class LiveSession:
    def __init__(self, config: SourceRequest, zones: ZoneProvider, publisher: EventPublisher,
                 source_factory=_open_source, pipeline_factory=Pipeline, retry_initial=LIVE_RETRY_INITIAL):
        self.id = uuid4()
        self.config = config
        self.zones = zones
        self.publisher = publisher
        self.source_factory = source_factory
        self.pipeline_factory = pipeline_factory
        self.retry_initial = retry_initial
        self._stop = Event()
        self._lock = Lock()
        self._frames = None
        self._jpeg = None
        self._sequence = 0
        self._status = "INICIANDO"
        self._session_id = None
        self._metrics = {}
        self.thread = Thread(target=self._run, name=f"visao-fonte-{self.id}", daemon=True)

    def snapshot(self) -> dict:
        with self._lock:
            return {"id": str(self.id), "camera_id": self.config.camera_id, "source": self.config.source,
                    "session_id": str(self._session_id) if self._session_id else None,
                    "status": self._status, "fps": 0, **self._metrics}

    def request_stop(self) -> None:
        self._stop.set()
        with self._lock:
            self._status = "ENCERRANDO"
            if self._frames:
                self._frames.close()

    async def stream(self):
        seen = 0
        while not self._stop.is_set():
            with self._lock:
                sequence, jpeg = self._sequence, self._jpeg
            if jpeg is not None and sequence != seen:
                seen = sequence
                yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                       + str(len(jpeg)).encode() + b"\r\n\r\n" + jpeg + b"\r\n")
            else:
                await asyncio.sleep(0.025)

    def _run(self) -> None:
        delay = self.retry_initial
        while not self._stop.is_set():
            try:
                zones = self.zones.get(self.config.camera_id)
                if self._stop.is_set():
                    break
                tracker = PersonTracker()
                pipeline = self.pipeline_factory(tracker, detectar_epi, zones, self.config.camera_id,
                                                 SourceType(self.config.source), self.publisher.record)
                with BufferedSource(self.source_factory(self.config)) as frames:
                    with self._lock:
                        self._frames = frames
                        self._session_id = tracker.session_id
                        self._metrics = {}
                        if self._stop.is_set():
                            frames.close()
                    metrics = Metrics(window=120)
                    for frame in frames:
                        processed = pipeline.process(frame)
                        ok, jpeg = cv2.imencode(".jpg", processed.image)
                        metrics.record(frame.capturado_em)
                        with self._lock:
                            if self._stop.is_set():
                                break
                            self._status = "ATIVA"
                            self._metrics = metrics.snapshot(frames.dropped)
                            if ok:
                                self._jpeg = jpeg.tobytes()
                                self._sequence += 1
                        delay = self.retry_initial
            except Exception:
                # Exceções de captura podem conter a URL original.
                if not self._stop.is_set():
                    logger.warning("Falha na fonte da câmera %s.", self.config.camera_id)
            finally:
                with self._lock:
                    self._frames = None
                    self._jpeg = None
                    self._metrics = {}
            if not self._stop.is_set():
                with self._lock:
                    self._status = "RECONECTANDO"
                logger.info("Nova tentativa para câmera %s em %g s.", self.config.camera_id, delay)
                if self._stop.wait(delay):
                    break
                delay = min(LIVE_RETRY_MAX, delay * 2)
        with self._lock:
            self._status = "ENCERRADA"


class SourceService:
    def __init__(self, zones: ZoneProvider, publisher: EventPublisher):
        self.zones = zones
        self.publisher = publisher
        self._sessions: dict[UUID, LiveSession] = {}
        self._lock = Lock()

    def start(self, config: SourceRequest) -> dict:
        session = LiveSession(config, self.zones, self.publisher)
        with self._lock:
            self._sessions[session.id] = session
            session.thread.start()
        return session.snapshot()

    def get(self, source_id: UUID) -> LiveSession | None:
        with self._lock:
            return self._sessions.get(source_id)

    def list(self) -> list[dict]:
        with self._lock:
            return [session.snapshot() for session in self._sessions.values()]

    def stop(self, session: LiveSession) -> bool:
        session.request_stop()
        session.thread.join(LIVE_STOP_TIMEOUT)
        if session.thread.is_alive():
            return False
        with self._lock:
            self._sessions.pop(session.id, None)
        return True

    def close(self) -> None:
        with self._lock:
            sessions = list(self._sessions.values())
        for session in sessions:
            session.request_stop()
        for session in sessions:
            if not self.stop(session):
                logger.warning("Captura da câmera %s ainda está encerrando.", session.config.camera_id)
