import os
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from threading import RLock

from PIL import Image

from .config import EPI_CONFIDENCE, EPI_MODEL, PERSON_CONFIDENCE, PERSON_MODEL, local_weight

_inference_lock = RLock()


def carregar_peso(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Peso local não encontrado: {path.name}")
    os.environ["YOLO_AUTOINSTALL"] = "false"
    from ultralytics import YOLO

    return YOLO(str(path.resolve()))


@lru_cache(maxsize=1)
def carregar_modelo():
    return carregar_peso(local_weight(PERSON_MODEL))


@lru_cache(maxsize=2)
def carregar_modelo_epi(path: Path | None = None):
    return carregar_peso(path if path is not None else local_weight(EPI_MODEL))


def detectar_pessoas(image_bytes: bytes) -> list[dict]:
    with Image.open(BytesIO(image_bytes)) as image, _inference_lock:
        model = carregar_modelo()
        return _detectar(model, image.convert("RGB"), PERSON_CONFIDENCE, classes=[0])


def detectar_epi(source, path: Path | None = None) -> list[dict]:
    with _inference_lock:
        model = carregar_modelo_epi(path)
        if isinstance(source, bytes):
            with Image.open(BytesIO(source)) as image:
                return _detectar(model, image.convert("RGB"), EPI_CONFIDENCE)
        return _detectar(model, source, EPI_CONFIDENCE)


def _detectar(model, image, confidence: float, **kwargs) -> list[dict]:
    detections = []
    for result in model.predict(image, conf=confidence, device="cpu", verbose=False, **kwargs):
        for box in result.boxes if result.boxes is not None else ():
            class_id = int(box.cls[0])
            detections.append({
                "class_id": class_id,
                "class_name": model.names[class_id],
                "confidence": round(float(box.conf[0]), 4),
                "bbox": dict(zip(("x1", "y1", "x2", "y2"),
                                 (round(value, 2) for value in box.xyxy[0].tolist()))),
            })
    return detections
