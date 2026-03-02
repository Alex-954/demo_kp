"""Chart repository with JSON backup/restore helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

from src.backend.chart_engine import ChartBundle


@dataclass
class ChartRepository:
    """In-memory chart storage for save/open and backup operations."""

    _charts: dict[str, ChartBundle] = field(default_factory=dict)

    def save(self, chart_id: str, chart: ChartBundle) -> None:
        self._charts[chart_id] = chart

    def get(self, chart_id: str) -> ChartBundle:
        return self._charts[chart_id]

    def backup_json(self) -> str:
        payload = {}
        for chart_id, chart in self._charts.items():
            payload[chart_id] = {
                "timestamp_utc": chart.timestamp_utc.isoformat(),
                "planets": [asdict(planet) for planet in chart.planets],
                "cusp_details": [asdict(cusp) for cusp in chart.cusp_details],
            }
        return json.dumps(payload, sort_keys=True)

    def restore_json(self, data: str) -> None:
        payload = json.loads(data)
        self._charts.clear()
        from src.backend.chart_engine.types import ChartBundle, ChartPlanet, KPCuspDetail

        for chart_id, raw in payload.items():
            self._charts[chart_id] = ChartBundle(
                timestamp_utc=datetime.fromisoformat(raw["timestamp_utc"]),
                planets=tuple(ChartPlanet(**planet) for planet in raw["planets"]),
                cusp_details=tuple(KPCuspDetail(**cusp) for cusp in raw["cusp_details"]),
            )
