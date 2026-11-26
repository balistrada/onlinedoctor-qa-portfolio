# Auswahl der Testebenen und Werkzeuge

## Pyramide

```text
        explorativ / manuelle Checkliste
      wenige Browserflüsse (Chromium voll, andere Browser nur Smoke)
    Integrationsprüfungen (Sitemap, interne Links)
  viele API- und Vertragsprüfungen (Status, Header, TLS, JSON-LD)
```

Ein toter Status, ein falscher Redirect oder ein JSON-Körper ohne Secrets
braucht keinen Browser. Der Browser kommt dazu, wo Sichtbarkeit, Klick und
clientseitige Validierung die Aussage sind. Explorativ bleibt, was ein
Skript schlecht sieht: ob ein Satz in der Datenschutzerklärung zur Technik
passt, ob der Fokus sinnvoll wandert, ob ein Preis verständlich ist.

## pytest

Die Stelle nennt Python und pytest. Ich nehme sie, weil Marker die
Traceability tragen: Risiko, Stufe und `REQ-…` hängen am Test, nicht in
einer zweiten Tabelle, die sofort veraltet. `pytest-rerunfailures` wiederholt
einen Fehlschlag einmal. Ein zweites Mal rot ist bis zum Beweis keine
Umgebung. Was wir als Umgebungslärm kennen, bekommt `quarantine` und fliegt
aus dem Gate. In dieser Mappe ist die Quarantäne leer; der Marker ist da,
damit die Regel einen Platz hat.

## Playwright für Python

Die Stelle nennt Playwright. Die Python-Bindings halten die Suite in einer
Sprache. Chromium, Firefox und WebKit laufen über denselben Test.
`--device "Pixel 7"` und `--device "iPhone 15"` sind die mobilen Profile,
keine eigenen Testkopien.

Der Volllauf setzt `max-parallel: 1`. Fünf Browser gleichzeitig gegen die
Produktion wären unhöflich und würden Zufallsfehler erzeugen, die wie
Produktfehler aussehen.

## axe-core

`axe-playwright-python` injiziert axe in die geladene Seite. Critical und
serious sind der automatische Riegel. Moderate Funde sind ein Hinweis für
die Charta, kein roter Build: sie sind oft Kontrast in dekorativen Flächen
und ohne Kontext leicht falsch. Tastatur und Zoom bleiben manuell
(`REQ-A11Y-02`).

## CircleCI neben GitHub Actions

Die Stelle nennt CircleCI. `.circleci/config.yml` spiegelt den Gate und,
nur wenn der Pipeline-Parameter `run_full` wahr ist, den seriellen Volllauf.
Es gibt keinen Cron. GitHub Actions ist der Workflow, der auf diesem
Repository wirklich läuft. CircleCI ist die zweite, lesbare Definition
derselben Stufen, für eine Umgebung, die CircleCI schon hat.

## React und Jest, klein und beschriftet

`frontend/report-summary/` rendert eine fertige Empfehlung. Es ist kein
Stück der Website. Die Entscheidung fällt in Python. Das Beispiel ist da,
weil der Stack React und Jest nennt, und es wäre unehrlich, eine zweite
App zu erfinden, nur damit der Ordner existiert.

## Was ich nicht genommen habe

- Kein Cypress, kein Selenium: ein Browser-Werkzeug reicht.
- Kein AWS, keine Gerätefarm, kein Browserstack. Die Aufgabe schließt AWS
  aus, und eine Farm würde die Produktion von vielen IPs gleichzeitig treffen.
- Kein Allure-CLI im Gate. `allure-pytest` schreibt die Rohdaten nach
  `reports/allure-results`. Die HTML-Anzeige braucht die Allure-CLI, die auf
  einem kostenlosen Runner nicht vorausgesetzt ist. pytest-html und JUnit
  sind ohne Zusatzwerkzeug lesbar.
- Kein visuelles Regressionstool, solange keine Baseline existiert.

## Flakes: Produkt oder Umgebung

| Zeichen | Eher | Reaktion |
| --- | --- | --- |
| Timeout, DNS, TLS-Handshake, einmaliges 502/503 am Rand | Umgebung | ein Wiederholversuch, dann rot lassen |
| Dieselbe Assertion, zweimal, auf einem Status oder einem Text, den die Seite selbst liefert | Produkt oder Test | nicht wiederholen, Defect oder Test nachziehen |
| Copy geändert, Selektor hängt am Satz | brüchiger Test | Selektor an Rolle oder an die JSON-Texte der Seite hängen |
| xfail wird xpass | die Lücke ist zu | xfail entfernen, nicht feiern und liegen lassen |

Der Angebots-Test liest die Fehlermeldungen aus `#quote-strings` auf der
Seite. Ändert sich der Satz, bleibt der Test grün, solange der Handler
denselben Satz zeigt. Das ist Absicht.
