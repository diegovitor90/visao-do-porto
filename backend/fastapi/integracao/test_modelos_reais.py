from importlib.util import find_spec
from pathlib import Path

import cv2
import pytest

from vision.detector import carregar_modelo_epi, detectar_epi
from vision.tracker import PersonTracker


@pytest.mark.slow
def test_yolo11n_bytetrack_e_yolo26s_em_cpu():
    ultralytics = Path(find_spec("ultralytics").origin).parent
    image = cv2.imread(str(ultralytics / "assets" / "bus.jpg"))
    assert image is not None
    image = cv2.resize(image, (360, 480))

    first, second = PersonTracker(), PersonTracker()
    before = {person.track_id for person in first.track(image)}
    assert before
    assert {person.track_id for person in second.track(image)} == before
    assert {person.track_id for person in first.track(image)} == before
    assert first.session_id != second.session_id

    epi = detectar_epi(image)
    classes = set(carregar_modelo_epi().names.values())
    assert classes == {"person", "helmet", "no_helmet", "vest", "no_vest"}
    assert epi and {detection["class_name"] for detection in epi} <= classes
