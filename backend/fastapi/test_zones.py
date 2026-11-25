from uuid import uuid4

import numpy as np
import pytest

from vision.tracker import TrackedPerson
from vision.zones import ZONE_LIST, Zone, ZonePresence, load_zones


def zone(polygon):
    return Zone(zone_id=uuid4(), nome="Teste", polygon=polygon, required_ppe=["CAPACETE"],
                rule_type="EPI_OBRIGATORIO", rule_id="R", rule_version=1, ativa=True)


def step(presence, point, size=(640, 480)):
    width, height = size
    x, y = point[0] * width, point[1] * height
    image = np.zeros((height, width, 3), dtype=np.uint8)
    return presence.update([TrackedPerson(1, (x - 10, y - 40, x + 10, y), 0.9)], image)[0]


@pytest.mark.parametrize("size", [(640, 480), (1920, 1080)])
def test_poligono_concavo_presenca_pelos_pes(size):
    presence = ZonePresence([zone([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.5, 0.5), (0.2, 0.8)])])
    for _ in range(5):
        assert not step(presence, (0.5, 0.7), size).inside
    for _ in range(4):
        assert not step(presence, (0.5, 0.3), size).inside
    assert step(presence, (0.5, 0.3), size).inside


def test_histerese_e_pes_incertos():
    presence = ZonePresence([zone([(0.2, 0.2), (0.8, 0.2), (0.8, 1), (0.2, 1)])])
    for _ in range(5):
        value = step(presence, (0.5, 0.9))
    assert value.inside
    for i in range(12):
        assert step(presence, (0.199 if i % 2 else 0.201, 0.9)).inside
    assert step(presence, (0.5, 0.999)).pes_incertos
    for _ in range(9):
        assert step(presence, (0.1, 0.9)).inside
    assert not step(presence, (0.1, 0.9)).inside


@pytest.mark.parametrize("polygon", [
    [(0, 0), (1, 1), (0, 1), (1, 0), (1, 0.2)],
    [(0, 0), (1, 0), (0.5, 0), (0, 1)],
    [(0, 0), (2, 0), (0, 1)],
])
def test_poligonos_invalidos(polygon):
    with pytest.raises(ValueError):
        zone(polygon)


def test_ausencia_breve_preserva_presenca_sem_reabrir_condicao():
    area = zone([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)])
    presence = ZonePresence([area])
    for _ in range(5):
        value = step(presence, (0.5, 0.5))
    assert value.inside
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    for _ in range(9):
        value, = presence.update([], image)
        assert value.inside and value.pes_incertos
    assert not presence.update([], image)
    assert not step(presence, (0.5, 0.5)).inside


def test_le_zonas_em_utf8_com_bom_do_powershell(tmp_path):
    area = zone([(0, 0), (1, 0), (0, 1)])
    path = tmp_path / "área de teste.json"
    path.write_text(ZONE_LIST.dump_json([area]).decode(), encoding="utf-8-sig")
    assert load_zones(path) == [area]


def test_zona_ativa_repetida_nao_acelera_confirmacao():
    area = zone([(0, 0), (1, 0), (0, 1)])
    with pytest.raises(ValueError, match="repetido"):
        ZonePresence([area, area])
