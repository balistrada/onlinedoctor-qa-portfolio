.PHONY: gate full-chromium

gate:
	bash scripts/quality_gate.sh

full-chromium:
	QA_RUN_SCOPE=full pytest tests/unit tests/api tests/integration tests/e2e tests/a11y \
	  -m "not quarantine" --browser chromium \
	  --html=reports/pytest-full.html --self-contained-html \
	  --junitxml=reports/junit-full.xml
