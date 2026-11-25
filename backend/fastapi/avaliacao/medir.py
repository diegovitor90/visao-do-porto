import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import median


def read_csv(path: Path, clip: str) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [row for row in csv.DictReader(stream) if row["clip"] == clip]


def grade_states(labels: list[dict], observations: list[dict], fps: float) -> dict:
    expected = {}
    for label in labels:
        start, end = int(label["frame_inicio"]), int(label["frame_fim"])
        if start < 0 or end < start:
            raise ValueError("Intervalo inválido nos rótulos de estado.")
        for frame in range(start, end + 1):
            key = (int(label["track_id"]), label["item"], frame)
            if key in expected and expected[key] != label["estado_real"]:
                raise ValueError(f"Rótulos de estado contraditórios para {key}.")
            expected[key] = label["estado_real"]

    observed = {(int(row["track_id"]), row["item"], int(row["frame"])): row["estado"]
                for row in observations}
    tracks = defaultdict(lambda: {"rotulados": 0, "corretos": 0, "sem_observacao": 0})
    series = defaultdict(list)
    for (track, item, frame), state in observed.items():
        series[track, item].append((frame, state))

    for key, label in expected.items():
        track = tracks[key[0]]
        track["rotulados"] += 1
        track["corretos"] += observed.get(key) == label
        track["sem_observacao"] += key not in observed

    times = defaultdict(list)
    for (track, _), values in series.items():
        values.sort()
        times[track].extend([values[0][0], values[-1][0]])
        count = sum(a[1] != b[1] for a, b in zip(values, values[1:]))
        metrics = tracks[track]
        metrics["trocas"] = metrics.get("trocas", 0) + count

    for track, values in tracks.items():
        indexes = times[track]
        minutes = (max(indexes) - min(indexes)) / fps / 60 if indexes else 0
        values["trocas"] = values.get("trocas", 0)
        values["trocas_por_min"] = values["trocas"] / minutes if minutes > 0 else None
        values["acerto"] = values["corretos"] / values["rotulados"] if values["rotulados"] else None
    return dict(tracks)


def grade_events(labels: list[dict], events: list[dict], fps: float, frames: int) -> dict:
    expected = defaultdict(list)
    for row in labels:
        start, end = int(row["frame_inicio"]), int(row["frame_fim"])
        if start < 0 or end < start:
            raise ValueError("Intervalo inválido nos rótulos de eventos.")
        expected[row["track_id"], row["zone_id"], row["event_type"]].append((end, start))
    for intervals in expected.values():
        intervals.sort()

    delays = []
    for row in sorted(events, key=lambda row: int(row["frame"])):
        frame = int(row["frame"])
        intervals = expected[row["track_id"], row["zone_id"], row["event_type"]]
        for i, (end, start) in enumerate(intervals):
            if start <= frame <= end:
                delays.append((frame - start) / fps)
                intervals.pop(i)
                break
    tp = len(delays)
    false_positives = len(events) - tp
    return {
        "verdadeiros_positivos": tp,
        "falsos_positivos": false_positives,
        "falsos_negativos": len(labels) - tp,
        "precisao": tp / len(events) if events else None,
        "recall": tp / len(labels) if labels else None,
        "atraso_mediano_s": median(delays) if delays else None,
        "falsos_alarmes_por_hora": false_positives * fps * 3600 / frames if frames else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara uma execução offline com rótulos manuais.")
    parser.add_argument("--execucao", type=Path, required=True)
    parser.add_argument("--rotulos", type=Path, required=True)
    parser.add_argument("--rotulos-eventos", type=Path)
    args = parser.parse_args()
    folder = args.execucao
    execution = json.loads((folder / "execucao.json").read_text(encoding="utf-8"))
    clip = execution["clip"]
    fps = execution["fps_fonte"]
    labels = read_csv(args.rotulos, clip)
    if not labels:
        parser.error("Nenhum rótulo de estado corresponde ao clipe informado pela execução.")
    results = {"execucao": execution, "estados_por_track": grade_states(
        labels, read_csv(folder / "observacoes.csv", clip), fps)}
    if args.rotulos_eventos:
        results["eventos"] = grade_events(read_csv(args.rotulos_eventos, clip),
                                           read_csv(folder / "eventos.csv", clip), fps, execution["quadros"])
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
