"""Read-only transport checks: HTTPS, HEAD, OPTIONS, TLS."""

from __future__ import annotations

import socket
import ssl
from urllib.parse import urlparse

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = [pytest.mark.api, pytest.mark.security]


def _https(sut_url: str) -> None:
    if urlparse(sut_url).scheme != "https":
        pytest.skip("TLS and HTTPS redirects apply to https environments")


@pytest.mark.risk_high
@pytest.mark.req("REQ-HTTP-01")
@pytest.mark.req("REQ-SEC-03")
def test_apex_http_redirects_to_https(http: PoliteClient, sut_url: str) -> None:
    _https(sut_url)
    host = urlparse(sut_url).netloc
    response = http.get(f"http://{host}/", cache=False)
    assert response.status_code in {301, 302, 307, 308}
    location = response.headers["location"]
    assert location.startswith(f"https://{host}")


@pytest.mark.risk_high
@pytest.mark.req("REQ-HTTP-02")
def test_homepage_is_html(http: PoliteClient) -> None:
    response = http.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "<html" in response.text.lower()


@pytest.mark.risk_low
@pytest.mark.req("REQ-HTTP-07")
def test_head_and_options_do_not_change_the_homepage(http: PoliteClient) -> None:
    head = http.request("HEAD", "/")
    assert head.status_code == 200
    options = http.request("OPTIONS", "/")
    assert options.status_code in {200, 204, 405}
    again = http.get("/", cache=False)
    assert again.status_code == 200


@pytest.mark.risk_high
@pytest.mark.req("REQ-SEC-03")
def test_tls_version_and_certificate_name(sut_url: str) -> None:
    _https(sut_url)
    host = urlparse(sut_url).hostname
    assert host
    context = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=15) as sock:
        with context.wrap_socket(sock, server_hostname=host) as secure:
            assert secure.version() in {"TLSv1.2", "TLSv1.3"}
            certificate = secure.getpeercert() or {}
            names = [
                value
                for kind, value in certificate.get("subjectAltName", ())
                if kind == "DNS"
            ]
    parent = host.split(".", 1)[1] if host.count(".") >= 1 else host
    assert host in names or f"*.{parent}" in names
