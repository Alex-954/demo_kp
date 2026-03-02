"""Reporting service for text exports and practitioner summaries."""

from __future__ import annotations

from dataclasses import dataclass

from src.backend.chart_engine import ChartBundle
from src.backend.event_finder import EventMatch


@dataclass(frozen=True)
class ReportingService:
    """Builds compact printable text reports from computed outputs."""

    def build_text_report(self, chart: ChartBundle, events: tuple[EventMatch, ...]) -> str:
        lines = [
            f"KP Report @ {chart.timestamp_utc.isoformat()}",
            "",
            "Planets:",
        ]
        for planet in chart.planets:
            lines.append(
                f"- {planet.body.title()}: {planet.longitude:.2f}° (sign {planet.sign_index}, house {planet.house_index})"
            )

        lines.extend(["", "Event windows:"])
        if not events:
            lines.append("- No matching windows found")
        else:
            for event in events:
                lines.append(f"- {event.timestamp_utc.isoformat()} :: {event.reason}")
        return "\n".join(lines)
