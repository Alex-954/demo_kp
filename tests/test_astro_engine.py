from datetime import datetime, timedelta, timezone

import pytest

from src.backend.astro_engine.engine import AstroEngine
from src.backend.astro_engine.time import TimeNormalizationError, normalize_to_utc


class FakeProvider:
    def julday(self, dt_utc: datetime) -> float:
        return 2_460_000.5

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]:
        return (123.45 + body_id, -1.2, 0.98)

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
        cusps = tuple(float(i * 30) for i in range(1, 13))
        ascmc = (15.0, 270.0)
        return cusps, ascmc


def test_normalize_to_utc_timezone_conversion() -> None:
    local = datetime(2024, 5, 1, 10, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    normalized = normalize_to_utc(local)
    assert normalized == datetime(2024, 5, 1, 5, 0, tzinfo=timezone.utc)


def test_normalize_to_utc_rejects_naive_datetime() -> None:
    with pytest.raises(TimeNormalizationError):
        normalize_to_utc(datetime(2024, 5, 1, 10, 30))


def test_planet_position_from_provider() -> None:
    engine = AstroEngine(provider=FakeProvider())
    ts = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)

    result = engine.planet_position("sun", ts)

    assert result.body == "sun"
    assert result.julian_day_ut == 2_460_000.5
    assert result.longitude == 123.45
    assert result.latitude == -1.2
    assert result.speed_longitude == 0.98


def test_house_cusps_from_provider() -> None:
    engine = AstroEngine(provider=FakeProvider())
    ts = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)

    result = engine.placidus_house_cusps(ts, 12.97, 77.59)

    assert len(result.cusps) == 12
    assert result.ascendant == 15.0
    assert result.midheaven == 270.0


def test_unknown_body_raises_error() -> None:
    engine = AstroEngine(provider=FakeProvider())
    ts = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="Unknown body"):
        engine.planet_position("pluto", ts)
