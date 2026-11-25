from collections import deque
from math import ceil
from statistics import median
from time import perf_counter


class Metrics:
    def __init__(self, window: int | None = None):
        self.started = perf_counter()
        self.total = 0
        self.latencies: deque[float] = deque(maxlen=window)

    def record(self, started: float) -> None:
        self.total += 1
        self.latencies.append((perf_counter() - started) * 1000)

    def snapshot(self, dropped: int = 0) -> dict:
        ordered = sorted(self.latencies)
        duration = perf_counter() - self.started
        return {
            "quadros": self.total,
            "fps": self.total / duration if duration > 0 else 0,
            "latencia_mediana_ms": median(ordered) if ordered else 0,
            "latencia_p95_ms": ordered[ceil(0.95 * len(ordered)) - 1] if ordered else 0,
            "descartados": dropped,
        }
