# QA-Portfolio — Senior QA Engineer

[![Quality gate](https://github.com/balistrada/onlinedoctor-qa-portfolio/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/balistrada/onlinedoctor-qa-portfolio/actions/workflows/quality-gate.yml)

Bewerbungsmappe von Palma für
[Senior QA Engineer (80–100 %) bei OnlineDoctor](https://jobs.startup-insider.com/unternehmen/onlinedoctor/jobs/senior-qa-engineer-80-100-fmd).

Das System under Test ist nicht das Medizinprodukt von OnlineDoctor. Dazu
habe ich keinen Zugang, und ich tue nicht so. Unter Test steht meine
öffentliche Website **[veryops](https://veryops.kintree.eu)**: Audit und
Monitoring für Websites, Deutsch und Englisch, Angebotsformular, Stripe-Link.
Die Praktiken sind die, die ich an einem Produkt mit Datenschutz- und
Nachweispflicht anlegen würde: Risiko zuerst, Tests an Anforderungen
gehängt, Lücken benannt, Freigabe als Satz.

## Urteil zum Stand 26. November 2026

**CONDITIONAL.** Die öffentlichen Flüsse, die sich lesen lassen, bestehen.
Drei mittlere Befunde sind offen. Ein GO wäre das falsche Wort.

| | |
| --- | --- |
| Funktional | GO, solange der Lauf keine unerwarteten Fehlschläge zeigt |
| Freigabe | CONDITIONAL wegen DEF-SEC-01, DEF-SEC-02, DEF-PRIV-01, DEF-A11Y-01 |
| Hohes offenes Defect | keines |
| Nicht prüfbar | Rollen und Rechte (kein Login), visuelle Baseline (keine) |

Die Pipeline ist absichtlich grün, wenn nur bekannte xfails fallen. Wer
nur den Haken sieht, liest an der Freigabe vorbei. Das Urteil steht in
`reports/release-readiness.html` nach einem vollen Lauf und in
[docs/befunde.md](docs/befunde.md).

## Was die Stelle verlangt, und wo es liegt

| | |
| --- | --- |
| Strategie, Risiko, Abdeckung, Freigabe | [docs/01-teststrategie.md](docs/01-teststrategie.md), [docs/02-risikoanalyse.md](docs/02-risikoanalyse.md) |
| Explorativ und manuelle Regression | [docs/07-exploratives-testen.md](docs/07-exploratives-testen.md), [docs/08-manuelle-regression.md](docs/08-manuelle-regression.md) |
| API, Integration, E2E, CI | `tests/`, [.github/workflows/quality-gate.yml](.github/workflows/quality-gate.yml) |
| Umgebungen, Testdaten, Reporting | [docs/05-testumgebungen-und-testdaten.md](docs/05-testumgebungen-und-testdaten.md), [docs/06-reporting-und-release-readiness.md](docs/06-reporting-und-release-readiness.md) |
| Traceability bis zum Defect | [docs/04-traceability.md](docs/04-traceability.md), `requirements/catalog.yml`, [.github/ISSUE_TEMPLATE/defect.md](.github/ISSUE_TEMPLATE/defect.md) |
| Desktop, Mobil, Auth, Fehler | Chromium, Firefox, WebKit, Pixel 7, iPhone 15. Auth als Negativprobe und N/A |
| pytest, Playwright, CircleCI, React/Jest | Suite, [.circleci/config.yml](.circleci/config.yml), [frontend/report-summary](frontend/report-summary) |
| KI, mit Grenzen | [docs/09-ki-im-testing.md](docs/09-ki-im-testing.md) |

Die ganze Tabelle mit den Nachweispfaden:
[docs/10-mapping-stellenanforderung.md](docs/10-mapping-stellenanforderung.md).
Was diese Mappe nicht kann: [docs/11-grenzen.md](docs/11-grenzen.md).

## Regeln gegen die live Seite

Lesen, nicht anfassen.

- Kein Absenden, kein Stripe, kein Login, kein Scanner, keine Last.
- HTTP nur GET, HEAD, OPTIONS, mit Abstand, ein Prozess.
- Playwright bricht POST auf dem Host ab, dazu Stripe und das
  Analytics-Beacon.
- `robots.txt` erlaubt das Crawlen. Die Suite bleibt klein.
- Kein Zeitplan und keine Nachtmail. Der Volllauf startet nur von Hand.

## Lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
python -m playwright install --with-deps chromium
bash scripts/quality_gate.sh
```

Voller Lauf auf Chromium, inklusive axe und der Freigabe
(`QA_RUN_SCOPE=full`):

```bash
QA_RUN_SCOPE=full pytest tests/unit tests/api tests/integration tests/e2e tests/a11y \
  -m "not quarantine" --browser chromium \
  --html=reports/pytest-full.html --self-contained-html
```

Andere Browser, nacheinander und nur der Smoke:

```bash
pytest tests/e2e -m "e2e and smoke" --browser firefox
pytest tests/e2e -m "e2e and smoke" --browser webkit
pytest tests/e2e -m "e2e and smoke" --browser chromium --device "Pixel 7"
pytest tests/e2e -m "e2e and smoke" --browser webkit --device "iPhone 15"
```

Staging oder lokal, sobald es sie gibt:

```bash
BASE_URL=https://staging.example.test QA_RUN_SCOPE=full pytest
```

`TEST_ENV=staging` liest die Platzhalter-URL aus
`config/environments.yml`. Die Profile `staging` und `local` sind nicht
provisioniert.

## CI

- **Quality gate** auf Pull Requests und auf `main`: ruff, das kleine
  Jest-Beispiel, Unit-Tests, die Hochrisiko-Teilmenge auf Chromium.
  Berichte als Artifact.
- **Full run** nur über *Run workflow*: ein Chromium-Lauf mit API, E2E und
  axe, danach Firefox, WebKit, Pixel 7 und iPhone 15 nacheinander
  (`max-parallel: 1`). Optional GitHub Pages, wenn `publish_pages` an ist.
- **CircleCI** (`.circleci/config.yml`) beschreibt denselben Gate. Der
  Volllauf dort hängt am Parameter `run_full` und läuft nicht von selbst.

## Befunde, kurz

Ausführlich in [docs/befunde.md](docs/befunde.md).

- **DEF-SEC-01** (mittel). Die HTML-Seiten senden kein HSTS, kein CSP,
  kein `X-Content-Type-Options`, keine Referrer-Policy.
- **DEF-SEC-02** (mittel). `GET /api` leitet auf `http://…/api/` um und
  erst von dort zurück auf HTTPS. Der Körper ist ein JSON-404.
- **DEF-PRIV-01** (mittel). Ein Cloudflare-Web-Analytics-Beacon wird
  ausgeliefert. Die Datenschutzerklärung sagt, es gebe keine
  Analysewerkzeuge. Das CDN selbst ist offengelegt.
- **DEF-A11Y-01** (mittel). Der Sprachschalter zeigt „EN“ oder „DE“, der
  barrierefreie Name sagt „Switch to English“ oder „Auf Deutsch wechseln“.
  axe wertet das auf jeder geprüften Seite als serious.
- **DEF-LINK-01** (niedrig). Verschleierte E-Mail-Links sind ohne Skript
  eine 404. `mailto:veryops@kintree.eu` steht daneben.

## Aufbau

```text
requirements/catalog.yml     Anforderungen
defects/register.yml         offene Befunde
tests/api                    HTTP, TLS, Negativprobe
tests/integration            Sitemap und interne Links
tests/e2e                    Browser, Formular ohne Absenden, Fehler
tests/a11y                   axe-core
tests/unit                   Urteil, Katalog, Heuristik, ohne Netz
qa_portfolio/reporting       Matrix und Freigabe
qa_portfolio/ai_review       Heuristik und Prompt-Vorlagen
frontend/report-summary      React/Jest, nur die Empfehlung anzeigen
docs/                        die Mappe auf Deutsch
```
