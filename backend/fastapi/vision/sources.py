from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from threading import Condition, Event, Lock, Thread
from time import perf_counter
from typing import Protocol

import cv2
from numpy import ndarray

from .config import RTSP_TIMEOUT_MS

_capture_open_lock = Lock()


@dataclass(frozen=True)
class Frame:
    frame_id: int
    timestamp: datetime
    imagem: ndarray
    capturado_em: float


class Source(Protocol):
    def read(self) -> Frame | None: ...
    def close(self) -> None: ...


class FileSource:
    def __init__(self, path: Path):
        if not path.is_file():
            raise FileNotFoundError(f"Vídeo local não encontrado: {path.name}")
        self._capture = cv2.VideoCapture(str(path))
        if not self._capture.isOpened():
            self.close()
            raise OSError("Não foi possível abrir o vídeo.")
        fps = self._capture.get(cv2.CAP_PROP_FPS)
        self.fps = fps if isfinite(fps) and fps > 0 else 30.0
        self._origin = datetime.now(timezone.utc)
        self._frame_id = 0

    def read(self) -> Frame | None:
        ok, image = self._capture.read()
        if not ok:
            return None
        frame = Frame(self._frame_id, self._origin + timedelta(seconds=self._frame_id / self.fps),
                      image, perf_counter())
        self._frame_id += 1
        return frame

    def close(self) -> None:
        self._capture.release()


class BufferedSource:
    def __init__(self, source: Source, sem_descarte: bool = False, pace_fps: float = 0):
        self.source = source
        self._wait_for_consumer = sem_descarte
        self._pace_fps = pace_fps if not sem_descarte else 0
        self._queue: deque[Frame] = deque(maxlen=1)
        self._condition = Condition()
        self._stop = Event()
        self._done = False
        self._error: Exception | None = None
        self.dropped = 0
        self._thread = Thread(target=self._read, name="visao-captura", daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *_):
        self.close()
        self._thread.join()

    def close(self) -> None:
        self._stop.set()
        with self._condition:
            self._condition.notify_all()

    def _read(self) -> None:
        started = perf_counter()
        index = 0
        try:
            while not self._stop.is_set():
                if self._pace_fps and self._stop.wait(max(0, started + index / self._pace_fps - perf_counter())):
                    break
                with self._condition:
                    if self._wait_for_consumer:
                        self._condition.wait_for(lambda: not self._queue or self._stop.is_set())
                if self._stop.is_set():
                    break
                frame = self.source.read()
                if frame is None:
                    break
                index += 1
                with self._condition:
                    self.dropped += len(self._queue)
                    self._queue.append(frame)
                    self._condition.notify_all()
        except Exception as exc:
            self._error = exc
        finally:
            try:
                self.source.close()
            finally:
                with self._condition:
                    self._done = True
                    self._condition.notify_all()

    def __iter__(self):
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._queue or self._done or self._stop.is_set())
                if self._stop.is_set() or not self._queue:
                    if self._error is not None:
                        raise self._error
                    return
                frame = self._queue.popleft()
                self._condition.notify_all()
            yield frame

class WebcamSource:
    def __init__(self, index: int):
        self._index = index
        self._capture = None
        self._frame_id = 0

    def _open(self):
        capture = cv2.VideoCapture(self._index)
        if not capture.isOpened():
            capture.release()
            raise OSError("Não foi possível abrir a webcam.")
        return capture

    def read(self) -> Frame | None:
        # O backend de captura do Windows pode manter estado associado à thread.
        if self._capture is None:
            self._capture = self._open()
        ok, image = self._capture.read()
        if not ok:
            return None
        frame = Frame(self._frame_id, datetime.now(timezone.utc), image, perf_counter())
        self._frame_id += 1
        return frame

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None


class RtspSource(WebcamSource):
    def __init__(self, url: str):
        super().__init__(0)
        self._url = url

    def _open(self):
        capture = cv2.VideoCapture()
        # O backend nativo pode imprimir URLs em mensagens de abertura.
        with _capture_open_lock:
            native_log = cv2.utils.logging
            previous_level = native_log.getLogLevel()
            native_log.setLogLevel(native_log.LOG_LEVEL_SILENT)
            try:
                opened = capture.open(self._url, cv2.CAP_FFMPEG, [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, RTSP_TIMEOUT_MS,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, RTSP_TIMEOUT_MS,
                ])
            except cv2.error:
                opened = False
            finally:
                native_log.setLogLevel(previous_level)
        if not opened:
            capture.release()
            raise OSError("Não foi possível abrir a fonte RTSP.")
        return capture
