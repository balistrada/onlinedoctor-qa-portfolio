"""Error paths that stay read-only: real 404, offline, mocked failure, blocked captcha."""

from __future__ import annotations

import json

import pytest
from playwright.sync_api import Error, Page, expect

pytestmark = pytest.mark.e2e


@pytest.mark.risk_medium
@pytest.mark.smoke
@pytest.mark.req("REQ-ERR-01")
def test_not_found_page_links_home(page: Page, sut_url: str, site: dict) -> None:
    response = page.goto(sut_url + site["missing_path"], wait_until="domcontentloaded")
    assert response is not None
    assert response.status == 404
    expect(page.locator("h1")).to_contain_text("Seite nicht gefunden")
    expect(page.get_by_role("link", name="Zur Startseite")).to_have_attribute("href", "/")


@pytest.mark.risk_medium
@pytest.mark.req("REQ-ERR-02")
def test_offline_navigation_fails_closed(page: Page, sut_url: str) -> None:
    page.context.set_offline(True)
    with pytest.raises(Error):
        page.goto(sut_url + "/", wait_until="domcontentloaded", timeout=8_000)


@pytest.mark.risk_medium
@pytest.mark.req("REQ-ERR-03")
def test_blocked_turnstile_shows_an_error_and_does_not_post(page: Page, sut_url: str) -> None:
    posts: list[str] = []

    def trap(route) -> None:
        posts.append(route.request.url)
        route.abort()

    page.route("**/api/proposal**", trap)
    page.route("https://challenges.cloudflare.com/**", lambda route: route.abort())
    page.goto(sut_url + "/angebot/", wait_until="domcontentloaded")
    messages = json.loads(page.locator("#quote-strings").inner_text())
    expect(page.locator(".q-capfail")).to_contain_text(
        messages["captcha"]["failed"], timeout=12_000
    )
    assert posts == []


@pytest.mark.risk_low
@pytest.mark.req("REQ-ERR-04")
def test_route_mock_serves_a_document_failure_without_the_network(page: Page, sut_url: str) -> None:
    def fulfill(route) -> None:
        route.fulfill(
            status=500,
            content_type="text/html",
            body="<!doctype html><title>simulated failure</title><h1>simulated failure</h1>",
        )

    page.route(sut_url + "/audit/", fulfill)
    response = page.goto(sut_url + "/audit/", wait_until="domcontentloaded")
    assert response is not None
    assert response.status == 500
    expect(page.get_by_role("heading", name="simulated failure")).to_be_visible()
