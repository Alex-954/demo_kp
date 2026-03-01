"""Swiss Ephemeris provider boundary and implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class SwissEphProvider(Protocol):
    """Abstraction boundary for Swiss Ephemeris-compatible providers."""

    def julday(self, dt_utc: datetime) -> float: ...

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]: ...

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]: ...


@dataclass(frozen=True)
class SwissEphBodyCatalog:
    """Supported body identifiers mapped to Swiss Ephemeris IDs."""

    by_name: dict[str, int]


class PySwissEphProvider:
    """Runtime adapter around `swisseph` package."""

    def __init__(self) -> None:
        try:
            import swisseph as swe
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "swisseph is not installed. Install pyswisseph to enable astronomical integration."
            ) from exc
        self._swe = swe

    def julday(self, dt_utc: datetime) -> float:
        return self._swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600 + dt_utc.microsecond / 3_600_000_000,
            self._swe.GREG_CAL,
        )

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]:
        values, _flags = self._swe.calc_ut(jd_ut, body_id)
        return values[0], values[1], values[3]

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
        cusps, ascmc = self._swe.houses_ex(jd_ut, lat, lon, b"P")
        return tuple(cusps), tuple(ascmc)


def default_body_catalog() -> SwissEphBodyCatalog:
    """Default catalog aligned with Swiss Ephemeris planetary constants."""

    return SwissEphBodyCatalog(
        by_name={
            "sun": 0,
            "moon": 1,
            "mars": 4,
            "mercury": 2,
            "jupiter": 5,
            "venus": 3,
            "saturn": 6,
            "rahu": 10,
            "ketu": 11,
        }
    )
