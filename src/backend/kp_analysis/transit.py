"""Transit contact calculation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.backend.chart_engine import ChartBundle

from .types import TransitContact


@dataclass(frozen=True)
class TransitAnalyzer:
    """Computes angular contacts between transit and natal charts."""

    default_aspects: tuple[float, ...] = (0.0, 60.0, 90.0, 120.0, 180.0)

    def compare(
        self,
        natal: ChartBundle,
        transit: ChartBundle,
        max_orb: float = 2.0,
    ) -> tuple[TransitContact, ...]:
        natal_by_body = {p.body: p for p in natal.planets}
        contacts: list[TransitContact] = []

        for transit_planet in transit.planets:
            natal_planet = natal_by_body.get(transit_planet.body)
            if natal_planet is None:
                continue
            angle = abs((transit_planet.longitude - natal_planet.longitude) % 360.0)
            angle = min(angle, 360.0 - angle)
            nearest = min(self.default_aspects, key=lambda aspect: abs(aspect - angle))
            orb = abs(nearest - angle)
            if orb <= max_orb:
                contacts.append(
                    TransitContact(
                        transit_body=transit_planet.body,
                        natal_body=natal_planet.body,
                        angle=nearest,
                        orb=orb,
                        timestamp_utc=transit.timestamp_utc,
                    )
                )
        return tuple(contacts)
