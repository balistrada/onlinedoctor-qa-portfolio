"""Shared fixtures. Product tests must carry risk, level, and requirement markers."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
import yaml

from qa_portfolio.config import host_of, resolve_base_url
from qa_portfolio.http import PoliteClient
from qa_portfolio.safety import install_guard

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "site.yml"

RISKS = {"risk_high", "risk_medium", "risk_low"}
LEVELS = {"api", "integration", "e2e", "a11y", "security", "visual"}


def pytest_configure(config: pytest.Config) -> None:
    if not getattr(config.option, "base_url", None):
        config.option.base_url = resolve_base_url()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    errors = []
    for item in items:
        if "unit" in Path(str(item.path)).parts:
            continue
        names = {mark.name for mark in item.iter_markers()}
        if len(names & RISKS) != 1:
            errors.append(f"{item.nodeid} needs exactly one of {sorted(RISKS)}")
        if not (names & LEVELS):
            errors.append(f"{item.nodeid} needs a level marker {sorted(LEVELS)}")
        if not any(mark.name == "req" and mark.args for mark in item.iter_markers("req")):
            errors.append(f"{item.nodeid} needs @pytest.mark.req('REQ-...')")
    if errors:
        raise pytest.UsageError("Marker contract:\n" + "\n".join(errors))


@pytest.fixture(scope="session")
def sut_url() -> str:
    return resolve_base_url()


@pytest.fixture(scope="session")
def site() -> dict:
    with DATA.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="session")
def http(sut_url: str, pytestconfig: pytest.Config) -> PoliteClient:
    interval = float(os.environ.get("REQUEST_INTERVAL_SECONDS", "0.35"))
    client = PoliteClient(sut_url, min_interval=interval)
    pytestconfig._qa_http = client  # type: ignore[attr-defined]
    yield client
    client.close()


@pytest.fixture(autouse=True)
def _guard_browser_and_pace(request: pytest.FixtureRequest, sut_url: str):
    if "page" in request.fixturenames:
        page = request.getfixturevalue("page")
        page.set_default_timeout(10_000)
        page.set_default_navigation_timeout(20_000)
        install_guard(page.context, host_of(sut_url))
    yield
    names = {mark.name for mark in request.node.iter_markers()}
    if names & {"e2e", "a11y"}:
        time.sleep(float(os.environ.get("E2E_PACE_SECONDS", "0.35")))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.qa_rep = report  # type: ignore[attr-defined]
    elif report.when == "setup" and report.outcome != "passed":
        item.qa_rep = report  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    try:
        from qa_portfolio.reporting.session import write_session_reports
    except ImportError:
        return
    try:
        write_session_reports(session)
    except Exception as exc:  # reporting must not hide a test result
        print(f"\n[qa] report generation failed: {exc}")
