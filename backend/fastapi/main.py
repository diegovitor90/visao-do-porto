
from datetime import datetime, timezone
from io import BytesIO
from importlib import import_module

from fastapi import FastAPI, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError


# ============================================================
# CONFIGURAÇÕES
# ============================================================

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_PIXELS = 20_000_000    # 20 megapixels


# ============================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================

app = FastAPI(
    title="Visão do Porto — Vision API",
    description="API de visão computacional do projeto Visão do Porto",
    version="0.3.0"
)


# ============================================================
# MODELOS PYDANTIC — CONTRATOS DA API
# ============================================================

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class ImageAnalysisResponse(BaseModel):
    filename: str
    width: int
    height: int
    status: str
    inference_performed: bool
    model: str
    detections: list[Detection]
    message: str


# ============================================================
# 1. SAÚDE DA API
# ============================================================

@app.get("/api/health", tags=["Health"])
def health():
    return {
        "status": "UP",
        "service": "visao-do-porto-vision",
        "framework": "FastAPI",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============================================================
# 2. STATUS DA VISÃO COMPUTACIONAL
# ============================================================

def _get_detector():
    # Importação tardia: importar a API não importa YOLO nem carrega pesos.
    module_name = f"{__package__}.vision_detector" if __package__ else "vision_detector"
    return import_module(module_name)


@app.get("/api/v1/vision/status", tags=["Vision"])
def vision_status():
    try:
        detector = _get_detector()
        available = callable(detector.detectar_pessoas)
        loaded = detector.carregar_modelo.cache_info().currsize > 0
    except Exception:
        available = False
        loaded = False

    return {
        "service": "visao-do-porto-vision",
        "model": "yolo11n",
        "model_loaded": loaded,
        "inference_available": available,
        "status": "READY" if available else "NOT_READY",
        "message": (
            "Detector disponível. Pesos carregados sob demanda."
            if available else "Detector indisponível."
        )
    }


# ============================================================
# 3. RECEBIMENTO E VALIDAÇÃO DE IMAGENS
# ============================================================

@app.post(
    "/api/v1/vision/analyze",
    tags=["Vision"],
    response_model=ImageAnalysisResponse
)
async def analyze_image(file: UploadFile = File(...)):

    # 3.1 — Validar formato declarado
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=415,
            detail=(
                "Formato não suportado. "
                "Envie JPEG ou PNG."
            )
        )

    # 3.2 — Ler arquivo respeitando o limite de 5 MB
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Imagem excede o limite de 5 MB."
        )

    # 3.3 — Validar conteúdo e dimensões
    try:
        with Image.open(BytesIO(content)) as image:

            if image.format not in {"JPEG", "PNG"}:
                raise HTTPException(
                    status_code=415,
                    detail=(
                        "O conteúdo não corresponde "
                        "a JPEG ou PNG."
                    )
                )

            width, height = image.size

            if width * height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        "Imagem excede o limite "
                        "de 20 megapixels."
                    )
                )

            # Verificar integridade da imagem
            image.verify()

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Arquivo de imagem inválido "
                "ou corrompido."
            )
        ) from exc

    # 3.4 — Executar inferência fora do event loop, após validar a imagem.
    try:
        detector = _get_detector()
        detections = await run_in_threadpool(detector.detectar_pessoas, content)
        response = ImageAnalysisResponse(
            filename=file.filename or "sem_nome",
            width=width,
            height=height,
            status="COMPLETED",
            inference_performed=True,
            model="yolo11n",
            detections=detections,
            message="Análise de imagem concluída."
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Serviço de inferência indisponível. Tente novamente mais tarde."
        ) from None

    return response
