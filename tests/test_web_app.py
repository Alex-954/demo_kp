import io
import json
from urllib.parse import urlencode

from src.web_app import app


def call_app(path: str, method: str = 'GET', body: str = ''):
    payload = body.encode()
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'CONTENT_LENGTH': str(len(payload)),
        'wsgi.input': io.BytesIO(payload),
    }
    captured = {}

    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = dict(headers)

    chunks = app(environ, start_response)
    response_body = b''.join(chunks)
    return captured['status'], captured['headers'], response_body


def test_health_endpoint() -> None:
    status, _headers, body = call_app('/api/health')
    assert status == '200 OK'
    assert json.loads(body) == {'status': 'ok'}


def test_location_endpoint_success() -> None:
    status, _headers, body = call_app('/api/location/IN/560001')
    assert status == '200 OK'
    payload = json.loads(body)
    assert payload['place_name'] == 'Bengaluru'


def test_location_endpoint_not_found() -> None:
    status, _headers, _body = call_app('/api/location/IN/999999')
    assert status == '404 Not Found'


def test_analyze_page_renders_report() -> None:
    form = urlencode(
        {
            'country_code': 'IN',
            'postal_code': '560001',
            'birth_local': '1990-01-01T08:30',
            'transit_local': '2025-01-01T08:30',
            'allowed_lords': 'venus,jupiter,saturn',
        }
    )
    status, _headers, body = call_app('/analyze', method='POST', body=form)
    text = body.decode()

    assert status == '200 OK'
    assert 'KP Astrology Web Application' in text
    assert 'Text report' in text
