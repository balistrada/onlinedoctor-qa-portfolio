"""Build a small index for GitHub Pages from whatever report files were produced."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports"
TARGET = ROOT / "reports" / "pages"


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    links = []
    for name in (
        "release-readiness.html",
        "traceability.html",
        "release-readiness.md",
        "traceability.md",
        "pytest-gate.html",
        "pytest-unit.html",
    ):
        source = SOURCE / name
        if not source.exists():
            continue
        shutil.copy(source, TARGET / name)
        links.append(f'<li><a href="{name}">{name}</a></li>')
    if not links:
        links.append("<li>Keine Berichte in diesem Lauf.</li>")
    (TARGET / "index.html").write_text(
        """<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><title>veryops QA-Berichte</title></head>
<body>
<h1>veryops QA-Berichte</h1>
<p>Erzeugt aus einem manuellen Volllauf. Kein Zeitplan, keine Nachtmails.</p>
<ul>
"""
        + "\n".join(links)
        + """
</ul>
</body></html>
""",
        encoding="utf-8",
    )
    print(TARGET / "index.html")


if __name__ == "__main__":
    main()
