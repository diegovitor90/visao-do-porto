import pytest

from vision.association import EpiDetection, Signal, SignalType, associar
from vision.tracker import TrackedPerson


P1 = TrackedPerson(1, (0, 0, 100, 100), 0.9)
P2 = TrackedPerson(2, (60, 0, 160, 100), 0.9)


def epi(name, box=(12, 2, 25, 22), confidence=0.8):
    return EpiDetection(name, box, confidence)


@pytest.mark.parametrize(("detections", "head", "vest"), [
    ([], Signal(), Signal()),
    ([epi("person")], Signal(), Signal()),
    ([epi("helmet")], Signal(SignalType.POSITIVO, 0.8), Signal()),
    ([epi("no_helmet")], Signal(SignalType.NEGATIVO, 0.8), Signal()),
    ([epi("helmet", (10, 30, 30, 50))], Signal(), Signal()),
    ([epi("helmet", (101, 3, 112, 20))], Signal(), Signal()),
    ([epi("vest", (20, 10, 60, 30))], Signal(), Signal(SignalType.POSITIVO, 0.8)),
    ([epi("no_vest", (20, 10, 60, 28))], Signal(), Signal()),
    ([epi("no_vest", (20, 20, 60, 50))], Signal(), Signal(SignalType.NEGATIVO, 0.8)),
    ([epi("vest", (20, 40, 20, 50))], Signal(), Signal()),
    ([epi("helmet"), epi("no_helmet", confidence=0.89)], Signal(), Signal()),
    ([epi("helmet"), epi("no_helmet", confidence=0.90)], Signal(SignalType.NEGATIVO, 0.90), Signal()),
    ([epi("helmet", confidence=0.95), epi("no_helmet")], Signal(SignalType.POSITIVO, 0.95), Signal()),
])
def test_sinais(detections, head, vest):
    assert associar([P1], detections) == {1: {"CAPACETE": head, "COLETE": vest}}


@pytest.mark.parametrize(("box", "winner"), [
    ((73, 2, 105, 30), 2),
    ((55, 2, 90, 30), 1),
    ((70, 2, 90, 30), 1),
])
def test_sobreposicao_determina_um_unico_dono(box, winner):
    result = associar([P2, P1], [epi("helmet", box)])
    assert result[winner]["CAPACETE"].type == SignalType.POSITIVO
    assert result[3 - winner]["CAPACETE"] == Signal()
