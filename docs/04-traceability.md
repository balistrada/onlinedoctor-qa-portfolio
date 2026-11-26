# Traceability

## Kette

```text
Anforderung  →  Testfall  →  Ergebnis  →  Defect  →  Evidenz
catalog.yml     @pytest.mark.req   results.json   register.yml   Bericht, Screenshot, Charta
```

Die Anforderung steht in `requirements/catalog.yml` mit ID, Risiko, Stufe,
Sollsatz und Art (`automated`, `manual`, `na`).

Der Test nennt die ID:

```python
@pytest.mark.risk_high
@pytest.mark.api
@pytest.mark.security
@pytest.mark.req("REQ-HTTP-01")
def test_apex_http_redirects_to_https(...):
    ...
```

Ein Test darf mehrere IDs tragen, wenn eine Beobachtung zwei Anforderungen
belegt. Der Angebots-Test trägt `REQ-E2E-07`. Startseite und Stripe-Href
teilen sich einen Seitenaufbau und zwei IDs, damit die Produktion nicht
doppelt geladen wird.

Am Ende der Session schreibt `qa_portfolio.reporting.session` nach
`reports/results.json`. Daraus entstehen:

- `reports/traceability.md` und `reports/traceability.html`
- `reports/release-readiness.md` und `reports/release-readiness.html`

Neu bauen, ohne die Seite noch einmal zu treffen:

```bash
python -m qa_portfolio.reporting.build --results reports/results.json
```

## Defects

Offene Lücken stehen in `defects/register.yml` mit ID, Risiko, Anforderung
und Evidenzpfad. Ein Test, der den heutigen Fehlzustand erwartet, ist
`xfail` und nennt die ID im `reason`. Ein xfail ohne `DEF-…` gilt als
ungeführtes Restrisiko.

Ein GitHub-Issue wird aus `.github/ISSUE_TEMPLATE/defect.md` angelegt.
Die Matrix verlinkt die Vorlage, solange `github_issue` leer ist, und die
URL, sobald sie im Register steht. Ich lege im Rahmen dieser Mappe keine
Issues im Namen der Seite an: die Befunde sind hier dokumentiert, das
Template ist der Weg, sie in den Tracker zu heben.

## Was die Matrix sonst noch zeigt

- `automatisiert`: mindestens ein Test, kein Fehlschlag, kein xfail
- `bekannt-offen`: xfail, im Register verankert
- `fehlgeschlagen`: unerwarteter roter Test
- `manuell`: Evidenzpfad in der Charta oder der Checkliste
- `n/a`: bewusste Lücke mit `na_reason`
- `lücke`: automatisiert gefordert, kein Test im vollen Lauf

## Statisch, ohne die Website

`tests/unit/test_catalog.py` prüft, dass jede automatisierte ID im
Testbaum vorkommt, jede manuelle ID eine existierende Datei nennt, und
jeder xfail-Grund eine Defect-ID enthält. Das läuft im Gate, ohne die
Produktion zu fragen.
