"""Typed models for location and timezone resolution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResolvedLocation:
    """Resolved geographic location from postal inputs."""

    country_code: str
    postal_code: str
    place_name: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class LocationQuery:
    """Location query fields for postcode lookup."""

    country_code: str
    postal_code: str
