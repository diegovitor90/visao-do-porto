import argparse
import json
import time
from collections.abc import Callable
from uuid import UUID

import httpx


def measure(poll: Callable[[], dict | None], duration: float, interval: float,
            clock=time.monotonic, sleeper=time.sleep) -> dict:
    start = clock()
    previous = None
    last_active = None
    offline_since = None
    recoveries = []
    while (now := clock()) - start < duration:
        source = poll()
        session = source.get("session_id") if source and source["status"] == "ATIVA" else None
        if session is not None:
            if previous is not None and previous != session:
                beginning = offline_since if offline_since is not None else last_active
                recoveries.append({"sessao_anterior": previous, "nova_sessao": session,
                                   "intervalo_estimado_s": now - beginning})
            previous, last_active, offline_since = session, now, None
        elif previous is not None and offline_since is None:
            offline_since = now
        sleeper(interval)
    return {
        "reconexoes": recoveries,
        "intervalo_amostragem_s": interval,
        "queda_em_andamento": offline_since is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mede a queda e a reconexão de uma fonte ativa.")
    parser.add_argument("--fonte", type=UUID, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--duracao", type=float, default=60)
    parser.add_argument("--intervalo", type=float, default=0.25)
    args = parser.parse_args()
    if not (0 < args.duracao < float("inf") and 0 < args.intervalo <= args.duracao):
        parser.error("Informe duração e intervalo positivos e finitos.")

    with httpx.Client(base_url=args.url, timeout=2, trust_env=False) as client:
        def poll():
            try:
                response = client.get("/api/v1/vision/status")
                response.raise_for_status()
                return next((source for source in response.json()["sources"]
                             if source["id"] == str(args.fonte)), None)
            except (httpx.HTTPError, ValueError, KeyError):
                return None

        print(json.dumps(measure(poll, args.duracao, args.intervalo), indent=2))


if __name__ == "__main__":
    main()
