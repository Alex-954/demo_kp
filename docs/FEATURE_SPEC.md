# KP Astrology Calculator — Feature Specification

## 1) Highly Accurate Astronomical Calculations

- Use Swiss Ephemeris (DE431-backed precision) for:
  - planetary longitudes, latitudes, speeds
  - house cusps (Placidus for KP Bhava relevance)
  - nakshatra (star-lord), sub-lord, and prana subdivisions
- Provide deterministic calculations for any timestamp with timezone-aware UTC conversion.
- Include configurable ayanamsa selection with KP default.

## 2) Birth & Transit Place Search (PIN/ZIP/Postcode)

- Input options: country + PIN/ZIP/postal code.
- Resolve to latitude, longitude, timezone, DST history.
- Fallback search chain:
  1. local geocode DB
  2. online geocoding API (optional)
  3. manual lat/long entry

## 3) Chart Generation & Display

### Charts

- Natal (Rasi)
- Navamsa (D9)
- Bhava (Placidus houses)
- KP Cuspal Chart (cusp star/sub details)
- Transit overlay
- Varshaphala / Solar Return
- Tithi Pravesh

### Rendering styles

- North Indian
- South Indian

### Chart data precision

- Degree–Minute–Second (DMS)
- Decimal degrees

## 4) Sub-Lord & Significator Tables

- For each house and event context:
  - house owner
  - star-lord
  - sub-lord
  - significator strengths
- Color-coded output for quick analysis.

## 5) Dasha & Transit Systems

- Vimshottari dasha timeline:
  - Maha dasha
  - Bhukti
  - Antara
  - Sukshma / prana where applicable
- Transit analyzer:
  - natal vs transit contacts
  - house/cusp triggering windows

## 6) Advanced Event Finder + Horary

- Scan date ranges to find condition matches:
  - favorable/unfavorable cusp-sub transitions
  - ruling planet combinations
- KP horary chart for query timestamp.
- Support sub-sub level reasoning for advanced prashna workflows.

## 7) House Rotation & Display Options

- Interactive house rotation in chart viewer.
- Toggle display templates:
  - Original KP
  - ABCD
  - 4-step theory styles

## 8) Aspect & Western Support

- Show Indian aspects.
- Show Western Ptolemaic aspects (configurable orbs).
- Allow blended interpretation mode.

## 9) Database & Chart Management

- Built-in city/town master with geo + timezone metadata.
- Chart persistence:
  - save/update/open
  - backup/restore
  - tagging and search

## 10) Muhurt Selector

- User-defined event type and constraints.
- Return ranked favorable time windows with reasons.

## 11) Extras & Utilities

- Birth-time rectification helpers.
- Cue-card generation for practitioners.
- Print-ready and PDF report exports.
