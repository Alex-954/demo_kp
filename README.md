# KP Astrology Application Blueprint

This repository contains an implementation blueprint for a **KP (Krishnamurti Paddhati) Astrology Calculator**.

## Core goals

- Deliver astronomy-grade precision for planetary and house calculations.
- Provide complete KP workflows: charts, cusps, sub-lords, significators, dasha/timing, transit, and horary.
- Support practical usability: PIN/ZIP location search, chart database, print/report options, backup.

## Feature set covered

1. Highly accurate astronomical calculations (Swiss Ephemeris / DE431 level).
2. Birth & transit place search using PIN/ZIP/postal code.
3. Multi-chart generation (Rasi, Navamsa, Bhava, KP Cuspal, Transit, Varshaphala, Tithi Pravesh).
4. Sub-lord and significator tables with color coding.
5. Vimshottari dasha with sub/sub-sub period timing + transit analysis.
6. Advanced event finder + KP horary up to sub-sub levels.
7. House rotation & display preferences (styles, DMS precision).
8. Indian + Western aspect support.
9. Database and chart management (save, backup, retrieve).
10. Muhurt selector.
11. Utilities (birth-time rectification, cue cards, printing/report export).

## Repository structure

- `docs/FEATURE_SPEC.md` — full functional specification derived from your requirements.
- `docs/ARCHITECTURE.md` — implementation architecture and module decomposition.
- `docs/ROADMAP.md` — suggested development plan by milestones.

## Next implementation step

Build the backend service modules in this order:

1. Astronomical engine integration.
2. Location and timezone resolution.
3. Chart engine + KP tables.
4. Dasha/transit + event finder.
5. UI/reporting and chart database.

## Implemented module status

- ✅ Milestone order step 1 completed: `astro_engine` backend module integrated with a Swiss Ephemeris provider boundary and deterministic UTC normalization.
- ✅ Milestone order step 2 completed: `location_service` module added for postal-code location resolution and IANA timezone conversion utilities.
- ✅ Milestone order step 3 completed: `chart_engine` now generates chart bundles and KP cusp/star/sub decomposition tables.
- ✅ Milestone order step 4 completed: `kp_analysis` + `event_finder` modules now provide dasha schedule generation, transit contact analysis, and event matching.
- ✅ Milestone order step 5 completed: `reporting` and `storage` modules now provide text report generation and chart backup/restore persistence.

## Run the application

You can now run an end-to-end KP analysis as a CLI app:

```bash
kp-app \
  --chart-id demo-1 \
  --country IN \
  --postal 560001 \
  --birth-local 1990-08-24T13:45:00 \
  --transit-utc 2026-02-20T05:30:00+00:00
```

The command prints a KP report and writes a JSON chart backup (default `charts_backup.json`).
