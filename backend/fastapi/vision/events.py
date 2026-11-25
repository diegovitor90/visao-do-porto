import logging
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import UUID

import cv2
from numpy import ndarray
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from .config import EVENT_LOG, EVIDENCE_DIR

CAMERA_PATTERN = r"^[A-Za-z0-9_-]{1,100}$"
EVIDENCE_PATTERN = r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\.jpg$"
_log_lock = Lock()
logger = logging.getLogger(__name__)


class SourceType(StrEnum):
    ARQUIVO = "ARQUIVO"
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"


class EventType(StrEnum):
    INTRUSAO = "INTRUSAO"
    EPI_AUSENTE = "EPI_AUSENTE"
    EPI_INDETERMINADO = "EPI_INDETERMINADO"


class EventoVisao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["0.2"] = "0.2"
    event_id: UUID
    camera_id: str = Field(pattern=CAMERA_PATTERN)
    session_id: UUID
    zone_id: UUID
    timestamp: AwareDatetime
    event_type: EventType
    track_id: int = Field(ge=0)
    rule_id: str = Field(min_length=1, max_length=120)
    rule_version: int = Field(ge=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence_ref: str | None = Field(default=None, pattern=EVIDENCE_PATTERN)
    source: SourceType
    explanation: str = Field(min_length=1, max_length=1024)

    @field_validator("timestamp")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        return value.astimezone(timezone.utc)

    @field_validator("evidence_ref")
    @classmethod
    def validate_evidence_ref(cls, value: str | None, info: ValidationInfo) -> str | None:
        event_id = info.data.get("event_id")
        if value is not None and event_id is not None and value != f"{event_id}.jpg":
            raise ValueError("A referência de evidência deve corresponder ao event_id.")
        return value


def save_evidence(event: EventoVisao, image: ndarray, evidence_dir: Path = EVIDENCE_DIR) -> EventoVisao:
    try:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        ok, jpeg = cv2.imencode(".jpg", image)
        if not ok:
            raise OSError("Falha na codificação JPEG.")
        ref = f"{event.event_id}.jpg"
        with (evidence_dir / ref).open("xb") as evidence:
            evidence.write(jpeg.tobytes())
        event = event.model_copy(update={"evidence_ref": ref})
    except (OSError, cv2.error):
        logger.warning("Falha ao gravar evidência do evento %s.", event.event_id)
    return event


def append_event(event: EventoVisao, event_log: Path = EVENT_LOG) -> None:
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with _log_lock, event_log.open("a", encoding="utf-8") as log:
        log.write(event.model_dump_json() + "\n")


def save_event(event: EventoVisao, image: ndarray, evidence_dir: Path = EVIDENCE_DIR,
               event_log: Path = EVENT_LOG) -> EventoVisao:
    saved = save_evidence(event, image, evidence_dir)
    append_event(saved, event_log)
    return saved
