"""Command-line entry point for running KP chart analysis workflows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from src.backend.application import KPApplication


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run KP analysis for a birth place and timestamps.")
    parser.add_argument("--chart-id", required=True, help="Identifier for persisted natal chart")
    parser.add_argument("--country", required=True, help="Country code (example: IN)")
    parser.add_argument("--postal", required=True, help="Postal code (example: 560001)")
    parser.add_argument(
        "--birth-local",
        required=True,
        help="Naive local birth datetime in ISO format, e.g. 1990-08-24T13:45:00",
    )
    parser.add_argument(
        "--transit-utc",
        required=True,
        help="Transit datetime in UTC ISO format, e.g. 2026-02-20T05:30:00+00:00",
    )
    parser.add_argument(
        "--backup-path",
        default="charts_backup.json",
        help="Path for writing repository backup JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    birth_local = datetime.fromisoformat(args.birth_local)
    transit_utc = datetime.fromisoformat(args.transit_utc)
    if transit_utc.tzinfo is None or transit_utc.utcoffset() is None:
        transit_utc = transit_utc.replace(tzinfo=timezone.utc)

    app = KPApplication()
    result = app.analyze(
        chart_id=args.chart_id,
        country_code=args.country,
        postal_code=args.postal,
        local_timestamp=birth_local,
        transit_timestamp_utc=transit_utc,
    )

    print(result.report)

    backup_path = Path(args.backup_path)
    backup_path.write_text(app.repository.backup_json(), encoding="utf-8")
    print(f"\nSaved chart backup: {backup_path}")


if __name__ == "__main__":
    main()
