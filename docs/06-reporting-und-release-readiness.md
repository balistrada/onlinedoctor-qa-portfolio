# Reporting und Release-Readiness

## Was ein Lauf hinterlässt

| Artefakt | Werkzeug | Wozu |
| --- | --- | --- |
| `reports/junit-*.xml` | pytest | CI, CircleCI `store_test_results` |
| `reports/pytest-*.html` | pytest-html | eine Datei, im Browser lesbar, als Artifact |
| `reports/allure-results/` | allure-pytest | Rohdaten, falls die Allure-CLI später HTML baut |
| `reports/results.json` | eigene Session-Hook | Eingabe für Matrix und Freigabe |
| `reports/traceability.md` / `.html` | `qa_portfolio.reporting` | Anforderung bis Evidenz |
| `reports/release-readiness.md` / `.html` | dasselbe | Urteil und Gründe |
| `reports/playwright/` | pytest-playwright | Screenshot nur beim Fehlschlag |

Der Gate lädt `reports/` als Artifact hoch, auch wenn der Job rot ist.

## Gewichtung

Hoch zählt 5, mittel 3, niedrig 1. Die gewichtete Pass-Rate ist das
Gewicht der bestandenen Tests (inklusive xpass) geteilt durch das Gewicht
aller ausgeführten Tests, xfails eingeschlossen. Übersprungene und nicht
gelaufene Tests zählen nicht. Die Rate ist eine Kennzahl, nicht das Urteil.
Ein einzelner hoher Fehlschlag ist NO-GO, auch wenn die Rate noch hoch
aussieht.

## Urteil

Siehe die Tabelle in der Teststrategie. Kurz die Reihenfolge:

1. Unerwarteter Fehlschlag, hoher xfail, im vollen Lauf ein offenes hohes
   Defect oder eine ungedeckte Hochrisiko-Anforderung: **NO-GO**.
2. Sonst, im vollen Lauf, mittleres offenes Defect, mittlerer xfail,
   xfail ohne Defect-ID, xpass oder eine kleinere Deckungslücke:
   **CONDITIONAL**.
3. Voller Lauf, nichts davon: **GO**. Niedrige offene Punkte werden
   genannt und blockieren nicht.
4. Jeder andere Scope ohne NO-GO: **INCOMPLETE**. Der PR-Gate ist ein
   Signal, keine Freigabe.

`functional_decision` ist NO-GO nur bei unerwarteten Fehlschlägen. Ein
Lauf kann funktional GO und insgesamt CONDITIONAL sein. Genau das ist der
erwartete Stand dieser Website, solange DEF-SEC-01, DEF-SEC-02,
DEF-PRIV-01 und DEF-A11Y-01 offen sind.

## Wie man das liest

Die HTML-Empfehlung ist die Seite, die ich in ein Review legen würde.
Die Gründe sind Sätze, keine Ampel ohne Text. Screenshots gibt es, wenn
ein Browser-Test fällt. Die Matrix zeigt daneben, welche Anforderung von
welchem Test getragen wird und welcher Defect daran hängt.

Ein xpass ist kein stiller Erfolg. Die Lücke ist weg, das xfail muss weg,
sonst bleibt der nächste echte Rückfall unsichtbar.

## Seitenveröffentlichung

Der Volllauf kann die Berichte auf GitHub Pages legen, wenn beim
`workflow_dispatch` die Eingabe `publish_pages` gesetzt ist. Voreinstellung
ist aus. Auch das ist kein Zeitplan: es passiert nur, wenn jemand den Lauf
startet.
