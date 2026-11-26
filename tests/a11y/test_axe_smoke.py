"""axe-core smoke. Critical and serious findings fail the test; moderate ones do not."""

from __future__ import annotations

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.a11y

PAGES = ["/", "/audit/", "/faq/", "/angebot/", "/impressum/"]


# Visible text "EN" / "DE" is not part of the accessible name
# ("Switch to English" / "Auf Deutsch wechseln"). axe flags that on every page.
KNOWN_SERIOUS = {"label-content-name-mismatch"}


@pytest.mark.risk_medium
@pytest.mark.req("REQ-A11Y-01")
@pytest.mark.flaky(reruns=0)
@pytest.mark.parametrize("path", PAGES)
def test_no_serious_axe_violations(page: Page, sut_url: str, path: str) -> None:
    page.goto(sut_url + path, wait_until="domcontentloaded")
    expect(page.locator("h1")).to_be_visible()
    results = Axe().run(page)
    blocking = [
        violation
        for violation in results.response.get("violations", [])
        if violation.get("impact") in {"critical", "serious"}
    ]
    unexpected = [item for item in blocking if item.get("id") not in KNOWN_SERIOUS]
    if unexpected:
        summary = ", ".join(
            f"{item.get('id')} ({item.get('impact')}, {len(item.get('nodes', []))} nodes)"
            for item in unexpected
        )
        pytest.fail(f"{path}: {summary}")
    known = [item for item in blocking if item.get("id") in KNOWN_SERIOUS]
    if known:
        pytest.xfail(
            "DEF-A11Y-01: language switch accessible name omits the visible EN/DE text"
        )
