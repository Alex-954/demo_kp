"""Timezone conversion helpers for location-aware date/time handling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneResolutionError(ValueError):
    """Raised when timezone identifier is invalid."""


@dataclass(frozen=True)
class TimezoneResolver:
    """Resolves IANA timezone names and converts datetimes."""

    def get_zone(self, timezone_name: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise TimezoneResolutionError(f"Unknown timezone '{timezone_name}'.") from exc

    def localize(self, naive_local: datetime, timezone_name: str) -> datetime:
        if naive_local.tzinfo is not None and naive_local.utcoffset() is not None:
            raise ValueError("Expected naive local datetime for localization.")
        zone = self.get_zone(timezone_name)
        return naive_local.replace(tzinfo=zone)

    def convert(self, aware_datetime: datetime, timezone_name: str) -> datetime:
        if aware_datetime.tzinfo is None or aware_datetime.utcoffset() is None:
            raise ValueError("Expected timezone-aware datetime for conversion.")
        zone = self.get_zone(timezone_name)
        return aware_datetime.astimezone(zone)
