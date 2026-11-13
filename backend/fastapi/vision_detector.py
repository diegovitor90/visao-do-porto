
from functools import lru_cache
from io import BytesIO

from PIL import Image
from ultralytics import YOLO


# ============================================================
# CONFIGURAÇÕES DO DETECTOR
# ============================================================

MODEL_NAME = "yolo11n.pt"
CONFIDENCE_THRESHOLD = 0.40


# ============================================================
# CARREGAMENTO DO MODELO
# ============================================================

@lru_cache(maxsize=1)
def carregar_modelo():
    """
    Carrega o modelo YOLO apenas uma vez.
    """
    return YOLO(MODEL_NAME)


# ============================================================
# DETECÇÃO DE PESSOAS
# ============================================================

def detectar_pessoas(image_bytes: bytes):
    """
    Recebe uma imagem e retorna as pessoas detectadas.
    Não realiza identificação pessoal.
    """

    imagem = Image.open(BytesIO(image_bytes)).convert("RGB")

    modelo = carregar_modelo()

    resultados = modelo.predict(
        source=imagem,
        conf=CONFIDENCE_THRESHOLD,
        classes=[0],
        device="cpu",
        verbose=False
    )

    deteccoes = []

    for resultado in resultados:
        if resultado.boxes is None:
            continue

        for box in resultado.boxes:
            coordenadas = box.xyxy[0].tolist()
            confianca = float(box.conf[0])

            deteccoes.append({
                "class_id": 0,
                "class_name": "person",
                "confidence": round(confianca, 4),
                "bbox": {
                    "x1": round(coordenadas[0], 2),
                    "y1": round(coordenadas[1], 2),
                    "x2": round(coordenadas[2], 2),
                    "y2": round(coordenadas[3], 2)
                }
            })

    return deteccoes
