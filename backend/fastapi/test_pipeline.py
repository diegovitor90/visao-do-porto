from unittest.mock import Mock


from test_sources import video
from vision.pipeline import COLORS, Pipeline
from vision.sources import BufferedSource, FileSource
from vision.state import Compliance
from vision.tracker import TrackedPerson


def test_pipeline_com_video_e_detectores_simulados(video):
    person = TrackedPerson(1, (8, 5, 40, 43), 0.9)
    tracker = Mock()
    tracker.track.return_value = [person]
    detect_epi = Mock(return_value=[
        {"class_name": "no_helmet", "confidence": 0.9, "bbox": dict(x1=10, y1=7, x2=21, y2=17)},
    ])
    pipeline = Pipeline(tracker, detect_epi)
    with BufferedSource(FileSource(video), sem_descarte=True) as frames:
        results = [pipeline.process(frame) for frame in frames]
    assert len(results) == tracker.track.call_count == detect_epi.call_count == 24
    assert detect_epi.call_args.args[0] is tracker.track.call_args.args[0]
    assert results[0].states[1]["CAPACETE"].status == Compliance.INDETERMINADO
    last = results[-1]
    assert last.states[1]["CAPACETE"].status == Compliance.NAO_CONFORME
    assert tuple(last.image[30, 8]) == COLORS[Compliance.NAO_CONFORME]
    assert last.states[1]["COLETE"].status == Compliance.INDETERMINADO
