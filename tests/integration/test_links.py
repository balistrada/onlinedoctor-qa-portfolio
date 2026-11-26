"""Sitemap URLs and same-origin links. Serial, cached, no third parties."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import pytest

from qa_portfolio.http import PoliteClient

pytestmark = pytest.mark.integration

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class _Anchors(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._skip += 1
        if self._skip:
            return
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip:
            self._skip -= 1


def _locs(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    return [node.text.strip() for node in root.findall(".//sm:loc", SITEMAP_NS) if node.text]


@pytest.mark.risk_high
@pytest.mark.req("REQ-INT-01")
@pytest.mark.req("REQ-HTTP-04")
def test_every_sitemap_url_resolves(http: PoliteClient, site: dict, sut_url: str) -> None:
    index = http.get("/sitemap-index.xml")
    assert index.status_code == 200
    children = _locs(index.text)
    assert children
    pages: list[str] = []
    for child in children:
        response = http.get(child)
        assert response.status_code == 200, child
        pages.extend(_locs(response.text))
    assert pages
    paths = {urlparse(url).path or "/" for url in pages}
    missing = [path for path in site["core_paths"] if path not in paths]
    assert missing == []
    for url in pages:
        response, final = http.get_followed(url)
        assert response.status_code == 200, url
        if urlparse(sut_url).scheme == "https":
            assert urlparse(final).scheme == "https", final


@pytest.mark.risk_medium
@pytest.mark.req("REQ-INT-02")
def test_internal_links_on_key_pages_resolve(http: PoliteClient, site: dict, sut_url: str) -> None:
    host = urlparse(sut_url).netloc
    seen: set[str] = set()
    for path in site["key_pages"]:
        page = http.get(path)
        assert page.status_code == 200, path
        parser = _Anchors()
        parser.feed(page.text)
        for href in parser.hrefs:
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            absolute = urljoin(sut_url + path, href)
            parsed = urlparse(absolute)
            if parsed.netloc != host:
                continue
            if parsed.path.startswith("/cdn-cgi/"):
                continue
            target = parsed._replace(fragment="").geturl()
            seen.add(target)
    assert seen
    for target in sorted(seen):
        response, final = http.get_followed(target)
        assert response.status_code == 200, target
        if urlparse(sut_url).scheme == "https":
            assert urlparse(final).scheme == "https", final
