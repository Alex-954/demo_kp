"""Vimshottari dasha timeline utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .types import DashaPeriod

VIMSHOTTARI_ORDER = ("ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury")
VIMSHOTTARI_YEARS = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}


@dataclass(frozen=True)
class DashaEngine:
    """Builds deterministic dasha periods for timeline displays."""

    def maha_dasha_schedule(self, start_utc: datetime, years: int = 120) -> tuple[DashaPeriod, ...]:
        cursor = start_utc
        periods: list[DashaPeriod] = []
        elapsed_years = 0
        while elapsed_years < years:
            for lord in VIMSHOTTARI_ORDER:
                duration_years = VIMSHOTTARI_YEARS[lord]
                duration_days = int(duration_years * 365.2425)
                end = cursor + timedelta(days=duration_days)
                periods.append(DashaPeriod(level="maha", lord=lord, start_utc=cursor, end_utc=end))
                cursor = end
                elapsed_years += duration_years
                if elapsed_years >= years:
                    break
        return tuple(periods)
