"""Collect pytest results and write the reports at session end."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from qa_portfolio.config import DEFECTS_FILE, REQUIREMENTS_FILE, load_yaml, resolve_base_url
from qa_portfolio.reporting.render import write_reports

ROOT = Path(__file__).resolve().parents[2]


def classify_report(report) -> str:
    wasxfail = getattr(report, "wasxfail", None)
    if report.passed and wasxfail:
        return "xpassed"
    if report.skipped and wasxfail:
        return "xfailed"
    if report.passed:
        return "passed"
    if report.skipped:
        return "skipped"
    if report.failed:
        return "failed"
    return str(getattr(report, "outcome", "error"))


def result_from_item(item) -> dict:
    report = getattr(item, "qa_rep", None)
    outcome = classify_report(report) if report is not None else "not_run"
    marks = {mark.name for mark in item.iter_markers()}
    risk_marks = ("risk_high", "risk_medium", "risk_low")
    risk = next((name.removeprefix("risk_") for name in risk_marks if name in marks), "unknown")
    levels = sorted(marks & {"api", "integration", "e2e", "a11y", "security", "visual"})
    requirements = []
    for mark in item.iter_markers("req"):
        requirements.extend(str(arg) for arg in mark.args)
    reason = None
    if report is not None and outcome in {"failed", "error", "xfailed", "xpassed"}:
        reason = getattr(report, "wasxfail", None) or _short_repr(report)
    return {
        "nodeid": item.nodeid,
        "outcome": outcome,
        "risk": risk,
        "levels": levels,
        "requirements": requirements,
        "duration_s": round(getattr(report, "duration", 0.0) or 0.0, 4),
        "quarantine": "quarantine" in marks,
        "reason": reason,
    }


def write_session_reports(session) -> None:
    tests = [result_from_item(item) for item in session.items]
    requirements = load_yaml(REQUIREMENTS_FILE).get("requirements", [])
    defects = load_yaml(DEFECTS_FILE).get("defects", [])
    meta = _meta(session)
    client = getattr(session.config, "_qa_http", None)
    if client is not None:
        meta["network_requests"] = client.network_requests
    payload = {"meta": meta, "tests": tests}
    outdir = ROOT / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_reports(
        tests=tests,
        requirements=requirements,
        defects=defects,
        outdir=outdir,
        meta=meta,
    )


def _meta(session) -> dict:
    try:
        base_url = resolve_base_url()
    except Exception as exc:  # a unit session can still report
        base_url = f"unresolved ({exc})"
    return {
        "scope": os.environ.get("QA_RUN_SCOPE", "adhoc"),
        "base_url": base_url,
        "git_sha": _git_sha(),
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pytest_exitstatus": getattr(session, "exitstatus", None),
    }


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unbekannt"


def _short_repr(report) -> str:
    text = str(getattr(report, "longrepr", "") or "")
    text = " ".join(text.split())
    return text[:500]
