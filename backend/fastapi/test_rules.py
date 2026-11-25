from datetime import datetime, timedelta, timezone
from uuid import uuid4

import numpy as np
import pytest
from pydantic import ValidationError

from test_zones import zone
from vision.events import EventType, EventoVisao, SourceType, save_event
from vision.rules import Rules
from vision.state import Compliance, ItemState
from vision.tracker import TrackedPerson
from vision.zones import Presence, RuleType

START = datetime(2026, 11, 24, tzinfo=timezone.utc)
PERSON = TrackedPerson(1, (5, 5, 25, 27), 0.9)


def setup(rule_type=RuleType.EPI_OBRIGATORIO):
    area = zone([(0, 0), (1, 0), (0, 1)]).model_copy(update={"rule_type": rule_type})
    rules = Rules("CAM-A", uuid4(), SourceType.ARQUIVO, clock=lambda: START)

    def evaluate(offset, status=Compliance.NAO_CONFORME, inside=True, uncertain=False):
        item = ItemState(status, 0.86 if status == Compliance.NAO_CONFORME else None)
        return rules.evaluate([Presence(1, area, inside, uncertain)], [PERSON],
                              {1: {"CAPACETE": item}}, START + timedelta(seconds=offset))
    return evaluate


def test_deduplicacao_reabertura_e_jpeg(tmp_path):
    evaluate = setup()
    original, = evaluate(0)
    assert original.event_type == EventType.EPI_AUSENTE
    assert original.confidence == 0.86
    assert not evaluate(1)
    assert not evaluate(5, Compliance.CONFORME)
    assert not evaluate(34)
    reaberto, = evaluate(35)
    assert reaberto.event_id != original.event_id
    saved = save_event(reaberto, np.zeros((32, 32, 3), dtype=np.uint8),
                       tmp_path / "evidencias", tmp_path / "eventos_locais.jsonl")
    assert (tmp_path / "evidencias" / saved.evidence_ref).read_bytes().startswith(b"\xff\xd8")
    assert EventoVisao.model_validate_json((tmp_path / "eventos_locais.jsonl").read_bytes()) == saved


def test_indeterminado_aguarda_e_nao_e_ausencia():
    evaluate = setup()
    for offset in [0, 4, 5]:
        assert not evaluate(offset, Compliance.INDETERMINADO)
    event, = evaluate(6, Compliance.INDETERMINADO)
    assert event.event_type == EventType.EPI_INDETERMINADO
    assert event.confidence is None
    absent, = evaluate(7)
    assert absent.event_type == EventType.EPI_AUSENTE


def test_area_restrita_e_pes_incertos():
    evaluate = setup(RuleType.AREA_RESTRITA)
    assert not evaluate(0, uncertain=True)
    assert not evaluate(1, inside=False)
    event, = evaluate(2, Compliance.CONFORME)
    assert event.event_type == EventType.INTRUSAO
    assert not evaluate(3, uncertain=True)
    assert not evaluate(4)


@pytest.mark.parametrize(("field", "value"), [
    ("timestamp", "2026-11-24T00:00:00"),
    ("event_type", "OUTRO"),
    ("confidence", 1.5),
    ("rule_version", 0),
    ("track_id", -1),
    ("evidence_ref", "../algo.jpg"),
    ("evidence_ref", f"{uuid4()}.jpg"),
    ("review_status", "CONFIRMADO"),
])
def test_valida_evento(field, value):
    event, = setup()(0)
    with pytest.raises(ValidationError):
        EventoVisao.model_validate({**event.model_dump(), field: value})
