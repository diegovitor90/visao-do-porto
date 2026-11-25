from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

import main
from test_main import client, criar_imagem_teste
from vision import detector


@pytest.fixture
def epi(monkeypatch):
    fake = Mock()
    fake.carregar_modelo.cache_info.return_value = SimpleNamespace(currsize=0)
    fake.carregar_modelo_epi.cache_info.return_value = SimpleNamespace(currsize=1)
    monkeypatch.setattr(main, "_get_detector", lambda: fake)
    return fake


@pytest.mark.parametrize("classes", [[], ["helmet", "vest"]])
def test_analise_epi(epi, classes):
    epi.detectar_epi.return_value = [
        {"class_id": i, "class_name": name, "confidence": 0.9,
         "bbox": {"x1": 1, "y1": 2, "x2": 3, "y2": 4}}
        for i, name in enumerate(classes)
    ]
    response = client.post("/api/v1/vision/analyze/ppe",
                           files={"file": ("epi.png", criar_imagem_teste(), "image/png")})
    assert response.status_code == 200
    assert response.json()["model"] == "best_epi_grupo_yolo26s.pt"
    assert [item["class_name"] for item in response.json()["detections"]] == classes
    assert client.get("/api/v1/vision/status").json()["ppe_model_loaded"] is True


@pytest.mark.parametrize(("mime", "data", "status"), [
    ("text/plain", b"not png", 415), ("image/png", b"bad", 422),
    ("image/png", b"x" * 10, 413),
])
def test_validacao_epi(epi, monkeypatch, mime, data, status):
    monkeypatch.setattr(main, "MAX_FILE_SIZE", 9)
    response = client.post("/api/v1/vision/analyze/ppe", files={"file": ("a.png", data, mime)})
    assert response.status_code == status
    epi.detectar_epi.assert_not_called()


def test_peso_ausente(epi):
    epi.detectar_epi.side_effect = FileNotFoundError
    response = client.post("/api/v1/vision/analyze/ppe",
                           files={"file": ("epi.png", criar_imagem_teste(), "image/png")})
    assert response.status_code == 503


def test_nomes_sao_lidos_do_modelo(monkeypatch):
    model = Mock(names={7: "vest", 3: "helmet"})
    model.predict.return_value = [SimpleNamespace(boxes=[
        SimpleNamespace(cls=[7], conf=[0.81], xyxy=[Mock(**{"tolist.return_value": [1, 2, 3, 4]})])
    ])]
    monkeypatch.setattr(detector, "carregar_modelo_epi", lambda _: model)
    result = detector.detectar_epi(criar_imagem_teste())
    assert result[0]["class_name"] == "vest"
    assert isinstance(model.predict.call_args.args[0], Image.Image)
    assert model.predict.call_args.kwargs["device"] == "cpu"

def test_jpeg_truncado_e_invalido_antes_da_inferencia(epi):
    jpeg = criar_imagem_teste("JPEG")[:-100]
    response = client.post("/api/v1/vision/analyze/ppe", files={"file": ("truncado.jpg", jpeg, "image/jpeg")})
    assert response.status_code == 422
    epi.detectar_epi.assert_not_called()

def test_upload_independe_do_open_global_modificado(epi, monkeypatch):
    patched = Mock(side_effect=ModuleNotFoundError("Dependência opcional indisponível"))
    monkeypatch.setattr(Image, "open", patched)
    response = client.post("/api/v1/vision/analyze/ppe",
                           files={"file": ("corrompido.jpg", b"corrompido", "image/jpeg")})
    assert response.status_code == 422
    patched.assert_not_called()
    epi.detectar_epi.assert_not_called()
