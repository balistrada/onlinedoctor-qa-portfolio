from qa_portfolio.reporting.decision import decide

REQS = [
    {
        "id": "REQ-HIGH",
        "title": "Zahlung",
        "risk": "high",
        "automation": "automated",
    },
    {
        "id": "REQ-MED",
        "title": "Sitemap",
        "risk": "medium",
        "automation": "automated",
    },
    {
        "id": "REQ-MAN",
        "title": "Checkliste",
        "risk": "medium",
        "automation": "manual",
        "evidence": "docs/08-manuelle-regression.md",
    },
    {
        "id": "REQ-NA",
        "title": "Rollen",
        "risk": "high",
        "automation": "na",
        "na_reason": "kein Login",
    },
]


def _test(req: str, outcome: str, risk: str = "high", reason: str | None = None) -> dict:
    return {
        "nodeid": f"tests/test_{req}.py::test",
        "outcome": outcome,
        "risk": risk,
        "requirements": [req],
        "reason": reason,
    }


def test_full_green_run_is_go() -> None:
    report = decide(
        [_test("REQ-HIGH", "passed"), _test("REQ-MED", "passed", risk="medium")],
        REQS,
        [],
        scope="full",
    )
    assert report["decision"] == "GO"
    assert report["functional_decision"] == "GO"
    assert report["weighted_pass_rate"] == 1


def test_high_failure_is_no_go_even_on_a_partial_run() -> None:
    report = decide(
        [_test("REQ-HIGH", "failed")],
        REQS,
        [],
        scope="quality-gate",
    )
    assert report["decision"] == "NO-GO"
    assert report["functional_decision"] == "NO-GO"


def test_high_xfail_is_no_go() -> None:
    report = decide(
        [_test("REQ-HIGH", "xfailed", reason="DEF-SEC-99 still broken")],
        REQS,
        [{"id": "DEF-SEC-99", "title": "x", "risk": "high", "status": "open"}],
        scope="full",
    )
    assert report["decision"] == "NO-GO"


def test_medium_xfail_on_a_full_run_is_conditional() -> None:
    report = decide(
        [
            _test("REQ-HIGH", "passed"),
            _test("REQ-MED", "xfailed", risk="medium", reason="DEF-SEC-01 headers missing"),
        ],
        REQS,
        [{"id": "DEF-SEC-01", "title": "Header", "risk": "medium", "status": "open"}],
        scope="full",
    )
    assert report["decision"] == "CONDITIONAL"
    assert report["functional_decision"] == "GO"


def test_uncovered_high_requirement_is_no_go_only_for_the_full_scope() -> None:
    report = decide([], REQS, [], scope="full")
    assert report["decision"] == "NO-GO"
    partial = decide([], REQS, [], scope="quality-gate")
    assert partial["decision"] == "INCOMPLETE"


def test_partial_green_run_is_not_a_release_go() -> None:
    report = decide([_test("REQ-HIGH", "passed")], REQS, [], scope="quality-gate")
    assert report["decision"] == "INCOMPLETE"
    assert report["functional_decision"] == "GO"


def test_xfail_without_defect_id_is_conditional() -> None:
    report = decide(
        [
            _test("REQ-HIGH", "passed"),
            _test("REQ-MED", "xfailed", risk="medium", reason="just broken"),
        ],
        REQS,
        [],
        scope="full",
    )
    assert report["decision"] == "CONDITIONAL"


def test_a11y_style_defect_ids_count_as_managed() -> None:
    report = decide(
        [
            _test("REQ-HIGH", "passed"),
            _test(
                "REQ-MED",
                "xfailed",
                risk="medium",
                reason="DEF-A11Y-01: language switch",
            ),
        ],
        REQS,
        [{"id": "DEF-A11Y-01", "title": "Name", "risk": "medium", "status": "open"}],
        scope="full",
    )
    assert report["decision"] == "CONDITIONAL"
    assert not any("ohne DEF-ID" in reason for reason in report["reasons"])


def test_manual_and_na_are_not_automation_gaps() -> None:
    report = decide(
        [_test("REQ-HIGH", "passed"), _test("REQ-MED", "passed", risk="medium")],
        REQS,
        [],
        scope="full",
    )
    assert report["gaps"] == []
