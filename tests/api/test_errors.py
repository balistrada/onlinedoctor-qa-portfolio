"""Status contracts for missing pages. No fuzzing, one fixed path."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = pytest.mark.api


@pytest.mark.risk_medium
@pytest.mark.req("REQ-HTTP-06")
def test_unknown_path_is_a_branded_404(http: PoliteClient, site: dict) -> None:
    response = http.get(site["missing_path"])
    assert response.status_code == 404
    assert "text/html" in response.headers.get("content-type", "")
    assert "Seite nicht gefunden" in response.text
    assert "Zur Startseite" in response.text


@pytest.mark.risk_medium
@pytest.mark.security
@pytest.mark.req("REQ-HTTP-06")
def test_unknown_path_without_slash_stays_on_https(
    http: PoliteClient, site: dict, sut_url: str
) -> None:
    if urlparse(sut_url).scheme != "https":
        pytest.skip("slash redirect scheme is asserted on https")
    bare = site["missing_path"].rstrip("/")
    response = http.get(bare, cache=False)
    assert response.status_code in {301, 302, 307, 308}
    location = urljoin(sut_url + "/", response.headers["location"])
    assert urlparse(location).scheme == "https"
