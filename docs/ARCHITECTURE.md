# Proposed Architecture

## Backend modules

1. `astro_engine`
   - Swiss Ephemeris wrapper
   - time conversion and ayanamsa config
2. `location_service`
   - PIN/ZIP/postcode resolver
   - timezone resolver
3. `chart_engine`
   - divisional charts
   - KP cuspal decomposition
4. `kp_analysis`
   - significators, sub-lords, ruling planets
   - dasha timelines
5. `event_finder`
   - condition compiler
   - time-range scanning
6. `storage`
   - chart persistence and backup
7. `reporting`
   - printable and exportable outputs

## UI layers

- Data-entry forms for birth, transit, and horary.
- Chart canvas with North/South mode switching.
- Tables for cusps, sub-lords, and significators.
- Timelines for dasha and transit windows.

## Data model (minimum)

- `PersonProfile`
- `GeoLocation`
- `ChartSnapshot`
- `CuspDetail`
- `PlanetPosition`
- `DashaPeriod`
- `TransitEvent`
- `MuhurtWindow`

## Non-functional requirements

- Deterministic and reproducible calculations.
- Millisecond timestamp fidelity internally.
- Modular computation pipelines for batch processing.
- Auditability: every prediction view links to source astronomical values.
