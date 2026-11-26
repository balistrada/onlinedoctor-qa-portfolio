# Risikoanalyse

## Skala

Eintrittswahrscheinlichkeit (L) und Wirkung (I) jeweils 1 bis 5.
Score = L × I.

| Score | Klasse | Folge für die Freigabe |
| --- | --- | --- |
| 1–6 | niedrig | Notiz, blockiert GO nicht allein |
| 7–14 | mittel | CONDITIONAL, solange der Punkt offen ist |
| 15–25 | hoch | NO-GO |

Wirkung meint hier den Schaden für Besucher, für das Vertrauen in ein
Prüfangebot und, als Maßstab der Stelle, für ein Umfeld, in dem Datenschutz
nicht verhandelbar ist. veryops verarbeitet auf dieser Oberfläche keine
Gesundheitsdaten. Ich übertrage den Maßstab trotzdem, und ich schreibe dazu,
wo die Wirkung wegen der tatsächlichen Oberfläche kleiner ist.

## Matrix

| ID | Risiko | L | I | Score | Klasse | Warum diese Werte | Prüfung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-HTTPS | Klartext auf der Apex | 2 | 5 | 10 | mittel, als Kontrolle hoch geführt | Ein fehlender Sprung auf HTTPS wäre auf einer öffentlichen Seite sofort sichtbar und für jedes Formular danach fatal. Heute funktioniert der Sprung, deshalb ist L klein. Der Test bleibt `risk_high`, weil die Wirkung bei einem Rückfall groß ist. | `REQ-HTTP-01` |
| R-TLS | Zertifikat oder Protokoll veraltet | 1 | 5 | 5 | hoch im Test, Score niedrig | Google Trust Services, TLS 1.3, Name `*.kintree.eu`. L ist klein, der Test ist hoch, weil ein abgelaufenes Zertifikat die ganze Seite unsichtbar macht. | `REQ-SEC-03` |
| R-PAY | Stripe-Link falsch oder ein Test löst einen Kauf aus | 2 | 5 | 10 | mittel | Der Href ist eine öffentliche Checkout-URL. Ein Klick würde einen echten Kauf anstoßen. Der Test liest den Href und navigiert nicht. | `REQ-E2E-06` |
| R-PII | Angebotsformular sendet ungültige oder ungewollte Angaben | 2 | 4 | 8 | mittel, Test hoch | Das Formular schickt Name und E-Mail an `/api/proposal`, sobald Captcha und Einwilligung da sind. Ein Test, der das auslöst, wäre selbst der Schaden. | `REQ-E2E-07` |
| R-AUTH | Versteckte Verwaltung oder API gibt Daten ohne Sitzung her | 2 | 5 | 10 | mittel, Test hoch | Es gibt keinen Login. Trotzdem dürfen `/admin/`, `/dashboard/`, `/login/` und `/api/…` keine Anwendung und keine Schlüssel zeigen. | `REQ-AUTH-01`, `REQ-AUTH-02` |
| R-SECRET | `.env` liegt im Webroot | 1 | 5 | 5 | Test hoch | Eine einzelne Negativprobe, kein Scan. Heute 404. | `REQ-SEC-05` |
| R-STORE | Eine öffentliche URL aus der Sitemap ist tot | 2 | 4 | 8 | mittel, Test hoch | Die Sitemap ist das Verzeichnis des Angebots. Eine tote URL ist ein direkter Besucherfehler und ein SEO-Fehler für ein SEO-Angebot. | `REQ-INT-01` |
| R-HEADER | Fehlende Härtungs-Header | 5 | 2 | 10 | mittel | Beobachtet, siehe DEF-SEC-01. L ist 5, weil der Zustand Fakt ist. I ist 2: keine Sitzung, keine Cookies, statische Seiten. Clickjacking und fehlendes HSTS bleiben ein Widerspruch zum eigenen Prüfangebot, aber kein Datenabfluss. | `REQ-SEC-01`, DEF-SEC-01 |
| R-DOWN | `/api` leitet auf HTTP um | 4 | 3 | 12 | mittel | Beobachtet, DEF-SEC-02. Der Hop springt zurück auf HTTPS, der Körper ist `{"error":"not found"}`. I steigt auf 5, sobald unter `/api` etwas Authentifiziertes liegt. | `REQ-SEC-02`, DEF-SEC-02 |
| R-PRIV | Analytics-Beacon gegen den Text der Datenschutzerklärung | 5 | 3 | 15 | mittel (an der Grenze) | Beobachtet, DEF-PRIV-01. L ist 5. I ist 3 und nicht 5, weil das CDN offengelegt ist, das Beacon typischerweise ohne Cookie arbeitet und auf dieser Seite keine Gesundheitsdaten liegen. Für ein Medizinprodukt-Umfeld wäre derselbe Widerspruch hoch. Ich lasse ihn hier mittel und schreibe die Grenze explizit, statt die Zahl aufzuhübschen. | `REQ-PRIV-01`, DEF-PRIV-01 |
| R-A11Y | Eigene Seiten bestehen axe critical/serious nicht | 5 | 2 | 10 | mittel | Beobachtet: DEF-A11Y-01, der Sprachschalter. L ist 5, weil der Verstoß auf jeder geprüften Seite liegt. I ist 2, weil der barrierefreie Name den Wechsel beschreibt und nur die sichtbare Abkürzung fehlt. Weitere serious-Funde wären neu zu bewerten. | `REQ-A11Y-01`, DEF-A11Y-01 |
| R-I18N | Sprachwechsel landet falsch | 2 | 3 | 6 | niedrig bis mittel | Zweisprachiges Angebot. Der Test ist mittel, weil ein stiller Wechsel auf die falsche Sprache den Kaufkontext verwechselt. | `REQ-I18N-01` |
| R-404 | Unbekannte URL ohne Orientierung | 2 | 2 | 4 | niedrig, Test mittel | Die markierte 404-Seite existiert. Der Test sichert, dass sie nicht durch eine nackte Proxy-Seite ersetzt wird. | `REQ-HTTP-06`, `REQ-ERR-01` |
| R-LINK | Verschleierte E-Mail-Links sind ohne Skript 404 | 3 | 1 | 3 | niedrig | DEF-LINK-01. Daneben steht ein funktionierendes `mailto:`. | `REQ-INT-02` |
| R-OFF | Offline oder Captcha-Ausfall wirkt wie ein Erfolg | 2 | 3 | 6 | niedrig | Die Seite ist kein PWA. Der Test erwartet, dass Offline scheitert und ein blockiertes Captcha einen Fehler zeigt, ohne zu senden. | `REQ-ERR-02`, `REQ-ERR-03` |

