"""Location resolver with deterministic local catalog and provider fallback chain."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .types import LocationQuery, ResolvedLocation


class LocationResolverError(LookupError):
    """Raised when no location can be resolved for a query."""


class LocationProvider(Protocol):
    """Provider interface for postcode-based geographic resolution."""

    def resolve(self, query: LocationQuery) -> ResolvedLocation | None: ...


@dataclass
class StaticLocationProvider:
    """In-memory local geo master keyed by country + postcode."""

    records: dict[tuple[str, str], ResolvedLocation]

    def resolve(self, query: LocationQuery) -> ResolvedLocation | None:
        key = (query.country_code.upper(), query.postal_code.strip().upper())
        return self.records.get(key)


@dataclass
class ChainedLocationResolver:
    """Runs providers in order until one returns a location."""

    providers: list[LocationProvider] = field(default_factory=list)

    def resolve(self, country_code: str, postal_code: str) -> ResolvedLocation:
        query = LocationQuery(country_code=country_code.strip().upper(), postal_code=postal_code.strip().upper())
        for provider in self.providers:
            hit = provider.resolve(query)
            if hit is not None:
                return hit
        raise LocationResolverError(
            f"Could not resolve location for country='{query.country_code}', postal_code='{query.postal_code}'."
        )


def default_location_provider() -> StaticLocationProvider:
    """Minimal seed catalog for deterministic local resolution."""

    data = {
        ("IN", "560001"): ResolvedLocation(
            country_code="IN",
            postal_code="560001",
            place_name="Bengaluru",
            latitude=12.9766,
            longitude=77.5993,
            timezone="Asia/Kolkata",
        ),
        ("US", "10001"): ResolvedLocation(
            country_code="US",
            postal_code="10001",
            place_name="New York",
            latitude=40.7506,
            longitude=-73.9972,
            timezone="America/New_York",
        ),
    }
    return StaticLocationProvider(records=data)
