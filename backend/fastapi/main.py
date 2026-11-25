
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
from importlib import import_module
from importlib.util import find_spec
import re
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
# Ultralytics troca Image.open ao carregar o modelo.
from PIL.Image import open as open_pillow_image

if __package__:
    from .vision.config import EPI_MODEL, EVIDENCE_DIR
    from .vision.events import EVIDENCE_PATTERN
    from .vision.service import SourceRequest, SourceService
    from .vision.spring_client import EventPublisher, ZoneProvider
else:
    from vision.config import EPI_MODEL, EVIDENCE_DIR
    from vision.events import EVIDENCE_PATTERN
    from vision.service import SourceRequest, SourceService
    from vision.spring_client import EventPublisher, ZoneProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    with EventPublisher() as publisher:
        app.state.sources = SourceService(ZoneProvider(), publisher)
        try:
            yield
        finally:
            await run_in_threadpool(app.state.sources.close)


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
    version="0.3.0",
    lifespan=lifespan,
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
    if find_spec("ultralytics") is None:
        raise ImportError("Ultralytics indisponível.")
    module_name = f"{__package__}.vision.detector" if __package__ else "vision.detector"
    return import_module(module_name)


@app.get("/api/v1/vision/status", tags=["Vision"])
def vision_status(request: Request):
    sources = getattr(request.app.state, 'sources', None)
    active_sources = sources.list() if sources else []
    ppe_loaded = False
    try:
        detector = _get_detector()
        available = callable(detector.detectar_pessoas)
        loaded = detector.carregar_modelo.cache_info().currsize > 0
        if hasattr(detector, 'carregar_modelo_epi'):
            ppe_loaded = detector.carregar_modelo_epi.cache_info().currsize > 0
    except Exception:
        available = False
        loaded = False

    return {
        "service": "visao-do-porto-vision",
        "model": "yolo11n",
        "model_loaded": loaded,
        "ppe_model_loaded": ppe_loaded,
        "sources": active_sources,
        "fps": sum(source["fps"] for source in active_sources),
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
    return await _analyze(file, "detectar_pessoas", "yolo11n")


@app.post("/api/v1/vision/analyze/ppe", tags=["Vision"], response_model=ImageAnalysisResponse)
async def analyze_ppe(file: UploadFile = File(...)):
    return await _analyze(file, "detectar_epi", EPI_MODEL)


async def _validate_upload(file: UploadFile) -> tuple[bytes, int, int]:

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

    width, height = _inspect_image(content)
    return content, width, height


def _inspect_image(content: bytes) -> tuple[int, int]:
    try:
        with open_pillow_image(BytesIO(content)) as image:

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

            image_format = image.format
            image.verify()
        if image_format == "JPEG":
            with open_pillow_image(BytesIO(content)) as image:
                image.load()

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Arquivo de imagem inválido "
                "ou corrompido."
            )
        ) from exc

    except Image.DecompressionBombError as exc:
        raise HTTPException(status_code=413, detail="Imagem excede o limite de 20 megapixels.") from exc

    return width, height


async def _analyze(file: UploadFile, detect: str, model: str) -> ImageAnalysisResponse:
    content, width, height = await _validate_upload(file)
    try:
        detector = _get_detector()
        detections = await run_in_threadpool(getattr(detector, detect), content)
        response = ImageAnalysisResponse(
            filename=file.filename or "sem_nome",
            width=width,
            height=height,
            status="COMPLETED",
            inference_performed=True,
            model=model,
            detections=detections,
            message="Análise de imagem concluída."
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Serviço de inferência indisponível. Tente novamente mais tarde."
        ) from None

    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if request.method == "POST" and request.url.path.rstrip("/") == "/api/v1/sources":
        return JSONResponse({"detail": "Configuração da fonte inválida."}, status_code=422)
    return await request_validation_exception_handler(request, exc)


@app.post("/api/v1/sources", status_code=201, tags=["Vision"])
def start_source(config: SourceRequest, request: Request):
    return request.app.state.sources.start(config)


@app.delete("/api/v1/sources/{source_id}", status_code=204, tags=["Vision"])
def stop_source(source_id: UUID, request: Request):
    service = request.app.state.sources
    source = service.get(source_id)
    if source is None:
        raise HTTPException(404, "Fonte não encontrada.")
    if not service.stop(source):
        raise HTTPException(503, "A fonte ainda está encerrando.")
    return Response(status_code=204)


@app.get("/api/v1/sources/{source_id}/stream", tags=["Vision"])
async def source_stream(source_id: UUID, request: Request):
    source = request.app.state.sources.get(source_id)
    if source is None:
        raise HTTPException(404, "Fonte não encontrada.")
    return StreamingResponse(source.stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/v1/evidencias/{evidence_ref}", tags=["Vision"])
def evidence(evidence_ref: str):
    if re.fullmatch(EVIDENCE_PATTERN, evidence_ref):
        try:
            directory = EVIDENCE_DIR.resolve(strict=True)
            path = (directory / evidence_ref).resolve(strict=True)
            if path.is_relative_to(directory) and path.is_file():
                return FileResponse(path, media_type="image/jpeg")
        except (OSError, RuntimeError):
            pass
    raise HTTPException(404, "Evidência não encontrada.")
