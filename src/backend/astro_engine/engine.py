"""Astronomical engine facade for planetary and house calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .provider import (
    PySwissEphProvider,
    SwissEphBodyCatalog,
    SwissEphProvider,
    default_body_catalog,
)
from .time import normalize_to_utc
from .types import HouseCusps, PlanetPosition


@dataclass
class AstroEngine:
    """Domain interface exposing deterministic astronomy operations."""

    provider: SwissEphProvider = field(default_factory=PySwissEphProvider)
    catalog: SwissEphBodyCatalog = field(default_factory=default_body_catalog)

    def planet_position(self, body: str, timestamp: datetime) -> PlanetPosition:
        """Compute planet position in tropical coordinates at UTC timestamp."""

        timestamp_utc = normalize_to_utc(timestamp)
        body_id = self.catalog.by_name.get(body.lower())
        if body_id is None:
            known = ", ".join(sorted(self.catalog.by_name))
            raise ValueError(f"Unknown body '{body}'. Supported bodies: {known}")

        jd_ut = self.provider.julday(timestamp_utc)
        longitude, latitude, speed = self.provider.calc_ut(jd_ut, body_id)

        return PlanetPosition(
            body=body.lower(),
            longitude=longitude,
            latitude=latitude,
            speed_longitude=speed,
            julian_day_ut=jd_ut,
            timestamp_utc=timestamp_utc,
        )

    def placidus_house_cusps(self, timestamp: datetime, lat: float, lon: float) -> HouseCusps:
        """Compute Placidus house cusps and key angles (ASC/MC)."""

        timestamp_utc = normalize_to_utc(timestamp)
        jd_ut = self.provider.julday(timestamp_utc)
        cusps, ascmc = self.provider.houses_ex(jd_ut, lat, lon)

        return HouseCusps(
            cusps=cusps,
            ascendant=ascmc[0],
            midheaven=ascmc[1],
            julian_day_ut=jd_ut,
            timestamp_utc=timestamp_utc,
        )
