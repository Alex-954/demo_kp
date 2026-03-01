"""Typed data models for astronomical calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlanetPosition:
    """Planet position at a specific UTC timestamp."""

    body: str
    longitude: float
    latitude: float
    speed_longitude: float
    julian_day_ut: float
    timestamp_utc: datetime


@dataclass(frozen=True)
class HouseCusps:
    """Placidus house cusps and key angles for a UTC timestamp and location."""

    cusps: tuple[float, ...]
    ascendant: float
    midheaven: float
    julian_day_ut: float
    timestamp_utc: datetime
