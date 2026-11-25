from collections.abc import Callable
from datetime import datetime, timezone
from statistics import mean
from uuid import UUID, uuid4

from .config import RuleConfig
from .events import EventType, EventoVisao, SourceType
from .state import Compliance, ItemState
from .tracker import TrackedPerson
from .zones import Presence, RuleType

EventKey = tuple[int, UUID, str, EventType]
ConditionKey = tuple[int, UUID, str, str, str]


class Rules:
    def __init__(self, camera_id: str, session_id: UUID, source: SourceType,
                 config: RuleConfig = RuleConfig(),
                 clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self.camera_id = camera_id
        self.session_id = session_id
        self.source = source
        self.config = config
        self.clock = clock
        self._active: set[EventKey] = set()
        self._closed: dict[EventKey, datetime] = {}
        self._since: dict[ConditionKey, datetime] = {}

    def evaluate(self, presence: list[Presence], people: list[TrackedPerson],
                 states: dict[int, dict[str, ItemState]], timestamp: datetime | None = None) -> list[EventoVisao]:
        now = timestamp if timestamp is not None else self.clock()
        cfg = self.config
        self._closed = {key: end for key, end in self._closed.items()
                        if (now - end).total_seconds() < cfg.cooldown_seconds}
        confidence = {person.track_id: person.confidence for person in people}
        conditions = {}
        continuous = set()
        uncertain = set()
        for observed in presence:
            if not observed.inside:
                continue
            zone = observed.zone
            identity = (observed.track_id, zone.zone_id, zone.rule_id)
            if observed.pes_incertos:
                uncertain.add(identity)
                continue
            candidates: dict[EventType, list[tuple[str, float, float | None]]] = {}
            if zone.rule_type == RuleType.AREA_RESTRITA:
                key = (*identity, "", EventType.INTRUSAO)
                continuous.add(key)
                seconds = (now - self._since.setdefault(key, now)).total_seconds()
                candidates[EventType.INTRUSAO] = [("presença em área restrita", seconds, confidence.get(observed.track_id))]
            else:
                for item in zone.required_ppe:
                    value = states.get(observed.track_id, {}).get(item)
                    if value is None or value.status == Compliance.CONFORME:
                        continue
                    key = (*identity, item, value.status)
                    continuous.add(key)
                    seconds = (now - self._since.setdefault(key, now)).total_seconds()
                    if value.status == Compliance.NAO_CONFORME:
                        event_type, description = EventType.EPI_AUSENTE, f"sem {item.lower()}"
                    elif seconds > cfg.indeterminate_seconds:
                        event_type, description = EventType.EPI_INDETERMINADO, f"{item.lower()} indeterminado"
                    else:
                        continue
                    candidates.setdefault(event_type, []).append((description, seconds, value.confidence))
            for event_type, facts in candidates.items():
                conditions[(*identity, event_type)] = (zone, facts)

        self._since = {key: start for key, start in self._since.items() if key in continuous}
        current = set(conditions) | {key for key in self._active if key[:3] in uncertain}
        for key in self._active - current:
            self._closed[key] = now
        events = []
        for key, (zone, facts) in conditions.items():
            if key in self._active or key in self._closed:
                continue
            track_id, _, _, event_type = key
            explanation = " e ".join(f"{item} por {duration:.1f} s".replace(".", ",")
                                     for item, duration, _ in facts)
            detected = [value for _, _, value in facts if value is not None]
            events.append(EventoVisao(
                event_id=uuid4(), camera_id=self.camera_id, session_id=self.session_id,
                zone_id=zone.zone_id, timestamp=now, event_type=event_type, track_id=track_id,
                rule_id=zone.rule_id, rule_version=zone.rule_version, source=self.source,
                confidence=mean(detected) if detected else None,
                explanation=f"Pessoa na zona '{zone.nome}': {explanation} (regra {zone.rule_id} v{zone.rule_version}).",
            ))
            self._active.add(key)
        self._active.intersection_update(current)
        return events
