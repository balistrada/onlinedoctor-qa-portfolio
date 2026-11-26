"""Serial, cached HTTP client for read-only checks against a live site."""

from __future__ import annotations

import threading
import time
from urllib.parse import urljoin, urlparse

import httpx

from qa_portfolio.config import USER_AGENT


class PoliteClient:
    """GET/HEAD/OPTIONS with a minimum gap and a session cache of 200 responses.

    Nothing in this client sends a body. Callers that need a redirect chain use
    ``get_followed`` and stop if a hop leaves HTTPS.
    """

    def __init__(self, base_url: str, min_interval: float = 0.35) -> None:
        self.base_url = base_url.rstrip("/")
        self.host = urlparse(self.base_url).netloc
        self.min_interval = min_interval
        self.network_requests = 0
        self._last = 0.0
        self._lock = threading.Lock()
        self._cache: dict[str, httpx.Response] = {}
        # Bind IPv4. Happy-eyeballs to Cloudflare's AAAA records stalled
        # once from this network and burned the whole timeout.
        self.client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=False,
            transport=httpx.HTTPTransport(local_address="0.0.0.0", retries=1),
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

    def close(self) -> None:
        self.client.close()

    def _absolute(self, url: str) -> str:
        if url.startswith(("http://", "https://")):
            return url
        if not url.startswith("/"):
            url = "/" + url
        return self.base_url + url

    def _pace(self) -> None:
        with self._lock:
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def request(
        self,
        method: str,
        url: str,
        *,
        cache: bool = True,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        method = method.upper()
        if method not in {"GET", "HEAD", "OPTIONS"}:
            raise ValueError(f"Refusing method {method}; this client is read-only")
        absolute = self._absolute(url)
        # Extra headers change the body (Cloudflare injects the analytics
        # beacon for browser user agents), so they never share the cache.
        key = f"{method} {absolute}"
        if cache and method == "GET" and headers is None and key in self._cache:
            return self._cache[key]
        self._pace()
        self.network_requests += 1
        response = self.client.request(method, absolute, headers=headers)
        if cache and method == "GET" and response.status_code == 200:
            self._cache[key] = response
        return response

    def get(
        self,
        url: str,
        *,
        cache: bool = True,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("GET", url, cache=cache, headers=headers)

    def get_followed(self, url: str, *, max_hops: int = 4) -> tuple[httpx.Response, str]:
        current = self._absolute(url)
        response = self.get(current)
        for _ in range(max_hops):
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response, current
            location = response.headers.get("location")
            if not location:
                return response, current
            current = urljoin(current, location)
            response = self.get(current, cache=False)
        return response, current
