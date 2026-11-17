"""Demonstração local: imagem por padrão, ou --webcam [índice]. Não grava mídia."""

import argparse
from collections import deque
import os
from pathlib import Path
import sys
from time import perf_counter

BASE_DIR = Path(__file__).resolve().parent
WINDOW = "Visao do Porto | YOLO11n | Q para sair"


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--webcam", nargs="?", const=0, type=int, metavar="INDICE",
                        help="Usa webcam (índice padrão: 0), em vez da imagem.")
    parser.add_argument("--image", type=Path, default=BASE_DIR / "teste_pessoas.png",
                        help="Imagem local; padrão: teste_pessoas.png junto ao script.")
    args = parser.parse_args()
    if args.webcam is not None and args.webcam < 0:
        parser.error("O índice da webcam deve ser >= 0.")
    return args


def draw(cv2, frame, detections, milliseconds, fps, mode):
    import numpy as np

    annotated = frame.copy()
    height, width = frame.shape[:2]
    for detection in detections:
        box = detection["bbox"]
        x1, y1, x2, y2 = (int(round(box[key])) for key in ("x1", "y1", "x2", "y2"))
        x1, x2 = (max(0, min(width - 1, x)) for x in (x1, x2))
        y1, y2 = (max(0, min(height - 1, y)) for y in (y1, y2))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (70, 240, 120), 3)
        label = f'{detection["class_name"]}  {detection["confidence"]:.1%}'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        tx = min(x1, max(0, width - tw - 12))
        ty = min(height - 1, max(th + 12, y1))
        cv2.rectangle(annotated, (tx, ty - th - 12),
                      (min(width - 1, tx + tw + 12), ty), (70, 240, 120), -1)
        cv2.putText(annotated, label, (tx + 5, ty - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 25, 20), 2, cv2.LINE_AA)

    scale = min(960 / width, 600 / height)
    resized = cv2.resize(annotated, (max(1, round(width * scale)), max(1, round(height * scale))))
    canvas = np.full((760, 1000, 3), (27, 22, 16), dtype=np.uint8)
    rh, rw = resized.shape[:2]
    left = (1000 - rw) // 2
    canvas[120:120 + rh, left:left + rw] = resized
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "VISAO DO PORTO", (25, 37), font, 0.95, (245, 245, 245), 2, cv2.LINE_AA)
    cv2.putText(canvas, f"{mode} | YOLO11n | CPU | person | limiar 0.40",
                (25, 69), font, 0.55, (195, 200, 205), 1, cv2.LINE_AA)
    metrics = f"Pessoas: {len(detections)}   |   Inferencia: {milliseconds:.1f} ms"
    if fps is not None:
        metrics += f"   |   FPS real: {fps:.1f}"
    elif mode == "AO VIVO":
        metrics += "   |   FPS real: medindo..."
    cv2.putText(canvas, metrics, (25, 102), font, 0.63, (70, 240, 120), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Q: encerrar   |   Processamento local   |   Sem gravacao",
                (25, 748), font, 0.55, (195, 200, 205), 1, cv2.LINE_AA)
    return canvas


def main():
    args = arguments()
    try:
        import cv2
    except ImportError:
        print("OpenCV indisponível. É necessário opencv-python com suporte gráfico. "
              "Nenhuma instalação foi realizada; autorize antes de instalar.", file=sys.stderr)
        return 1

    capture = None
    previous_dir = Path.cwd()
    image_path = args.image.resolve()
    try:
        # O detector existente resolve MODEL_NAME relativamente ao diretório atual.
        os.chdir(BASE_DIR)
        if not (BASE_DIR / "yolo11n.pt").is_file():
            raise RuntimeError("Pesos yolo11n.pt não encontrados junto ao script. Nenhum download foi iniciado.")
        from vision_detector import carregar_modelo, detectar_pessoas

        if args.webcam is None:
            if not image_path.is_file():
                raise RuntimeError(f"Imagem não encontrada: {image_path.name}")
            content = image_path.read_bytes()
            import numpy as np
            frame = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                raise RuntimeError("Não foi possível decodificar a imagem.")
        else:
            capture = cv2.VideoCapture(args.webcam)
            if not capture.isOpened():
                raise RuntimeError("Webcam indisponível. Confira conexão, permissão de câmera, "
                                   "outros aplicativos ou tente --webcam 1.")

        print("Carregando YOLO11n local em CPU...", flush=True)
        load_start = perf_counter()
        carregar_modelo()
        print(f"Carregamento: {perf_counter() - load_start:.3f} s", flush=True)
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW, 1000, 760)
        completed_frames = deque(maxlen=31)
        if capture is None:
            start = perf_counter()
            detections = detectar_pessoas(content)
            milliseconds = (perf_counter() - start) * 1000
            canvas = draw(cv2, frame, detections, milliseconds, None, "IMAGEM")
            print(f"Imagem: {frame.shape[1]}x{frame.shape[0]} | Pessoas: {len(detections)} "
                  f"| Inferência: {milliseconds:.1f} ms", flush=True)
            print("Detecções:", detections, flush=True)
            cv2.imshow(WINDOW, canvas)
            print("Janela aberta. Clique nela e pressione Q para encerrar.", flush=True)
            while True:
                if cv2.waitKey(30) & 0xFF in (ord("q"), ord("Q")):
                    break
                if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                    break
        else:
            print("Webcam ativa; Q para encerrar. FPS mede quadros exibidos por tempo real, "
                  "incluindo captura, codificação, detector e desenho.", flush=True)
            while True:
                ok, frame = capture.read()
                if not ok or frame is None:
                    raise RuntimeError("Não foi possível ler a webcam. Confira a conexão e tente novamente.")
                ok, encoded = cv2.imencode(".png", frame)
                if not ok:
                    raise RuntimeError("Não foi possível preparar o quadro da webcam.")
                start = perf_counter()
                detections = detectar_pessoas(encoded.tobytes())
                milliseconds = (perf_counter() - start) * 1000
                fps = None
                if len(completed_frames) >= 2:
                    fps = (len(completed_frames) - 1) / (completed_frames[-1] - completed_frames[0])
                canvas = draw(cv2, frame, detections, milliseconds, fps, "AO VIVO")
                cv2.imshow(WINDOW, canvas)
                key = cv2.waitKey(1) & 0xFF
                completed_frames.append(perf_counter())
                if key in (ord("q"), ord("Q")) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                    break
        return 0
    except KeyboardInterrupt:
        print("Demonstração encerrada.")
        return 0
    except Exception as exc:
        print(f"Não foi possível executar a demonstração: {exc}", file=sys.stderr)
        print("Confira imagem/pesos, dependências da .venv e suporte gráfico do OpenCV. "
              "Nenhuma instalação foi realizada.", file=sys.stderr)
        return 1
    finally:
        if capture is not None:
            capture.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
        os.chdir(previous_dir)


if __name__ == "__main__":
    sys.exit(main())
