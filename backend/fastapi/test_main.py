
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from main import app


client = TestClient(app)


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
    assert data["inference_available"] is False
    assert data["status"] == "NOT_READY"


# ============================================================
# 3. TESTE DA DOCUMENTAÇÃO OPENAPI
# ============================================================

def test_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["version"] == "0.2.0"

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
    assert data["status"] == "VALIDATED"
    assert data["inference_performed"] is False
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
    assert data["status"] == "VALIDATED"


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
