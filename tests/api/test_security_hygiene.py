"""Header, cookie, redirect, and privacy observations. Known gaps are xfail."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = [pytest.mark.api, pytest.mark.security]


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEC-01")
@pytest.mark.xfail(
    reason="DEF-SEC-01: public HTML responses omit standard hardening headers",
    strict=False,
)
@pytest.mark.flaky(reruns=0)
def test_public_html_sends_hardening_headers(http: PoliteClient, site: dict) -> None:
    response = http.get("/")
    missing = [name for name in site["hardening_headers"] if name not in response.headers]
    assert not missing, missing


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEC-02")
def test_public_slash_redirect_stays_on_https(http: PoliteClient, sut_url: str) -> None:
    if urlparse(sut_url).scheme != "https":
        pytest.skip("https redirect asserted only for https environments")
    response = http.get("/audit", cache=False)
    assert response.status_code in {301, 302, 307, 308}
    location = urljoin(sut_url + "/", response.headers["location"])
    parsed = urlparse(location)
    assert parsed.scheme == "https"
    assert parsed.path.rstrip("/") == "/audit"


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEC-02")
@pytest.mark.xfail(
    reason="DEF-SEC-02: /api redirects to http:// before bouncing back to https",
    strict=False,
)
@pytest.mark.flaky(reruns=0)
def test_api_root_redirect_stays_on_https(http: PoliteClient, sut_url: str) -> None:
    if urlparse(sut_url).scheme != "https":
        pytest.skip("https redirect asserted only for https environments")
    response = http.get("/api", cache=False)
    assert response.status_code in {301, 302, 307, 308}
    location = urljoin(sut_url + "/", response.headers["location"])
    assert urlparse(location).scheme == "https"


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEC-04")
def test_public_documents_set_no_unflagged_cookies(http: PoliteClient) -> None:
    for path in ("/", "/audit/", "/datenschutz/"):
        response = http.get(path)
        for cookie in response.headers.get_list("set-cookie"):
            lowered = cookie.lower()
            assert "secure" in lowered
            assert "httponly" in lowered or "samesite" in lowered


@pytest.mark.risk_medium
@pytest.mark.req("REQ-PRIV-01")
@pytest.mark.xfail(
    reason="DEF-PRIV-01: analytics beacon is served but not disclosed",
    strict=False,
)
@pytest.mark.flaky(reruns=0)
def test_analytics_beacon_is_absent_or_disclosed(http: PoliteClient) -> None:
    # Cloudflare injects the beacon for browser user agents and omits it for
    # the suite's identifying UA. Visitors get the browser response.
    browser = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html",
    }
    home = http.get("/", cache=False, headers=browser).text
    if "cloudflareinsights.com" not in home:
        pytest.skip(
            "DEF-PRIV-01: beacon was not injected on this response. "
            "The finding stays open in defects/register.yml."
        )
    # The beacon tag is on the privacy page too. Only the visible text counts
    # as a disclosure.
    visible = re.sub(r"<script[\s\S]*?</script>", " ", http.get("/datenschutz/").text, flags=re.I)
    visible = re.sub(r"<style[\s\S]*?</style>", " ", visible, flags=re.I)
    visible = re.sub(r"<[^>]+>", " ", visible).casefold()
    disclosed = "cloudflareinsights" in visible or "web analytics" in visible
    assert disclosed


@pytest.mark.risk_low
@pytest.mark.integration
@pytest.mark.req("REQ-INT-02")
def test_plain_mailto_is_present(http: PoliteClient, site: dict) -> None:
    html = http.get("/").text
    assert f'mailto:{site["contact_email"]}' in html


@pytest.mark.risk_low
@pytest.mark.integration
@pytest.mark.req("REQ-INT-02")
@pytest.mark.xfail(
    reason="DEF-LINK-01: Cloudflare email-protection URL responds 404",
    strict=False,
)
@pytest.mark.flaky(reruns=0)
def test_obfuscated_email_link_resolves(http: PoliteClient) -> None:
    html = http.get("/").text
    match = re.search(r'href="(/cdn-cgi/l/email-protection[^"]*)"', html)
    assert match, "no obfuscated email link on the homepage"
    response = http.get(match.group(1), cache=False)
    assert response.status_code == 200
