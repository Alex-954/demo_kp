"""Chart engine for planetary placements and KP cusp decomposition tables."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.backend.astro_engine import AstroEngine

from .types import ChartBundle, ChartPlanet, ChartRequest, KPCuspDetail

KP_LORD_SEQUENCE = ("ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury")


@dataclass
class ChartEngine:
    """Generates deterministic chart snapshots and KP cusp tables."""

    astro_engine: AstroEngine = field(default_factory=AstroEngine)
    tracked_bodies: tuple[str, ...] = (
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "ketu",
    )

    def generate(self, request: ChartRequest) -> ChartBundle:
        planets: list[ChartPlanet] = []
        houses = self.astro_engine.placidus_house_cusps(request.timestamp, request.latitude, request.longitude)
        for body in self.tracked_bodies:
            pos = self.astro_engine.planet_position(body, request.timestamp)
            longitude = pos.longitude % 360.0
            sign_index = int(longitude // 30) + 1
            house_index = self._house_for_longitude(longitude, houses.cusps)
            planets.append(
                ChartPlanet(
                    body=body,
                    longitude=longitude,
                    sign_index=sign_index,
                    house_index=house_index,
                )
            )

        cusp_details = tuple(
            self._kp_detail(house_index=index + 1, cusp_longitude=longitude % 360.0)
            for index, longitude in enumerate(houses.cusps)
        )

        return ChartBundle(timestamp_utc=houses.timestamp_utc, planets=tuple(planets), cusp_details=cusp_details)

    def _house_for_longitude(self, longitude: float, cusps: tuple[float, ...]) -> int:
        for index, cusp in enumerate(cusps):
            next_cusp = cusps[(index + 1) % len(cusps)]
            start = cusp % 360.0
            end = next_cusp % 360.0
            in_house = (start <= longitude < end) if start < end else (longitude >= start or longitude < end)
            if in_house:
                return index + 1
        return 12

    def _kp_detail(self, house_index: int, cusp_longitude: float) -> KPCuspDetail:
        nakshatra_size = 360.0 / 27
        nakshatra_index = int(cusp_longitude // nakshatra_size) + 1
        star_lord = KP_LORD_SEQUENCE[(nakshatra_index - 1) % len(KP_LORD_SEQUENCE)]

        sub_slot = int((cusp_longitude % nakshatra_size) // (nakshatra_size / len(KP_LORD_SEQUENCE)))
        sub_lord = KP_LORD_SEQUENCE[sub_slot]

        return KPCuspDetail(
            house_index=house_index,
            cusp_longitude=cusp_longitude,
            nakshatra_index=nakshatra_index,
            star_lord=star_lord,
            sub_lord=sub_lord,
        )
