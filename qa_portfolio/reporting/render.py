"""Write the traceability matrix and the release report as Markdown and HTML."""

from __future__ import annotations

import html
from collections import defaultdict
from pathlib import Path

from qa_portfolio.reporting.decision import decide


def write_reports(
    *,
    tests: list[dict],
    requirements: list[dict],
    defects: list[dict],
    outdir: Path,
    meta: dict,
) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    scope = str(meta.get("scope") or "adhoc")
    decision = decide(tests, requirements, defects, scope=scope)
    matrix_rows = _matrix_rows(tests, requirements, defects)

    matrix_md = outdir / "traceability.md"
    matrix_html = outdir / "traceability.html"
    release_md = outdir / "release-readiness.md"
    release_html = outdir / "release-readiness.html"

    matrix_md.write_text(_matrix_markdown(matrix_rows, meta), encoding="utf-8")
    matrix_html.write_text(_matrix_html(matrix_rows, meta), encoding="utf-8")
    release_md.write_text(_release_markdown(decision, meta), encoding="utf-8")
    release_html.write_text(_release_html(decision, meta), encoding="utf-8")
    return {
        "decision": decision,
        "matrix_md": str(matrix_md),
        "matrix_html": str(matrix_html),
        "release_md": str(release_md),
        "release_html": str(release_html),
    }


def _matrix_rows(tests: list[dict], requirements: list[dict], defects: list[dict]) -> list[dict]:
    by_req: dict[str, list[dict]] = defaultdict(list)
    for test in tests:
        for req_id in test.get("requirements") or []:
            by_req[req_id].append(test)
    defects_by_req: dict[str, list[dict]] = defaultdict(list)
    for defect in defects:
        for req_id in defect.get("requirements") or []:
            defects_by_req[req_id].append(defect)

    rows = []
    for req in requirements:
        linked = by_req.get(req["id"], [])
        outcomes = sorted({test.get("outcome", "not_run") for test in linked}) or ["—"]
        defect_bits = []
        for defect in defects_by_req.get(req["id"], []):
            issue = defect.get("github_issue") or "template:.github/ISSUE_TEMPLATE/defect.md"
            defect_bits.append(f"{defect['id']} ({defect.get('status')}, {issue})")
        if req.get("automation") == "manual":
            coverage = "manuell"
        elif req.get("automation") == "na":
            coverage = "n/a"
        elif not linked:
            coverage = "lücke"
        elif "failed" in outcomes or "error" in outcomes:
            coverage = "fehlgeschlagen"
        elif "xfailed" in outcomes:
            coverage = "bekannt-offen"
        else:
            coverage = "automatisiert"
        evidence = []
        if req.get("evidence"):
            evidence.append(req["evidence"])
        evidence.extend(test["nodeid"] for test in linked)
        rows.append(
            {
                "id": req["id"],
                "title": req.get("title", ""),
                "risk": req.get("risk", ""),
                "automation": req.get("automation", ""),
                "coverage": coverage,
                "outcomes": ", ".join(outcomes),
                "tests": ", ".join(test["nodeid"] for test in linked) or "—",
                "defects": "; ".join(defect_bits) or "—",
                "evidence": "; ".join(evidence) or "—",
            }
        )
    return rows


