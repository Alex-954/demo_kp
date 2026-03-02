from datetime import datetime, timezone

from src.backend.application import KPApplication
from src.backend.astro_engine import AstroEngine
from src.backend.chart_engine import ChartEngine


class FakeProvider:
    def julday(self, dt_utc: datetime) -> float:
        return 2_460_000.5

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]:
        return (body_id * 15.0, 0.0, 1.0)

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
        cusps = tuple(float((i * 30) % 360.0) for i in range(1, 13))
        return cusps, (90.0, 180.0)


def test_kp_application_runs_end_to_end_and_saves_chart() -> None:
    chart_engine = ChartEngine(astro_engine=AstroEngine(provider=FakeProvider()))
    app = KPApplication(chart_engine=chart_engine)

    result = app.analyze(
        chart_id="cli-sample",
        country_code="IN",
        postal_code="560001",
        local_timestamp=datetime(1990, 8, 24, 13, 45, 0),
        transit_timestamp_utc=datetime(2026, 2, 20, 5, 30, tzinfo=timezone.utc),
    )

    assert "KP Report" in result.report
    assert app.repository.get("cli-sample").timestamp_utc == result.chart.timestamp_utc