Scores auf der Grenze (R-PRIV = 15) stufe ich nach der Wirkung ein, nicht
nach der runden Zahl. 15 wäre nach der Tabelle hoch. Ich setze mittel, weil
die Wirkung auf dieser Oberfläche begrenzt ist, und dokumentiere das hier,
damit die Tabelle nicht still überschrieben wird. Würde dieselbe Lücke auf
einem Portal mit Sitzung und Gesundheitsdaten liegen, wäre die Klasse hoch
und die Freigabe NO-GO.

## Was ich bewusst nicht als Risiko „teste“

- Last und Verfügbarkeit unter Druck. Das wäre ein Angriff auf die
  Produktion, kein Test.
- Injizieren, Fuzzing, Authentifizierungs-Brute-Force. Die Negativprobe
  ist eine feste, kurze Liste.
- Ob Turnstile wirklich Menschen von Bots trennt. Dazu müsste man es lösen
  oder umgehen.

## Restrisiko nach dem Stand vom 26. November 2026

Funktional ist die öffentliche Fläche in den automatisierten Flüssen
unauffällig. Offen und mittel: DEF-SEC-01, DEF-SEC-02, DEF-PRIV-01,
DEF-A11Y-01. Offen und niedrig: DEF-LINK-01. Dazu die N/A-Lücken
Auth-Modell und visuelle Baseline.

Empfehlung des vollen Laufs deshalb **CONDITIONAL**, nicht GO. Eine
Freigabe unter einem Medizinprodukt-Maßstab würde die drei mittleren
Punkte schließen oder ausdrücklich akzeptieren. Ein GO auf der reinen
Funktion (Seiten da, Links da, Formular sendet im Test nicht) wäre
vertretbar und steht als `functional_decision` daneben.
