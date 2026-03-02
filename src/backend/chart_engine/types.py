"""Typed models for chart-engine outputs and KP table rows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChartRequest:
    """Input request for chart generation."""

    timestamp: datetime
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ChartPlanet:
    """A planet placement in a generated chart."""

    body: str
    longitude: float
    sign_index: int
    house_index: int


@dataclass(frozen=True)
class KPCuspDetail:
    """KP decomposition details for a single house cusp."""

    house_index: int
    cusp_longitude: float
    nakshatra_index: int
    star_lord: str
    sub_lord: str


@dataclass(frozen=True)
class ChartBundle:
    """Combined chart output with planets and KP cusp details."""

    timestamp_utc: datetime
    planets: tuple[ChartPlanet, ...]
    cusp_details: tuple[KPCuspDetail, ...]
