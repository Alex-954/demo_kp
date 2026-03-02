"""Models for dasha timelines and transit contacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DashaPeriod:
    level: str
    lord: str
    start_utc: datetime
    end_utc: datetime


@dataclass(frozen=True)
class TransitContact:
    transit_body: str
    natal_body: str
    angle: float
    orb: float
    timestamp_utc: datetime
