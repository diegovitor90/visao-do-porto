import argparse
import csv
import json
import platform
import re
from contextlib import ExitStack
from dataclasses import asdict
from functools import partial
from importlib.metadata import version
from pathlib import Path

import cv2

from .config import AssociationConfig, EPI_CONFIDENCE, EPI_MODEL, PERSON_MODEL, RuleConfig, StateConfig, ZoneConfig
from .detector import detectar_epi
from .events import CAMERA_PATTERN, save_event
from .metrics import Metrics
from .pipeline import Pipeline
from .sources import BufferedSource, FileSource
from .spring_client import EventPublisher, ZoneProvider
from .tracker import PersonTracker
from .zones import RuleType, load_zones


def main() -> None:
    parser = argparse.ArgumentParser(description="Processa um vídeo local.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--sem-descarte", action="store_true")
    parser.add_argument("--track", action="store_true")
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--epi", type=Path)
    zone_source = parser.add_mutually_exclusive_group()
    zone_source.add_argument("--zonas", type=Path)
    zone_source.add_argument("--spring", action="store_true")
    parser.add_argument("--camera", default="CAM-LAB-01")
    parser.add_argument("--avaliacao", type=Path, help="Diretório para CSVs e métricas da execução offline.")
    args = parser.parse_args()
    if not re.fullmatch(CAMERA_PATTERN, args.camera):
        parser.error("Identificador de câmera inválido.")
    if args.saida and args.saida.resolve() == args.source.resolve():
        parser.error("A saída deve ser diferente do vídeo de origem.")
    if args.epi and not args.epi.is_file():
        parser.error("O peso de EPI deve existir localmente.")
    if args.avaliacao and not args.sem_descarte:
        parser.error("Use --sem-descarte para avaliações offline.")
    if args.epi:
        args.epi = args.epi.resolve()

    zones = ZoneProvider().get(args.camera) if args.spring else load_zones(args.zonas) if args.zonas else []
    use_epi = args.epi or any(zone.ativa and zone.rule_type == RuleType.EPI_OBRIGATORIO for zone in zones)
    tracker = PersonTracker() if args.track or args.epi or args.zonas or args.spring else None
    clip = args.source.name
    size = None
    writer = None
    metrics = Metrics()
    try:
        with ExitStack() as resources:
            publisher = resources.enter_context(EventPublisher()) if args.spring else None
            record = publisher.record if publisher else save_event
            detect = partial(detectar_epi, path=args.epi) if use_epi else None
            pipeline = Pipeline(tracker, detect, zones, args.camera, record_event=record) if tracker else None

            if args.avaliacao:
                args.avaliacao.mkdir(parents=True, exist_ok=True)
                files = args.avaliacao
                observations = csv.writer(resources.enter_context(
                    (files / "observacoes.csv").open("w", encoding="utf-8", newline="")))
                events = csv.writer(resources.enter_context(
                    (files / "eventos.csv").open("w", encoding="utf-8", newline="")))
                observations.writerow(("clip", "frame", "track_id", "item", "estado"))
                events.writerow(("clip", "frame", "track_id", "zone_id", "event_type"))

            source = FileSource(args.source)
            frames = resources.enter_context(BufferedSource(source, args.sem_descarte, source.fps))
            for frame in frames:
                result = pipeline.process(frame) if pipeline else None
                image = result.image if result else frame.imagem
                size = image.shape[1::-1]
                if args.avaliacao and result:
                    for track_id, states in result.states.items():
                        observations.writerows((clip, frame.frame_id, track_id, name, item.status)
                                               for name, item in states.items())
                    events.writerows((clip, frame.frame_id, event.track_id, event.zone_id, event.event_type)
                                     for event in result.events)
                if args.saida:
                    if writer is None:
                        writer = cv2.VideoWriter(str(args.saida), cv2.VideoWriter_fourcc(*"mp4v"), source.fps, size)
                        if not writer.isOpened():
                            raise OSError("Não foi possível criar o vídeo anotado.")
                    writer.write(image)
                metrics.record(frame.capturado_em)
            result = metrics.snapshot(frames.dropped)
    finally:
        if writer is not None:
            writer.release()
    if tracker:
        result["session_id"] = str(tracker.session_id)
    if args.avaliacao:
        execution = {
            **result, "clip": clip, "fps_fonte": source.fps, "resolucao": size,
            "sistema": platform.platform(), "processador": platform.processor(), "device": "cpu",
            "python": platform.python_version(),
            "versoes": {name: version(name) for name in ("ultralytics", "torch", "opencv-python", "lap")},
            "modelo_pessoa": PERSON_MODEL if tracker else None,
            "modelo_epi": (args.epi.name if args.epi else EPI_MODEL) if use_epi else None,
            "config": {"associacao": asdict(AssociationConfig()), "estado": asdict(StateConfig()),
                       "zonas": asdict(ZoneConfig()), "regras": asdict(RuleConfig()),
                       "confianca_epi": EPI_CONFIDENCE, "sem_descarte": True},
        }
        (args.avaliacao / "execucao.json").write_text(json.dumps(execution, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
