"""Browser flows. Nothing here submits a form or opens Stripe."""

from __future__ import annotations

import json
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


@pytest.mark.risk_high
@pytest.mark.smoke
@pytest.mark.req("REQ-E2E-01")
@pytest.mark.req("REQ-E2E-06")
def test_home_shows_audit_and_stripe_links_without_following_them(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/", wait_until="domcontentloaded")
    heading = page.locator("h1")
    expect(heading).to_be_visible()
    expect(heading).not_to_be_empty()
    cta = page.get_by_role("link", name="Website-Audit für 79 € starten")
    expect(cta).to_be_visible()
    expect(cta).to_have_attribute("href", "/audit/")
    stripe = page.locator("a[href*='buy.stripe.com']")
    assert stripe.count() >= 1
    for index in range(stripe.count()):
        href = stripe.nth(index).get_attribute("href") or ""
        assert href.startswith("https://buy.stripe.com/")
    assert "stripe.com" not in page.url
    assert page.url.rstrip("/") == sut_url


@pytest.mark.risk_medium
@pytest.mark.smoke
@pytest.mark.req("REQ-E2E-02")
def test_navigation_reaches_the_faq(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/", wait_until="domcontentloaded")
    link = page.locator("nav.nav").get_by_role("link", name="FAQ", exact=True)
    if not link.is_visible():
        page.locator("#menuToggle").click()
        link = page.locator("#mobileMenu").get_by_role("link", name="FAQ", exact=True)
    link.click()
    expect(page).to_have_url(re.compile(r"/faq/?$"))
    expect(page.locator("h1")).to_contain_text("Häufige Fragen")


@pytest.mark.risk_low
@pytest.mark.req("REQ-E2E-03")
def test_billing_toggle_changes_the_displayed_price(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/#pricing", wait_until="domcontentloaded")
    price = page.locator("#pricing .price span").first
    before = price.inner_text()
    page.get_by_role("button", name=re.compile(r"Jährlich")).click()
    expect(price).not_to_have_text(before)
    assert page.url.startswith(sut_url)


@pytest.mark.risk_medium
@pytest.mark.smoke
@pytest.mark.req("REQ-E2E-04")
def test_mobile_menu_opens(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/", wait_until="domcontentloaded")
    viewport = page.viewport_size or {"width": 1280, "height": 800}
    if viewport["width"] > 700:
        page.set_viewport_size({"width": 390, "height": 844})
    toggle = page.locator("#menuToggle")
    expect(toggle).to_be_visible()
    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(page.locator("#mobileMenu")).to_be_visible()
    expect(page.locator("#mobileMenu").get_by_role("link", name="FAQ")).to_be_visible()


@pytest.mark.risk_low
@pytest.mark.req("REQ-E2E-05")
def test_theme_toggle_persists_in_local_storage(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/", wait_until="domcontentloaded")
    root = page.locator("html")
    before = root.get_attribute("data-theme")
    page.locator("#themeToggle").click()
    after = root.get_attribute("data-theme")
    assert before in {"dark", "light"}
    assert after in {"dark", "light"}
    assert before != after
    stored = page.evaluate("() => localStorage.getItem('veryops-theme')")
    assert stored == after


@pytest.mark.risk_medium
@pytest.mark.smoke
@pytest.mark.req("REQ-I18N-01")
def test_language_switch_opens_the_english_home(page: Page, sut_url: str) -> None:
    page.goto(sut_url + "/", wait_until="domcontentloaded")
    switch = page.locator("a.lang-switch")
    if not switch.is_visible():
        page.locator("#menuToggle").click()
        switch = page.locator("#mobileMenu a[hreflang='en']")
    expect(switch).to_be_visible()
    expect(switch).to_have_attribute("href", "/en/")
    switch.click()
    expect(page).to_have_url(re.compile(r"/en/?$"))
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("h1")).to_be_visible()


@pytest.mark.risk_high
@pytest.mark.smoke
@pytest.mark.req("REQ-E2E-07")
def test_quote_form_validates_in_the_browser_and_does_not_post(page: Page, sut_url: str) -> None:
    posts: list[str] = []

    def trap(route) -> None:
        posts.append(route.request.url)
        route.abort()

    page.route("**/api/proposal**", trap)
    page.goto(sut_url + "/angebot/", wait_until="domcontentloaded")
    messages = json.loads(page.locator("#quote-strings").inner_text())
    send = page.locator("#quote-send")
    expect(send).to_be_disabled()
    honeypot = page.locator("input[name='company_fax']")
    expect(honeypot).to_have_count(1)
    assert honeypot.get_attribute("aria-hidden") == "true"

    page.locator("#quote-form input[name='name']").fill("QA Portfolio")
    email = page.locator("#quote-form input[name='email']")

    def submit() -> None:
        # The product keeps the button disabled until Turnstile, which this
        # test does not solve. Dispatch the submit listener directly. Any
        # POST is aborted by the route above and by the context guard.
        page.locator("#quote-form").evaluate(
            """form => form.dispatchEvent(
                new Event("submit", { bubbles: true, cancelable: true })
            )"""
        )

    email.fill("not-an-email")
    submit()
    expect(page.locator("#quote-status")).to_have_text(messages["invalidEmail"])

    email.fill("qa-portfolio@example.com")
    submit()
    expect(page.locator("#quote-status")).to_have_text(messages["consentRequired"])

    page.locator("#q-consent-cb").check()
    submit()
    expect(page.locator("#quote-status")).to_have_text(messages["captcha"]["required"])
    assert posts == []
    assert "/angebot" in page.url
