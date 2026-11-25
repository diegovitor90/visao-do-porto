from datetime import datetime, timedelta, timezone

import pytest

from vision.association import Signal, SignalType
from vision.state import Compliance, TemporalState
from vision.tracker import TrackedPerson

START = datetime(2026, 11, 24, tzinfo=timezone.utc)
PERSON = TrackedPerson(1, (10, 10, 80, 90), 0.9)
POS = Signal(SignalType.POSITIVO, 0.9)
NEG = Signal(SignalType.NEGATIVO, 0.9)


def step(state, i, signal, person=PERSON):
    return state.update(i, START + timedelta(seconds=i), (100, 100), [person],
                        {1: {"CAPACETE": signal, "COLETE": Signal()}})[1]["CAPACETE"]


@pytest.mark.parametrize(("sequence", "expected"), [
    ([POS] * 7, Compliance.INDETERMINADO),
    ([POS] * 8, Compliance.CONFORME),
    ([NEG] * 8, Compliance.NAO_CONFORME),
    ([Signal()] * 15, Compliance.INDETERMINADO),
    ([POS] * 10 + [NEG] * 5, Compliance.INDETERMINADO),
    ([NEG] * 11 + [POS] * 4, Compliance.NAO_CONFORME),
    ([Signal(SignalType.NEGATIVO, 0.39)] * 15, Compliance.INDETERMINADO),
])
def test_janela(sequence, expected):
    state = TemporalState()
    for i, signal in enumerate(sequence):
        result = step(state, i, signal)
    assert result.status == expected


@pytest.mark.parametrize("box", [(10, 20, 20, 29), (0, 10, 80, 90), (10, 10, 80, 100)])
def test_qualidade_invalida(box):
    state = TemporalState()
    for i in range(15):
        result = step(state, i, POS, TrackedPerson(1, box, 0.9))
    assert result.status == Compliance.INDETERMINADO


def test_trocas_e_expiracao():
    state = TemporalState()
    for i, signal in enumerate([POS] * 15 + [NEG] * 15):
        result = step(state, i, signal)
    assert result.status == Compliance.NAO_CONFORME
    assert state.oscillations(1, START + timedelta(minutes=1)) == (3, 3.0)
    state.update(60, START + timedelta(minutes=1), (100, 100), [], {})
    with pytest.raises(KeyError):
        state.oscillations(1, START + timedelta(minutes=1))
    assert step(state, 61, NEG).status == Compliance.INDETERMINADO


def test_quadros_processados_sem_track_expiram_evidencia_antiga():
    state = TemporalState()
    for i in range(8):
        result = step(state, i, POS)
    assert result.status == Compliance.CONFORME
    for i in range(8, 14):
        state.update(i, START + timedelta(seconds=i), (100, 100), [], {})
    assert step(state, 14, POS).status == Compliance.INDETERMINADO
