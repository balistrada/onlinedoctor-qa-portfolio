"""Playwright route guard. Keeps browser tests from posting or checking out."""

from __future__ import annotations

from urllib.parse import urlparse

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
BLOCKED_HOSTS = (
    "buy.stripe.com",
    "checkout.stripe.com",
    "billing.stripe.com",
    "static.cloudflareinsights.com",
)


def install_guard(context, host: str) -> None:
    """Abort unsafe methods on the system under test and a few off-limits hosts.

    GET/HEAD of public pages still proceed. A test may register a more specific
    route afterwards; Playwright checks the latest route first.
    """

    def handler(route) -> None:
        request = route.request
        parsed = urlparse(request.url)
        method = request.method.upper()
        if method in UNSAFE_METHODS and parsed.hostname == host:
            route.abort()
            return
        if parsed.hostname in BLOCKED_HOSTS:
            route.abort()
            return
        route.continue_()

    context.route("**/*", handler)
