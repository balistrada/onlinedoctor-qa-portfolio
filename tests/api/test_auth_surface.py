"""Negative checks for paths that look like an application. No credentials."""

from __future__ import annotations

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = [pytest.mark.api, pytest.mark.security]

LEAKS = ("traceback", "aws_secret", "private key", "password=")


@pytest.mark.risk_high
@pytest.mark.req("REQ-AUTH-01")
@pytest.mark.parametrize("path", ["/admin/", "/dashboard/", "/login/", "/wp-admin/"])
def test_admin_like_paths_are_not_an_application(http: PoliteClient, path: str) -> None:
    response = http.get(path)
    assert response.status_code in {401, 403, 404}
    body = response.text.lower()
    assert 'type="password"' not in body
    for needle in LEAKS:
        assert needle not in body
    assert "set-cookie" not in {name.lower() for name in response.headers}


@pytest.mark.risk_high
@pytest.mark.req("REQ-AUTH-02")
@pytest.mark.parametrize("path", ["/api/", "/api/health", "/api/proposal"])
def test_unknown_api_paths_do_not_leak(http: PoliteClient, path: str) -> None:
    response = http.get(path)
    assert response.status_code in {401, 403, 404}
    assert len(response.content) < 5_000
    body = response.text.lower()
    for needle in LEAKS:
        assert needle not in body
    if response.status_code == 404:
        assert "not found" in body


@pytest.mark.risk_high
@pytest.mark.req("REQ-SEC-05")
def test_env_file_is_not_served(http: PoliteClient, site: dict) -> None:
    for path in site["secret_probe"]:
        response = http.get(path)
        assert response.status_code in {401, 403, 404}
        body = response.text
        assert "AWS_SECRET" not in body
        assert "DATABASE_URL=" not in body
        assert "BEGIN PRIVATE KEY" not in body
