import logging
import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.getenv("VISION_MODELS_DIR", str(BASE_DIR / "models"))).resolve()
PERSON_MODEL = "yolo11n.pt"
PERSON_CONFIDENCE = 0.40
EPI_MODEL = "best_epi_grupo_yolo26s.pt"
EPI_CONFIDENCE = 0.40


def local_weight(name: str) -> Path:
    path = MODELS_DIR / name
    if path.is_file():
        return path
    legacy = BASE_DIR / name
    if name == PERSON_MODEL and legacy.is_file():
        logging.getLogger(__name__).warning("Usando yolo11n.pt no local antigo junto à API.")
        return legacy
    raise FileNotFoundError(f"Peso local não encontrado: {name}")

@dataclass(frozen=True)
class AssociationConfig:
    head_fraction: float = 0.35
    torso_top: float = 0.20
    torso_bottom: float = 0.65
    vest_min_overlap: float = 0.50
    conflict_gap: float = 0.10

@dataclass(frozen=True)
class StateConfig:
    window: int = 15
    agreement: float = 0.70
    min_observations: int = 8
    min_height: float = 0.10
    border: float = 0.01
    min_confidence: float = 0.40
    expire_frames: int = 30

@dataclass(frozen=True)
class ZoneConfig:
    enter_frames: int = 5
    exit_frames: int = 10
    feet_border: float = 0.01

EVIDENCE_DIR = Path(os.getenv("VISION_EVIDENCE_DIR", str(BASE_DIR / "evidencias"))).resolve()
EVENT_LOG = Path(os.getenv("VISION_EVENTS_FILE", str(BASE_DIR / "eventos_locais.jsonl"))).resolve()


@dataclass(frozen=True)
class RuleConfig:
    indeterminate_seconds: float = 5.0
    cooldown_seconds: float = 30.0

SPRING_BASE_URL = os.getenv("SPRING_BASE_URL", "http://127.0.0.1:8080")
ZONES_CACHE = Path(os.getenv("VISION_ZONES_CACHE", str(BASE_DIR / "zonas_cache"))).resolve()
EVENT_QUEUE = Path(os.getenv("VISION_EVENT_QUEUE", str(BASE_DIR / "eventos.sqlite3"))).resolve()

LIVE_RETRY_INITIAL = 1
LIVE_RETRY_MAX = 30
LIVE_STOP_TIMEOUT = 8
RTSP_TIMEOUT_MS = 3000

# Evita que o backend FFmpeg inclua a URL da câmera na saída nativa.
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"
os.environ["OPENCV_FFMPEG_DEBUG"] = "0"
