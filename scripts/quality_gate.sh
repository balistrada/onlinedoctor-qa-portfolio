#!/usr/bin/env bash
# Fast gate: ruff, the report widget when present, unit tests, high-risk product tests.
# A missing high-risk selection (exit 5) is success on a branch that has no product tests yet.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
ruff check .
if [[ -f frontend/report-summary/package-lock.json ]]; then
  npm ci --prefix frontend/report-summary
  npm test --prefix frontend/report-summary
fi
export QA_RUN_SCOPE="${QA_RUN_SCOPE:-quality-gate}"
pytest tests/unit -q \
  --junitxml=reports/junit-unit.xml \
  --html=reports/pytest-unit.html --self-contained-html
set +e
pytest -m "risk_high and not quarantine and not a11y" \
  --browser "${BROWSER:-chromium}" \
  --junitxml=reports/junit-gate.xml \
  --html=reports/pytest-gate.html --self-contained-html \
  --alluredir=reports/allure-results
code=$?
set -e
if [[ "$code" -ne 0 && "$code" -ne 5 ]]; then
  exit "$code"
fi
