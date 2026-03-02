"""High-level KP application workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.backend.chart_engine import ChartBundle, ChartEngine, ChartRequest
from src.backend.event_finder import EventFinder, EventMatch
from src.backend.kp_analysis import DashaEngine, TransitAnalyzer
from src.backend.location_service import ChainedLocationResolver, TimezoneResolver, default_location_provider
from src.backend.reporting import ReportingService
from src.backend.storage import ChartRepository


@dataclass(frozen=True)
class AnalysisResult:
    """End-to-end KP analysis output for one client request."""

    chart_id: str
    chart: ChartBundle
    events: tuple[EventMatch, ...]
    report: str


@dataclass
class KPApplication:
    """Application service that connects location, chart, analysis, reporting, and storage modules."""

    chart_engine: ChartEngine = field(default_factory=ChartEngine)
    dasha_engine: DashaEngine = field(default_factory=DashaEngine)
    transit_analyzer: TransitAnalyzer = field(default_factory=TransitAnalyzer)
    event_finder: EventFinder = field(default_factory=EventFinder)
    reporting_service: ReportingService = field(default_factory=ReportingService)
    repository: ChartRepository = field(default_factory=ChartRepository)
    location_resolver: ChainedLocationResolver = field(
        default_factory=lambda: ChainedLocationResolver(providers=[default_location_provider()])
    )
    timezone_resolver: TimezoneResolver = field(default_factory=TimezoneResolver)

    def analyze(
        self,
        *,
        chart_id: str,
        country_code: str,
        postal_code: str,
        local_timestamp: datetime,
        transit_timestamp_utc: datetime,
        allowed_lords: tuple[str, ...] = ("ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"),
    ) -> AnalysisResult:
        """Build and persist natal chart, run transit+dasha analysis, and render a text report."""

        location = self.location_resolver.resolve(country_code=country_code, postal_code=postal_code)
        localized = self.timezone_resolver.localize(local_timestamp, location.timezone)

        natal = self.chart_engine.generate(
            ChartRequest(timestamp=localized, latitude=location.latitude, longitude=location.longitude)
        )
        transit = self.chart_engine.generate(
            ChartRequest(timestamp=transit_timestamp_utc, latitude=location.latitude, longitude=location.longitude)
        )

        dasha = self.dasha_engine.maha_dasha_schedule(start_utc=natal.timestamp_utc, years=40)
        contacts = self.transit_analyzer.compare(natal=natal, transit=transit)
        events = self.event_finder.find_matches(dasha_periods=dasha, transit_contacts=contacts, allowed_lords=allowed_lords)
        report = self.reporting_service.build_text_report(natal, events)

        self.repository.save(chart_id, natal)

        return AnalysisResult(chart_id=chart_id, chart=natal, events=events, report=report)
