from datetime import datetime, timezone

from src.backend.astro_engine import AstroEngine
from src.backend.chart_engine import ChartEngine, ChartRequest
from src.backend.event_finder import EventFinder
from src.backend.kp_analysis import DashaEngine, TransitAnalyzer
from src.backend.reporting import ReportingService
from src.backend.storage import ChartRepository


class FakeProvider:
    def julday(self, dt_utc: datetime) -> float:
        return 2_460_000.5

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]:
        return (body_id * 15.0, 0.0, 1.0)

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
        cusps = tuple(float((i * 30) % 360.0) for i in range(1, 13))
        return cusps, (90.0, 180.0)


def test_chart_engine_generates_planets_and_kp_cusps() -> None:
    chart_engine = ChartEngine(astro_engine=AstroEngine(provider=FakeProvider()))
    request = ChartRequest(timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc), latitude=12.9, longitude=77.6)

    chart = chart_engine.generate(request)

    assert len(chart.planets) == 9
    assert len(chart.cusp_details) == 12
    assert chart.cusp_details[0].house_index == 1


def test_dasha_transit_event_and_reporting_pipeline() -> None:
    chart_engine = ChartEngine(astro_engine=AstroEngine(provider=FakeProvider()))
    natal = chart_engine.generate(ChartRequest(datetime(2024, 1, 1, tzinfo=timezone.utc), 0.0, 0.0))
    transit = chart_engine.generate(ChartRequest(datetime(2024, 1, 2, tzinfo=timezone.utc), 0.0, 0.0))

    dasha = DashaEngine().maha_dasha_schedule(start_utc=datetime(2020, 1, 1, tzinfo=timezone.utc), years=20)
    contacts = TransitAnalyzer().compare(natal=natal, transit=transit)
    events = EventFinder().find_matches(dasha_periods=dasha, transit_contacts=contacts, allowed_lords=("ketu", "venus"))

    report = ReportingService().build_text_report(natal, events)

    assert "KP Report" in report
    assert isinstance(events, tuple)


def test_chart_repository_backup_and_restore_roundtrip() -> None:
    chart_engine = ChartEngine(astro_engine=AstroEngine(provider=FakeProvider()))
    chart = chart_engine.generate(ChartRequest(datetime(2024, 1, 1, tzinfo=timezone.utc), 10.0, 20.0))

    repo = ChartRepository()
    repo.save("sample", chart)
    payload = repo.backup_json()

    recovered = ChartRepository()
    recovered.restore_json(payload)

    loaded = recovered.get("sample")
    assert loaded.timestamp_utc == chart.timestamp_utc
    assert loaded.planets[0].body == chart.planets[0].body
