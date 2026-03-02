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
        "<!doctype html><html><head><meta charset='utf-8'><title>KP Astrology Web Application</title>",
        "<style>body{font-family:Arial;margin:2rem;background:#f8fafc}.card{background:#fff;border:1px solid #cbd5e1;padding:1rem;margin-bottom:1rem;border-radius:8px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #e2e8f0;padding:.35rem}</style>",
        "</head><body><h1>KP Astrology Web Application</h1>",
        "<div class='card'><form method='post' action='/analyze'>",
        f"Country <input name='country_code' value='{field('country_code')}' required> ",
        f"Postal <input name='postal_code' value='{field('postal_code')}' required><br><br>",
        f"Birth <input name='birth_local' value='{field('birth_local')}' required> ",
        f"Transit <input name='transit_local' value='{field('transit_local')}' required><br><br>",
        f"Allowed lords <input name='allowed_lords' value='{field('allowed_lords')}'><br><br>",
        "<button type='submit'>Analyze</button></form></div>",
    ]
    if error:
        html.append(f"<div class='card'><strong>Error:</strong> {escape(error)}</div>")
    if result:
        loc = result["location"]
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
    html.append("</body></html>")
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