def _matrix_markdown(rows: list[dict], meta: dict) -> str:
    lines = [
        "# Traceability-Matrix",
        "",
        f"- Lauf: `{meta.get('scope', 'adhoc')}`",
        f"- Basis-URL: `{meta.get('base_url', '')}`",
        f"- Commit: `{meta.get('git_sha', 'unbekannt')}`",
        f"- Zeitpunkt: {meta.get('generated_at', '')}",
        "",
        "| Anforderung | Risiko | Abdeckung | Ergebnis | Tests | Defect | Evidenz |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        cells = {key: _md(row[key]) for key in row}
        line = (
            "| {id} {title} | {risk} | {coverage} | {outcomes} "
            "| {tests} | {defects} | {evidence} |"
        ).format(**cells)
        lines.append(line)
    lines.append("")
    return "\n".join(lines)


def _release_markdown(decision: dict, meta: dict) -> str:
    percent = f"{decision['weighted_pass_rate'] * 100:.1f} %"
    lines = [
        "# Release-Readiness",
        "",
        f"**Empfehlung: {decision['decision']}**",
        "",
        f"- Funktional: {decision['functional_decision']}",
        f"- Gewichtete Pass-Rate: {percent}",
        f"- Scope: `{decision['scope']}`",
        f"- Basis-URL: `{meta.get('base_url', '')}`",
        f"- Commit: `{meta.get('git_sha', 'unbekannt')}`",
        (
            f"- Ausführungen: {decision['executed']}, bestanden: {decision['passed']}, "
            f"fehlgeschlagen: {decision['failed']}, xfail: {decision['xfailed']}, "
            f"xpass: {decision['xpassed']}"
        ),
        "",
        "## Begründung",
        "",
    ]
    lines.extend(f"- {reason}" for reason in decision["reasons"])
    if decision["open_defects"]:
        lines.extend(["", "## Offene Defects", ""])
        for defect in decision["open_defects"]:
            lines.append(f"- {defect['id']} ({defect['risk']}): {defect['title']}")
    if decision["gaps"]:
        lines.extend(["", "## Deckungslücken", ""])
        for gap in decision["gaps"]:
            lines.append(f"- {gap['id']} ({gap['risk']}): {gap['gap']}")
    lines.extend(
        [
            "",
            "Maßstab: kein unerwarteter Fehlschlag, kein offenes hohes Risiko, "
            "keine ungedeckte Hochrisiko-Anforderung. Mittlere offene Punkte "
            "ergeben CONDITIONAL, niedrige bleiben als Notiz unter GO. "
            "Ein Teillauf wird nie als GO oder CONDITIONAL ausgegeben.",
            "",
        ]
    )
    return "\n".join(lines)


def _matrix_html(rows: list[dict], meta: dict) -> str:
    body = "\n".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key in (
            "id", "title", "risk", "coverage", "outcomes", "tests", "defects", "evidence"
        ))
        + "</tr>"
        for row in rows
    )
    return _page(
        "Traceability",
        f"<p>Lauf {html.escape(str(meta.get('scope', '')))} · "
        f"{html.escape(str(meta.get('base_url', '')))} · "
        f"{html.escape(str(meta.get('git_sha', '')))}</p>"
        "<table><thead><tr>"
        "<th>ID</th><th>Anforderung</th><th>Risiko</th><th>Abdeckung</th>"
        "<th>Ergebnis</th><th>Tests</th><th>Defect</th><th>Evidenz</th>"
        f"</tr></thead><tbody>{body}</tbody></table>",
    )


def _release_html(decision: dict, meta: dict) -> str:
    reasons = "".join(f"<li>{html.escape(reason)}</li>" for reason in decision["reasons"])
    defects = "".join(
        f"<li>{html.escape(item['id'])} ({html.escape(str(item['risk']))}): "
        f"{html.escape(str(item['title']))}</li>"
        for item in decision["open_defects"]
    )
    percent = f"{decision['weighted_pass_rate'] * 100:.1f} %"
    klass = html.escape(decision["decision"]).lower()
    return _page(
        "Release-Readiness",
        f"<p class='decision {klass}'>{html.escape(decision['decision'])}</p>"
        f"<p>Funktional: {html.escape(decision['functional_decision'])} · "
        f"gewichtete Pass-Rate {percent} · Scope {html.escape(decision['scope'])}</p>"
        f"<p>{html.escape(str(meta.get('base_url', '')))} · "
        f"{html.escape(str(meta.get('git_sha', '')))}</p>"
        f"<ul>{reasons}</ul>"
        + (f"<h2>Offene Defects</h2><ul>{defects}</ul>" if defects else ""),
    )


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body {{ font: 16px/1.45 system-ui, sans-serif; margin: 2rem; color: #14202b; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d5dde4; padding: 0.4rem 0.5rem; vertical-align: top; }}
th {{ background: #f3f6f8; text-align: left; }}
.decision {{ font-size: 2rem; font-weight: 700; }}
.no-go {{ color: #9d174d; }}
.conditional {{ color: #9a6700; }}
.go {{ color: #17663a; }}
.incomplete {{ color: #1d4e89; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
{body}
</body>
</html>
"""


def _md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
