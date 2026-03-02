"""Minimal WSGI web application for the KP astrology demo repository."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from html import escape
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from src.backend.astro_engine import AstroEngine
from src.backend.chart_engine import ChartEngine, ChartRequest
from src.backend.event_finder import EventFinder
from src.backend.kp_analysis import DashaEngine, TransitAnalyzer
from src.backend.location_service import ChainedLocationResolver, TimezoneResolver, default_location_provider
from src.backend.reporting import ReportingService

location_resolver = ChainedLocationResolver(providers=[default_location_provider()])
timezone_resolver = TimezoneResolver()


class DemoEphemerisProvider:
    """Deterministic fallback provider when swisseph is unavailable."""

    def julday(self, dt_utc: datetime) -> float:
        epoch = datetime(2000, 1, 1, 12, 0, tzinfo=dt_utc.tzinfo)
        return 2451545.0 + (dt_utc - epoch).total_seconds() / 86400

    def calc_ut(self, jd_ut: float, body_id: int) -> tuple[float, float, float]:
        longitude = (jd_ut * (body_id + 1) * 0.985647) % 360
        latitude = ((body_id % 3) - 1) * 0.75
        speed = 0.8 + (body_id % 5) * 0.1
        return longitude, latitude, speed

    def houses_ex(self, jd_ut: float, lat: float, lon: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
        base = (jd_ut * 0.1 + lon + lat) % 360
        cusps = tuple((base + i * 30) % 360 for i in range(12))
        ascmc = ((base + 90) % 360, (base + 180) % 360)
        return cusps, ascmc


def _build_chart_engine() -> ChartEngine:
    try:
        return ChartEngine()
    except RuntimeError:
        return ChartEngine(astro_engine=AstroEngine(provider=DemoEphemerisProvider()))


chart_engine = _build_chart_engine()
dasha_engine = DashaEngine()
transit_analyzer = TransitAnalyzer()
event_finder = EventFinder()
reporting = ReportingService()


def run_analysis(country_code: str, postal_code: str, birth_local: str, transit_local: str, allowed_lords: str) -> dict:
    location = location_resolver.resolve(country_code=country_code, postal_code=postal_code)
    birth_aware = timezone_resolver.localize(datetime.fromisoformat(birth_local), location.timezone)
    transit_aware = timezone_resolver.localize(datetime.fromisoformat(transit_local), location.timezone)

    natal = chart_engine.generate(ChartRequest(timestamp=birth_aware, latitude=location.latitude, longitude=location.longitude))
    transit = chart_engine.generate(
        ChartRequest(timestamp=transit_aware, latitude=location.latitude, longitude=location.longitude)
    )
    contacts = transit_analyzer.compare(natal=natal, transit=transit)
    dashas = dasha_engine.maha_dasha_schedule(start_utc=natal.timestamp_utc, years=36)
    allowed_lord_values = tuple(v.strip().lower() for v in allowed_lords.split(",") if v.strip())
    events = event_finder.find_matches(dasha_periods=dashas, transit_contacts=contacts, allowed_lords=allowed_lord_values)
    report = reporting.build_text_report(chart=natal, events=events)

    return {
        "location": location,
        "natal": natal,
        "contacts": contacts,
        "events": events,
        "allowed_lords": allowed_lord_values,
        "report": report,
    }


def render_page(result: dict | None = None, error: str | None = None, input_values: dict | None = None) -> str:
    values = input_values or {
        "country_code": "IN",
        "postal_code": "560001",
        "birth_local": "1990-01-01T08:30",
        "transit_local": "2025-01-01T08:30",
        "allowed_lords": "venus,jupiter,saturn",
    }

    def field(name: str) -> str:
        return escape(values.get(name, ""))

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>KP Astrology Web Application</title>",
        "<style>",
        "body{font-family:Inter,Segoe UI,Arial,sans-serif;margin:0;background:#eef2ff;color:#0f172a}",
        ".page{max-width:1080px;margin:0 auto;padding:2rem 1rem 3rem}",
        ".hero{background:linear-gradient(135deg,#312e81,#1d4ed8);padding:2rem;border-radius:16px;color:#fff;box-shadow:0 14px 35px rgba(30,64,175,.25)}",
        ".hero h1{margin:0 0 .5rem;font-size:2rem}",
        ".hero p{margin:.25rem 0;color:#dbeafe}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}",
        ".card{background:#fff;border:1px solid #cbd5e1;padding:1rem;margin-top:1rem;border-radius:12px;box-shadow:0 3px 10px rgba(15,23,42,.05)}",
        ".stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.75rem;margin-top:1rem}",
        ".stat{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:.75rem;border-radius:10px}",
        ".stat strong{display:block;font-size:1.25rem;color:#fff}",
        "label{font-size:.9rem;color:#334155;font-weight:600}",
        "input{width:100%;padding:.5rem;border-radius:8px;border:1px solid #cbd5e1;margin-top:.3rem}",
        "button{background:#2563eb;color:#fff;border:none;padding:.7rem 1rem;border-radius:10px;font-weight:700;cursor:pointer}",
        "button:hover{background:#1d4ed8}",
        "table{border-collapse:collapse;width:100%;font-size:.92rem}",
        "th,td{border:1px solid #e2e8f0;padding:.4rem;text-align:left}",
        "th{background:#f8fafc}",
        "pre{white-space:pre-wrap;background:#f8fafc;padding:1rem;border-radius:8px;border:1px solid #e2e8f0}",
        ".error{border-color:#fecaca;background:#fef2f2;color:#b91c1c}",
        "</style></head><body><main class='page'>",
        "<section class='hero'><h1>KP Astrology Analyzer</h1><p>Generate natal charts, transit contacts, and event windows from postal-code based location resolution.</p>",
        "<div class='stats'><div class='stat'><strong>5</strong>Analysis engines</div><div class='stat'><strong>1-click</strong>Report generation</div><div class='stat'><strong>JSON</strong>API endpoints included</div></div></section>",
        "<section class='card'><h2>Run analysis</h2><form method='post' action='/analyze'><div class='grid'>",
        f"<label>Country code<input name='country_code' value='{field('country_code')}' required></label>",
        f"<label>Postal code<input name='postal_code' value='{field('postal_code')}' required></label>",
        f"<label>Birth datetime (local)<input name='birth_local' value='{field('birth_local')}' required></label>",
        f"<label>Transit datetime (local)<input name='transit_local' value='{field('transit_local')}' required></label>",
        f"<label style='grid-column:1/-1'>Allowed lords (comma separated)<input name='allowed_lords' value='{field('allowed_lords')}'></label>",
        "</div><br><button type='submit'>Analyze chart</button></form></section>",
    ]
    if error:
        html.append(f"<div class='card error'><strong>Error:</strong> {escape(error)}</div>")
    if result:
        loc = result["location"]
        html.append(
            f"<div class='card'><h2>Summary</h2><div class='grid'><div><strong>Place</strong><p>{escape(loc.place_name)} ({loc.country_code} {loc.postal_code})</p></div><div><strong>Timezone</strong><p>{escape(loc.timezone)}</p></div><div><strong>Transit contacts</strong><p>{len(result['contacts'])}</p></div><div><strong>Event windows</strong><p>{len(result['events'])}</p></div></div></div>"
        )
        html.append(
            f"<div class='card'><h2>Resolved location</h2><p>{escape(loc.place_name)} ({loc.country_code} {loc.postal_code}), tz {escape(loc.timezone)}</p></div>"
        )
        html.append("<div class='card'><h2>Natal planets</h2><table><tr><th>Body</th><th>Longitude</th><th>Sign</th><th>House</th></tr>")
        for p in result["natal"].planets:
            html.append(
                f"<tr><td>{escape(p.body)}</td><td>{p.longitude:.2f}</td><td>{p.sign_index}</td><td>{p.house_index}</td></tr>"
            )
        html.append("</table></div>")
        html.append("<div class='card'><h2>Text report</h2><pre>{}</pre></div>".format(escape(result["report"])))
    html.append("</main></body></html>")
    return "".join(html)


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if method == "GET" and path == "/api/health":
        payload = json.dumps({"status": "ok"}).encode()
        start_response("200 OK", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
        return [payload]

    if method == "GET" and path.startswith("/api/location/"):
        parts = path.strip("/").split("/")
        if len(parts) != 4:
            payload = json.dumps({"detail": "Invalid location path"}).encode()
            start_response("400 Bad Request", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
            return [payload]
        _, _, country_code, postal_code = parts
        try:
            loc = location_resolver.resolve(country_code=country_code, postal_code=postal_code)
            payload = json.dumps(asdict(loc)).encode()
            status = "200 OK"
        except LookupError as exc:
            payload = json.dumps({"detail": str(exc)}).encode()
            status = "404 Not Found"
        start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
        return [payload]

    if method == "POST" and path == "/analyze":
        size = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(size).decode()
        fields = {k: v[0] for k, v in parse_qs(body).items()}
        try:
            result = run_analysis(
                country_code=fields.get("country_code", ""),
                postal_code=fields.get("postal_code", ""),
                birth_local=fields.get("birth_local", ""),
                transit_local=fields.get("transit_local", ""),
                allowed_lords=fields.get("allowed_lords", ""),
            )
            page = render_page(result=result, input_values=fields)
            status = "200 OK"
        except Exception as exc:  # noqa: BLE001
            page = render_page(error=str(exc), input_values=fields)
            status = "400 Bad Request"
        payload = page.encode()
        start_response(status, [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(payload)))])
        return [payload]

    page = render_page().encode()
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(page)))])
    return [page]


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    with make_server(host, port, app) as server:
        print(f"Serving KP app at http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    serve()
