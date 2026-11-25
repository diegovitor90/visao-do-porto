import argparse
import hashlib
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica os pesos locais de EPI.")
    parser.add_argument("peso", type=Path)
    parser.add_argument("imagem", type=Path)
    args = parser.parse_args()
    for arquivo in (args.peso, args.imagem):
        if not arquivo.is_file():
            parser.error(f"Arquivo local não encontrado: {arquivo}")

    os.environ["YOLO_AUTOINSTALL"] = "false"
    from ultralytics import YOLO, __version__

    with args.peso.open("rb") as arquivo:
        print(f"SHA-256: {hashlib.file_digest(arquivo, 'sha256').hexdigest()}")
    modelo = YOLO(str(args.peso.resolve()))
    print(f"Ultralytics: {__version__}")
    print(f"Classes: {modelo.names}")
    resultado = modelo.predict(str(args.imagem.resolve()), device="cpu", verbose=False)[0]
    print(f"Detecções: {len(resultado.boxes)}")


if __name__ == "__main__":
    main()
