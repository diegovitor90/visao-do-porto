
from io import BytesIO
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock
import threading


def test_importacao_do_pacote_a_partir_da_raiz():
    result = subprocess.run(
        [sys.executable, "-c", "from backend.fastapi.main import app; print(app.version)"],
        cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0.3.0"

import pytest
import main

from fastapi.testclient import TestClient
from PIL import Image

from main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def detector_mock(monkeypatch):
    detector = SimpleNamespace(
        detectar_pessoas=Mock(return_value=[]),
        carregar_modelo=Mock()
    )
    detector.carregar_modelo.cache_info.return_value = SimpleNamespace(currsize=0)
    monkeypatch.setattr(main, "_get_detector", lambda: detector)
    yield detector
    detector.carregar_modelo.assert_not_called()


# ============================================================
# FUNÇÃO AUXILIAR — CRIAR IMAGEM PARA TESTES
# ============================================================

def criar_imagem_teste(formato="PNG", tamanho=(640, 480)):
    imagem = Image.new("RGB", tamanho, "white")

    buffer = BytesIO()
    imagem.save(buffer, format=formato)

    return buffer.getvalue()


# ============================================================
# 1. TESTE DE SAÚDE DA API
# ============================================================

def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "UP"
    assert data["service"] == "visao-do-porto-vision"
    assert data["framework"] == "FastAPI"
    assert "timestamp" in data


# ============================================================
# 2. TESTE DO STATUS DA VISÃO COMPUTACIONAL
# ============================================================

def test_vision_status():
    response = client.get("/api/v1/vision/status")

    assert response.status_code == 200

    data = response.json()

    assert data["model_loaded"] is False
    assert data["inference_available"] is True
    assert data["status"] == "READY"


# ============================================================
# 3. TESTE DA DOCUMENTAÇÃO OPENAPI
# ============================================================

def test_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["version"] == "0.3.0"

    assert "/api/health" in data["paths"]
    assert "/api/v1/vision/status" in data["paths"]
    assert "/api/v1/vision/analyze" in data["paths"]

    schemas = data["components"]["schemas"]
    assert "ImageAnalysisResponse" in schemas


# ============================================================
# 4. TESTE DE IMAGEM PNG VÁLIDA
# ============================================================

def test_analyze_imagem_valida():
    imagem = criar_imagem_teste()

    response = client.post(
        "/api/v1/vision/analyze",
        files={
            "file": ("teste.png", imagem, "image/png")
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "teste.png"
    assert data["width"] == 640
    assert data["height"] == 480
    assert data["status"] == "COMPLETED"
    assert data["inference_performed"] is True
    assert data["model"] == "yolo11n"
    assert data["detections"] == []


# ============================================================
# 5. TESTE DE IMAGEM JPEG VÁLIDA
# ============================================================

def test_analyze_imagem_jpeg():
    imagem = criar_imagem_teste(formato="JPEG")

    response = client.post(
        "/api/v1/vision/analyze",
        files={
            "file": ("teste.jpg", imagem, "image/jpeg")
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "teste.jpg"
    assert data["width"] == 640
    assert data["height"] == 480
    assert data["status"] == "COMPLETED"


# ============================================================
# 6. TESTE DE FORMATO NÃO SUPORTADO
# ============================================================

def test_analyze_formato_nao_suportado():
    response = client.post(
        "/api/v1/vision/analyze",
        files={
            "file": (
                "teste.txt",
                b"arquivo de texto",
                "text/plain"
            )
        }
    )

    assert response.status_code == 415


# ============================================================
# 7. TESTE DE IMAGEM CORROMPIDA
# ============================================================

def test_analyze_imagem_corrompida():
    response = client.post(
        "/api/v1/vision/analyze",
        files={
            "file": (
                "teste.png",
                b"imagem invalida",
                "image/png"
            )
        }
    )

    assert response.status_code == 422


# ============================================================
# 8. TESTE DE ARQUIVO MAIOR QUE 5 MB
# ============================================================

def test_analyze_arquivo_muito_grande():
    arquivo = b"0" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/v1/vision/analyze",
        files={
            "file": (
                "grande.png",
                arquivo,
                "image/png"
            )
        }
    )

    assert response.status_code == 413



def test_analyze_com_pessoa(detector_mock, monkeypatch):
    detection = {
        "class_id": 0, "class_name": "person", "confidence": 0.95,
        "bbox": {"x1": 10.0, "y1": 20.0, "x2": 100.0, "y2": 200.0}
    }
    detector_mock.detectar_pessoas.return_value = [detection]
    image = criar_imagem_teste()
    original_threadpool = main.run_in_threadpool
    calls = []

    async def tracked_threadpool(func, *args):
        event_loop_thread = threading.get_ident()

        def invoke():
            assert threading.get_ident() != event_loop_thread
            return func(*args)

        calls.append((func, args))
        return await original_threadpool(invoke)

    monkeypatch.setattr(main, "run_in_threadpool", tracked_threadpool)
    response = client.post('/api/v1/vision/analyze',
                           files={"file": ("pessoa.png", image, "image/png")})
    assert response.status_code == 200
    assert response.json()["detections"] == [detection]
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["inference_performed"] is True
    assert response.json()["model"] == "yolo11n"
    detector_mock.detectar_pessoas.assert_called_once_with(image)
    assert calls == [(detector_mock.detectar_pessoas, (image,))]


def test_analyze_falha_inferencia(detector_mock):
    detector_mock.detectar_pessoas.side_effect = RuntimeError("segredo /pesos/modelo.pt")
    response = client.post('/api/v1/vision/analyze', files={
        "file": ("teste.png", criar_imagem_teste(), "image/png")})
    assert response.status_code == 503
    assert response.json() == {"detail": "Serviço de inferência indisponível. Tente novamente mais tarde."}


def test_detector_indisponivel(monkeypatch):
    def unavailable():
        raise ImportError("dependência interna")

    monkeypatch.setattr(main, "_get_detector", unavailable)
    status = client.get('/api/v1/vision/status').json()
    assert status["status"] == "NOT_READY"
    assert status["inference_available"] is False
    assert status["model_loaded"] is False
    response = client.post('/api/v1/vision/analyze', files={
        "file": ("teste.png", criar_imagem_teste(), "image/png")})
    assert response.status_code == 503
    assert "dependência interna" not in response.text


def test_status_modelo_carregado(detector_mock):
    detector_mock.carregar_modelo.cache_info.return_value = SimpleNamespace(currsize=1)
    data = client.get('/api/v1/vision/status').json()
    assert data["model_loaded"] is True
    assert data["inference_available"] is True


@pytest.mark.parametrize("content,mime,expected", [
    (b"invalid", "image/png", 422),
    (b"invalid", "text/plain", 415),
    (b"0" * (5 * 1024 * 1024 + 1), "image/png", 413),
])
def test_invalidacao_impede_inferencia(content, mime, expected, detector_mock):
    response = client.post('/api/v1/vision/analyze',
                           files={"file": ("teste.png", content, mime)})
    assert response.status_code == expected
    detector_mock.detectar_pessoas.assert_not_called()


def test_analyze_mais_de_20_mp(detector_mock):
    image = criar_imagem_teste(tamanho=(5000, 4001))
    response = client.post('/api/v1/vision/analyze',
                           files={"file": ("grande.png", image, "image/png")})
    assert response.status_code == 413
    detector_mock.detectar_pessoas.assert_not_called()


def test_conteudo_formato_nao_suportado(detector_mock):
    image = criar_imagem_teste(formato="GIF")
    response = client.post('/api/v1/vision/analyze',
                           files={"file": ("teste.png", image, "image/png")})
    assert response.status_code == 415
    detector_mock.detectar_pessoas.assert_not_called()
