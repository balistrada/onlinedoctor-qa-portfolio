"""Rebuild the matrix and the release report from reports/results.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qa_portfolio.config import DEFECTS_FILE, REQUIREMENTS_FILE, load_yaml
from qa_portfolio.reporting.render import write_reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild QA reports from results.json")
    parser.add_argument("--results", type=Path, default=Path("reports/results.json"))
    parser.add_argument("--outdir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    payload = json.loads(args.results.read_text(encoding="utf-8"))
    meta = payload.get("meta") or {}
    written = write_reports(
        tests=payload.get("tests") or [],
        requirements=load_yaml(REQUIREMENTS_FILE).get("requirements", []),
        defects=load_yaml(DEFECTS_FILE).get("defects", []),
        outdir=args.outdir,
        meta=meta,
    )
    print(json.dumps({"decision": written["decision"]["decision"], **{
        key: written[key] for key in ("matrix_md", "release_md")
    }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
