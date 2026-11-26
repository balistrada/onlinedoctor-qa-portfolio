"""Turn a pytest session plus the catalogs into a release recommendation.

Decision bar (documented in docs/06-reporting-und-release-readiness.md):

- NO-GO: an unexpected failure, a high-risk xfail, an open high defect,
  or a high requirement with neither a test nor an explicit N/A.
- CONDITIONAL: no NO-GO, but an open or unmanaged medium residual,
  a medium/low gap, or a partial scope that still has medium residuals.
- GO: full scope, no medium-or-higher residual, coverage complete.
- INCOMPLETE: a partial run (quality gate, unit) that did not earn NO-GO.
  It is not a release decision.

``functional_decision`` ignores accepted xfails and open defects. It is GO
when every executed test passed or was an accepted xfail/skip.
"""

from __future__ import annotations

import re
from collections import defaultdict

WEIGHT = {"high": 5, "medium": 3, "low": 1}
DEFECT_ID = re.compile(r"DEF-[A-Z0-9]+-\d+")


def decide(
    tests: list[dict],
    requirements: list[dict],
    defects: list[dict],
    *,
    scope: str,
) -> dict:
    executed = [test for test in tests if test.get("outcome") not in {"skipped", "not_run"}]
    failures = [test for test in executed if test.get("outcome") in {"failed", "error"}]
    xfails = [test for test in executed if test.get("outcome") == "xfailed"]
    xpasses = [test for test in executed if test.get("outcome") == "xpassed"]
    passed = [test for test in executed if test.get("outcome") in {"passed", "xpassed"}]

    weight_exec = sum(WEIGHT.get(test.get("risk", "low"), 1) for test in executed)
    weight_pass = sum(WEIGHT.get(test.get("risk", "low"), 1) for test in passed)
    rate = (weight_pass / weight_exec) if weight_exec else 1.0

    by_req: dict[str, list[dict]] = defaultdict(list)
    for test in tests:
        for req_id in test.get("requirements") or []:
            by_req[req_id].append(test)

    open_defects = [item for item in defects if item.get("status") == "open"]
    open_by_risk = _count_risk(open_defects)

    unmanaged = [
        test
        for test in xfails
        if not DEFECT_ID.search(test.get("reason") or "")
    ]
    high_xfail = [test for test in xfails if test.get("risk") == "high"]
    medium_xfail = [test for test in xfails if test.get("risk") == "medium"]

    # Coverage is a property of the whole suite. A quality-gate session only
    # contains the high-risk subset, so it must not treat missing medium
    # tests as release gaps. The unit test
    # tests/unit/test_catalog.py locks the static link from requirement to test.
    gaps = []
    if scope == "full":
        for req in requirements:
            automation = req.get("automation")
            linked = [
                test
                for test in by_req.get(req["id"], [])
                if test.get("outcome") not in {"not_run"}
            ]
            if automation == "na":
                continue
            if automation == "manual":
                if not req.get("evidence"):
                    gaps.append({**req, "gap": "manual-ohne-evidenz"})
                continue
            if not linked:
                gaps.append({**req, "gap": "kein-test"})

    high_gaps = [gap for gap in gaps if gap.get("risk") == "high"]
    other_gaps = [gap for gap in gaps if gap.get("risk") != "high"]

    reasons: list[str] = []
    decision = "GO"

    if failures:
        decision = "NO-GO"
        reasons.append(
            f"{len(failures)} unerwartete Fehlschläge, davon "
            f"{sum(1 for test in failures if test.get('risk') == 'high')} mit hohem Risiko."
        )
    if high_xfail:
        decision = "NO-GO"
        reasons.append(
            f"{len(high_xfail)} erwartete Fehlschläge mit hohem Risiko "
            "(xfail). Ein bekanntes Hochrisiko ist kein GO."
        )
    if scope == "full" and open_by_risk.get("high"):
        decision = "NO-GO"
        reasons.append(
            f"{open_by_risk['high']} offene Defects mit hohem Risiko im Register."
        )
    if scope == "full" and high_gaps:
        decision = "NO-GO"
        reasons.append(
            "Hochrisiko-Anforderungen ohne automatisierten Test und ohne N/A: "
            + ", ".join(gap["id"] for gap in high_gaps)
        )

    conditional_bits: list[str] = []
    if scope == "full" and open_by_risk.get("medium"):
        conditional_bits.append(
            f"{open_by_risk['medium']} offene Defects mit mittlerem Risiko"
        )
    if medium_xfail:
        conditional_bits.append(f"{len(medium_xfail)} xfail mit mittlerem Risiko")
    if unmanaged:
        conditional_bits.append(
            f"{len(unmanaged)} xfail ohne DEF-ID (nicht im Register verankert)"
        )
    if other_gaps:
        conditional_bits.append(
            "Lücken bei mittlerem oder niedrigem Risiko: "
            + ", ".join(gap["id"] for gap in other_gaps)
        )
    if xpasses:
        conditional_bits.append(
            f"{len(xpasses)} xpass: ein erwarteter Fehlschlag ist verschwunden, "
            "das xfail sollte entfernt werden"
        )

    if decision != "NO-GO" and conditional_bits:
        decision = "CONDITIONAL"
        reasons.extend(conditional_bits)

    if decision == "GO" and scope == "full" and open_by_risk.get("low"):
        reasons.append(
            f"{open_by_risk['low']} offene Defects mit niedrigem Risiko bleiben "
            "als akzeptierte Restpunkte im Bericht."
        )

    if not reasons and decision == "GO":
        if scope == "full":
            reasons.append(
                "Keine unerwarteten Fehlschläge und keine offenen mittleren "
                "oder hohen Defects."
            )
        else:
            reasons.append("In diesem Teillauf kein unerwarteter Fehlschlag.")

    functional = "NO-GO" if failures else "GO"
    if scope != "full" and decision != "NO-GO":
        reasons.insert(
            0,
            "Teillauf ("
            + scope
            + "): keine Release-Freigabe. GO oder CONDITIONAL gibt es nur "
            "aus dem vollständigen workflow_dispatch-Lauf.",
        )
        decision = "INCOMPLETE"

    return {
        "decision": decision,
        "functional_decision": functional,
        "scope": scope,
        "weighted_pass_rate": round(rate, 4),
        "executed": len(executed),
        "passed": len([test for test in executed if test.get("outcome") == "passed"]),
        "failed": len(failures),
        "xfailed": len(xfails),
        "xpassed": len(xpasses),
        "reasons": reasons,
        "gaps": [{"id": gap["id"], "gap": gap["gap"], "risk": gap.get("risk")} for gap in gaps],
        "open_defects": [
            {"id": item["id"], "risk": item.get("risk"), "title": item.get("title")}
            for item in open_defects
        ],
    }


def _count_risk(items: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        counts[item.get("risk", "medium")] += 1
    return counts
