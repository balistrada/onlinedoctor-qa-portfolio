# Abbildung der Stellenanforderung

Stelle: Senior QA Engineer (80–100 %) bei OnlineDoctor,
[Ausschreibung](https://jobs.startup-insider.com/unternehmen/onlinedoctor/jobs/senior-qa-engineer-80-100-fmd).

| Anforderung der Stelle | Wo in diesem Repository | Nachweis |
| --- | --- | --- |
| Risikoorientierte Teststrategie, Abdeckungsziele, Lücken, Empfehlung zur Release-Reife | `docs/01-teststrategie.md`, `docs/02-risikoanalyse.md`, `docs/06-reporting-und-release-readiness.md` | Katalog plus `decide()`; voller Lauf liefert GO / CONDITIONAL / NO-GO |
| Exploratives Testen und manuelle Regression | `docs/07-exploratives-testen.md`, `docs/08-manuelle-regression.md` | Ausgeführte Session vom 26. November 2026, Checkliste, offene Chartas |
| Automatisierte API-, Integrations- und E2E-Tests in CI | `tests/api`, `tests/integration`, `tests/e2e`, `.github/workflows/quality-gate.yml` | PR-Gate: ruff, Jest, Hochrisiko-Teilmenge auf Chromium. Volllauf manuell |
| Testumgebungen, Testdaten, Reporting | `docs/05-testumgebungen-und-testdaten.md`, `config/environments.yml`, `tests/data/site.yml`, pytest-html, JUnit, Allure-Rohdaten | `BASE_URL` / `TEST_ENV`, Platzhalter für Staging, ohne erfundene Umgebung |
| Traceability Anforderung → Test → Ergebnis → Defect → Evidenz | `docs/04-traceability.md`, `requirements/catalog.yml`, `defects/register.yml`, `.github/ISSUE_TEMPLATE/defect.md` | Matrix als Markdown und HTML, aus Markern und Ergebnissen erzeugt |
| Web auf Desktop und mobil, Authentifizierung und Rechte, Fehlerfälle | `tests/e2e`, `tests/a11y`, `tests/api/test_auth_surface.py`, `tests/e2e/test_error_paths.py` | Chromium, Firefox, WebKit, Pixel 7, iPhone 15. Kein Login auf der Fläche: Negativprobe und N/A, kein erfundener Rollen-Test |
| Python, pytest, Playwright | gesamte Suite | eine Sprache, drei Browser |
| CircleCI | `.circleci/config.yml` | Gate immer, Volllauf nur mit Parameter `run_full` |
| React, Jest | `frontend/report-summary/` | beschriftet als lokales Beispiel, nicht als SUT |
| KI im Testing, mit Grenzen | `docs/09-ki-im-testing.md`, `qa_portfolio/ai_review/` | Review-Liste, Prompt-Vorlagen, Heuristik ohne Modell, Abschnitt was geprüft wurde |
| Kein AWS | — | nicht verwendet, in der Tool-Auswahl begründet |
| Keine nächtlichen Läufe | beide Workflows, CircleCI | kein `schedule`, kein Cron; der Unit-Test `test_ci_workflows_exist_and_have_no_schedule` bewacht das |

Die frühen Einbindung beim Product Owner, das Coaching der Entwickler und
die Arbeit am echten Medizinprodukt kann eine Mappe nicht vorführen. Sie
kann zeigen, wie die Unterlagen aussehen, mit denen ich in so ein Team
gehen würde: Risiko begründet, Lücken benannt, Tests an Anforderungen
gehängt, Freigabe als Satz und nicht als Ampel.
