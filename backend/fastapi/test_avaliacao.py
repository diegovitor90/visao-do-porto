import pytest

from avaliacao.medir import grade_events, grade_states
from avaliacao.reconexao import measure


def test_acerto_por_track_e_oscilacao():
    label = {"track_id": "1", "item": "CAPACETE", "estado_real": "CONFORME",
             "frame_inicio": "0", "frame_fim": "2"}
    observations = [
        {"track_id": "1", "item": "CAPACETE", "estado": status, "frame": str(frame)}
        for frame, status in [(0, "CONFORME"), (2, "NAO_CONFORME")]
    ]
    result = grade_states([label], observations, 2)[1]
    assert result == {"rotulados": 3, "corretos": 1, "acerto": 1 / 3,
                      "sem_observacao": 1, "trocas": 1, "trocas_por_min": 60}
    with pytest.raises(ValueError):
        grade_states([label, {**label, "estado_real": "NAO_CONFORME"}], observations, 2)


def test_metricas_eventos_com_pareamento_unico():
    identity = {"track_id": "1", "zone_id": "zona", "event_type": "INTRUSAO"}
    labels = [{**identity, "frame_inicio": "1", "frame_fim": "4"},
              {**identity, "frame_inicio": "8", "frame_fim": "10"}]
    events = [{**identity, "frame": "2"}, {**identity, "frame": "3"}]
    assert grade_events(labels, events, 2, 20) == {
        "verdadeiros_positivos": 1, "falsos_positivos": 1, "falsos_negativos": 1,
        "precisao": 0.5, "recall": 0.5, "atraso_mediano_s": 0.5, "falsos_alarmes_por_hora": 360,
    }


def test_queda_e_reconexao_medidas():
    states = iter([
        {"status": "ATIVA", "session_id": "1"}, {"status": "RECONECTANDO", "session_id": "1"},
        None, {"status": "ATIVA", "session_id": "2"}, {"status": "ATIVA", "session_id": "2"},
    ])
    now = [0]
    result = measure(lambda: next(states), 5, 1, lambda: now[0],
                     lambda seconds: now.__setitem__(0, now[0] + seconds))
    assert result["reconexoes"] == [
        {"sessao_anterior": "1", "nova_sessao": "2", "intervalo_estimado_s": 2},
    ]
    assert not result["queda_em_andamento"]
