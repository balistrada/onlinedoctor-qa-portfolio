import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _catalog() -> list[dict]:
    data = yaml.safe_load((ROOT / "requirements" / "catalog.yml").read_text(encoding="utf-8"))
    return data["requirements"]


def _defects() -> list[dict]:
    data = yaml.safe_load((ROOT / "defects" / "register.yml").read_text(encoding="utf-8"))
    return data["defects"]


def test_requirement_ids_are_unique_and_complete() -> None:
    rows = _catalog()
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    for row in rows:
        assert row["risk"] in {"high", "medium", "low"}
        assert row["automation"] in {"automated", "manual", "na"}
        assert row.get("statement")
        if row["automation"] == "na":
            assert row.get("na_reason")
        if row["automation"] == "manual":
            assert row.get("evidence")
            assert (ROOT / row["evidence"].split("#")[0]).exists()


def test_open_defects_point_at_real_requirements() -> None:
    known = {row["id"] for row in _catalog()}
    for defect in _defects():
        assert defect["id"].startswith("DEF-")
        assert defect["risk"] in {"high", "medium", "low"}
        assert defect["status"] in {"open", "closed"}
        for req_id in defect["requirements"]:
            assert req_id in known


def test_automated_requirements_are_referenced_by_a_test() -> None:
    tree = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "tests").rglob("*.py")
        if "unit" not in path.parts
    )
    missing = [
        row["id"]
        for row in _catalog()
        if row["automation"] == "automated" and row["id"] not in tree
    ]
    assert missing == []


def test_ci_workflows_exist_and_have_no_schedule() -> None:
    workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        assert "schedule" not in text
        assert "cron" not in text
        yaml.safe_load(text)
    circle = (ROOT / ".circleci" / "config.yml").read_text(encoding="utf-8")
    assert "cron" not in circle
    assert "schedule" not in circle
    yaml.safe_load(circle)


def test_xfail_reasons_cite_a_defect() -> None:
    pattern = re.compile(r"xfail\([^)]*reason=\"([^\"]+)\"", re.S)
    cited = []
    for path in (ROOT / "tests").rglob("*.py"):
        cited.extend(pattern.findall(path.read_text(encoding="utf-8")))
    assert cited, "expected the known product gaps to be marked xfail"
    for reason in cited:
        assert "DEF-" in reason
