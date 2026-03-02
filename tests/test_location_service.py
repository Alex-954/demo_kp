from datetime import datetime, timezone

import pytest

from src.backend.location_service import (
    ChainedLocationResolver,
    LocationResolverError,
    StaticLocationProvider,
    TimezoneResolutionError,
    TimezoneResolver,
    default_location_provider,
)


def test_default_location_provider_resolves_by_country_and_postal_code() -> None:
    resolver = ChainedLocationResolver(providers=[default_location_provider()])

    result = resolver.resolve("in", "560001")

    assert result.place_name == "Bengaluru"
    assert result.latitude == pytest.approx(12.9766)
    assert result.timezone == "Asia/Kolkata"


def test_chained_location_resolver_falls_back_to_next_provider() -> None:
    empty = StaticLocationProvider(records={})
    resolver = ChainedLocationResolver(providers=[empty, default_location_provider()])

    result = resolver.resolve("US", "10001")

    assert result.place_name == "New York"


def test_location_resolver_error_when_no_provider_matches() -> None:
    resolver = ChainedLocationResolver(providers=[StaticLocationProvider(records={})])

    with pytest.raises(LocationResolverError):
        resolver.resolve("IN", "999999")


def test_timezone_resolver_convert_between_zones() -> None:
    tz = TimezoneResolver()
    source = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    converted = tz.convert(source, "Asia/Kolkata")

    assert converted.hour == 17
    assert converted.minute == 30


def test_timezone_resolver_rejects_unknown_zone() -> None:
    tz = TimezoneResolver()

    with pytest.raises(TimezoneResolutionError):
        tz.get_zone("Mars/Olympus_Mons")
