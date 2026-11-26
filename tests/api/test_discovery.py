"""robots.txt, sitemaps, llms.txt, and JSON-LD. All reads, all cached."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = pytest.mark.api


class _JsonLd(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._capture = False
        self._buf: list[str] = []
        self.blocks: list[object] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._capture = True
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capture:
            self.blocks.append(json.loads("".join(self._buf)))
            self._capture = False

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buf.append(data)


def _types(node: object, found: set[str]) -> None:
    if isinstance(node, dict):
        value = node.get("@type")
        if isinstance(value, str):
            found.add(value)
        elif isinstance(value, list):
            found.update(item for item in value if isinstance(item, str))
        for child in node.values():
            _types(child, found)
    elif isinstance(node, list):
        for child in node:
            _types(child, found)


def _jsonld_types(html: str) -> set[str]:
    parser = _JsonLd()
    parser.feed(html)
    found: set[str] = set()
    for block in parser.blocks:
        _types(block, found)
    return found


@pytest.mark.risk_medium
@pytest.mark.req("REQ-HTTP-03")
def test_robots_allows_crawling_and_names_the_sitemap(http: PoliteClient, sut_url: str) -> None:
    response = http.get("/robots.txt")
    assert response.status_code == 200
    body = response.text
    assert "User-agent: *" in body
    assert re.search(r"(?m)^Allow:\s*/\s*$", body)
    assert f"Sitemap: {sut_url}/sitemap-index.xml" in body


@pytest.mark.risk_medium
@pytest.mark.req("REQ-HTTP-04")
def test_sitemap_index_and_legacy_path(http: PoliteClient, sut_url: str) -> None:
    index = http.get("/sitemap-index.xml")
    assert index.status_code == 200
    assert "<sitemapindex" in index.text
    assert "/sitemap-0.xml" in index.text or "<loc>" in index.text
    legacy = http.get("/sitemap.xml", cache=False)
    assert legacy.status_code in {301, 302, 307, 308}
    assert legacy.headers["location"].startswith(f"{sut_url}/sitemap-index.xml")


@pytest.mark.risk_medium
@pytest.mark.req("REQ-HTTP-05")
def test_llms_txt_names_the_offer(http: PoliteClient, sut_url: str) -> None:
    response = http.get("/llms.txt")
    assert response.status_code == 200
    body = response.text
    for fragment in (f"{sut_url}/audit/", f"{sut_url}/faq/", f"{sut_url}/en/quote/", "veryops"):
        assert fragment in body


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEO-01")
def test_core_pages_expose_language_and_canonical(
    http: PoliteClient, site: dict, sut_url: str
) -> None:
    for page in site["seo_pages"]:
        response = http.get(page["path"])
        assert response.status_code == 200, page["path"]
        html = response.text
        assert f'lang="{page["lang"]}"' in html
        assert "<title>" in html and "</title>" in html
        assert 'rel="canonical"' in html
        assert 'name="description"' in html
        assert 'hreflang="de"' in html
        assert 'hreflang="en"' in html
        assert sut_url in html


@pytest.mark.risk_medium
@pytest.mark.req("REQ-SEO-02")
def test_jsonld_matches_the_page(http: PoliteClient) -> None:
    home = _jsonld_types(http.get("/").text)
    assert {"Organization", "WebSite"} <= home
    faq = _jsonld_types(http.get("/faq/").text)
    assert "FAQPage" in faq
    audit = _jsonld_types(http.get("/audit/").text)
    assert "FAQPage" in audit
    assert "Service" in audit or "Offer" in audit


@pytest.mark.risk_low
@pytest.mark.integration
@pytest.mark.req("REQ-INT-03")
def test_homepage_stylesheet_is_served(http: PoliteClient, sut_url: str) -> None:
    html = http.get("/").text
    match = re.search(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html)
    assert match, "homepage did not reference a stylesheet"
    response, final = http.get_followed(match.group(1))
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")
    assert urlparse(final).scheme == "https" or urlparse(sut_url).scheme != "https"
