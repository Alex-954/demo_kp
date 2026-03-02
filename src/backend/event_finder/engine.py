"""Event finder module for scanning dasha and transit windows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.backend.kp_analysis import DashaPeriod, TransitContact


@dataclass(frozen=True)
class EventMatch:
    """A matched event window with trigger context."""

    timestamp_utc: datetime
    reason: str


@dataclass(frozen=True)
class EventFinder:
    """Finds events from transit contacts and dasha constraints."""

    def find_matches(
        self,
        dasha_periods: tuple[DashaPeriod, ...],
        transit_contacts: tuple[TransitContact, ...],
        allowed_lords: tuple[str, ...],
    ) -> tuple[EventMatch, ...]:
        hits: list[EventMatch] = []
        for contact in transit_contacts:
            for period in dasha_periods:
                if period.lord not in allowed_lords:
                    continue
                if period.start_utc <= contact.timestamp_utc <= period.end_utc:
                    hits.append(
                        EventMatch(
                            timestamp_utc=contact.timestamp_utc,
                            reason=f"{contact.transit_body} {contact.angle:.0f}° {contact.natal_body} during {period.lord}",
                        )
                    )
                    break
        return tuple(hits)
