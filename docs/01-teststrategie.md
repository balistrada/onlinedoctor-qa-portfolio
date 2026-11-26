# Teststrategie

## Wofür diese Mappe da ist

Ich bewerbe mich als Senior QA Engineer bei OnlineDoctor. Die Stelle verlangt
eine risikoorientierte Strategie, manuelles und automatisiertes Testen, CI,
Umgebungen, Nachvollziehbarkeit und ein Urteil zur Release-Reife. Das
Medizinprodukt von OnlineDoctor steht mir nicht zur Verfügung. System under
Test ist deshalb meine öffentliche Website [veryops](https://veryops.kintree.eu):
Website-Audit und Monitoring, zweisprachig, mit Angebotsformular und
Stripe-Checkout.

Die Praktiken sind dieselben, die ich an einem Medizinprodukt anlegen würde.
Der Maßstab ist bewusst streng: Vertrauen, Datenschutz und nachvollziehbare
Evidenz wiegen schwerer als ein grüner Marketing-Smoke. Die Grenze ist
ehrlich gezogen in [11-grenzen.md](11-grenzen.md).

## Qualitätsziele

1. Ein Besucher findet das Angebot, wechselt die Sprache und erreicht die
   rechtlichen Seiten.
2. Niemand kann über die öffentlichen Pfade eine Verwaltung, eine Sitzung
   oder Kundendaten sehen.
3. Der Kauf-Link und das Angebotsformular sind sichtbar und korrekt, ohne
   dass ein Test sie auslöst.
4. Was die Seite über sich selbst sagt (robots, Sitemap, llms.txt, JSON-LD,
   Datenschutzerklärung), stimmt mit dem ausgelieferten HTML überein oder
   ist als Defect mit Risiko geführt.
5. Eine Freigabe nennt GO, CONDITIONAL oder NO-GO und die Gründe. Ein
   Teillauf gibt keine Freigabe.

## Im Scope

- Die öffentlichen Dokumente aus der Sitemap, Stand 26. November 2026.
- HTTP-Vertrag, TLS, Header, Cookies, eine feste Negativprobe auf
  `/admin/`, `/dashboard/`, `/login/`, `/wp-admin/`, `/api/…`, `/.env`.
- Browserflüsse auf Chromium, dazu ein Smoke auf Firefox, WebKit, Pixel 7
  und iPhone 15.
- axe-core auf fünf Kernseiten, Stufe critical und serious.
- Fehlerbilder: echte 404, Offline, blockiertes Captcha, per Route
  simuliertes HTTP 500.

## Nicht im Scope

- Absenden des Angebots, Lösen von Turnstile, Öffnen von Stripe.
- Login-Versuche, Fuzzing, Scanner, Last, Exploit-PoCs.
- Visuelle Pixel-Baselines (`REQ-VIS-01`, N/A).
- Rollen und Rechte (`REQ-AUTH-03`, N/A): es gibt keinen Login.
- AWS. Die Stelle nennt AWS als Nice-to-have. Dieses System liegt nicht
  in einem Konto, das ich beschreiben oder anfassen dürfte, und die Aufgabe
  schließt AWS aus.

## Risiko zuerst

Jedes automatisierte Produkt-Test hat genau ein Risiko
(`risk_high`, `risk_medium`, `risk_low`), mindestens eine Stufe und
mindestens eine Anforderungs-ID. Die Matrix steht in
[02-risikoanalyse.md](02-risikoanalyse.md), der Katalog in
`requirements/catalog.yml`.

Hoch heißt: ein unerwarteter Fehlschlag oder ein bekanntes, noch offenes
Hochrisiko ist NO-GO. Mittel hält die Freigabe auf CONDITIONAL. Niedrig
bleibt eine Notiz und blockiert GO nicht allein.

## Abdeckungsziele

| Ziel | Soll | Wo es geprüft wird |
| --- | --- | --- |
| Jede Anforderung ist automatisiert, manuell mit Evidenz, oder N/A mit Begründung | 100 % | `tests/unit/test_catalog.py` |
| Jede Hochrisiko-Anforderung hat einen automatisierten Test oder ein N/A | 100 % | derselbe Test |
| Jede Sitemap-URL antwortet HTTPS 200 | 100 % der `loc`-Einträge | `REQ-INT-01` |
| Kernseiten haben Sprache, Titel, Canonical, hreflang | die Liste in `tests/data/site.yml` | `REQ-SEO-01` |
| Hochrisiko-Teilmenge läuft auf jedem Pull Request | API plus zwei Browserflüsse auf Chromium | `.github/workflows/quality-gate.yml` |
| Cross-Browser und axe | manueller Volllauf, Browser nacheinander | `.github/workflows/full-run.yml` |

Eine Lücke ist erlaubt, wenn sie als N/A mit Grund im Katalog steht. Eine
stille Lücke bei hohem Risiko ist NO-GO.

## Stufen

Viele lesende API- und Integrationsprüfungen, wenige Browserläufe, darüber
explorative Chartas und eine manuelle Checkliste. Begründung und Pyramide:
[03-testebenen-und-tools.md](03-testebenen-und-tools.md).

## Produktion, vorsichtig

Es gibt kein Staging. Der Gate läuft deshalb gegen die öffentliche Seite,
aber nur lesend:

- Methoden im HTTP-Client: GET, HEAD, OPTIONS.
- Abstand zwischen Requests, Voreinstellung 0,35 s, ein Prozess, kein xdist.
- Playwright bricht POST/PUT/PATCH/DELETE auf dem Host ab, dazu Stripe und
  das Analytics-Beacon.
- Das Angebotsformular wird im Browser geprüft, Turnstile wird nicht gelöst,
  `/api/proposal` wird zusätzlich abgefangen.
- `robots.txt` erlaubt das Crawlen. Die Suite bleibt klein und seriell.
- Kein Zeitplan. Niemand bekommt nachts eine Mail, weil ein Workflow
  tickt. Der Volllauf startet nur per `workflow_dispatch`.

## Freigabe

| Urteil | Wann |
| --- | --- |
| NO-GO | Unerwarteter Fehlschlag, xfail mit hohem Risiko, offenes hohes Defect, oder eine Hochrisiko-Anforderung ohne Test und ohne N/A |
| CONDITIONAL | Kein NO-GO, aber offenes oder nicht verankertes mittleres Restrisiko |
| GO | Voller Lauf, nichts davon |
| INCOMPLETE | Teillauf ohne NO-GO. Das ist keine Freigabe |

`functional_decision` ignoriert akzeptierte xfails. Sie sagt, ob die Suite
heute etwas Unerwartetes gesehen hat. Die Empfehlung daneben sagt, ob man
damit ausliefern würde. Details:
[06-reporting-und-release-readiness.md](06-reporting-und-release-readiness.md).

## Annahmen

- Die Sitemap ist die Liste der öffentlichen Seiten. Was nicht darin steht
  und nicht in der festen Negativprobe liegt, wird nicht erraten.
- Kopietexte dürfen sich ändern. Hochrisiko-Tests hängen an Rollen, Href
  und Status, nicht am Slogan.
- Ein xfail ohne `DEF-…` im Grund ist ein ungeführtes Restrisiko und macht
  den vollen Lauf CONDITIONAL.
