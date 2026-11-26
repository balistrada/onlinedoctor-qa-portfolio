# Befunde auf veryops.kintree.eu

Beobachtet am 26. November 2026, nur mit GET, HEAD und OPTIONS. Keine
Formular-Absends, keine Login-Versuche. Die IDs entsprechen
`defects/register.yml`. Ein GitHub-Issue ist bewusst keines angelegt; die
Vorlage dafür ist `.github/ISSUE_TEMPLATE/defect.md`.

## DEF-SEC-01 {#def-sec-01}

**Öffentliche HTML-Antworten ohne die üblichen Härtungs-Header.** Risiko mittel.

`GET /` antwortet 200 und setzt weder `Strict-Transport-Security` noch
`Content-Security-Policy`, `X-Content-Type-Options` oder `Referrer-Policy`.
Dieselbe Leerstelle auf `/audit/` und `/datenschutz/`. Ein Abruf von
`/cdn-cgi/l/email-protection` setzt `X-Frame-Options` und `Referrer-Policy`,
die Dokumente tun es nicht. Es gibt auf diesen Seiten kein `Set-Cookie`.

Wirkung heute: kein Sitzungsdiebstahl über ein Cookie, das es nicht gibt.
Bleibt: Clickjacking ist nicht per Header ausgeschlossen, HSTS fehlt, und
eine Seite, die Härtung als Leistung verkauft, liefert sie selbst nicht.
Der Test `test_public_html_sends_hardening_headers` ist xfail. Wird der
Header-Satz vollständig, wird der Test xpass und das xfail gehört entfernt.

## DEF-SEC-02 {#def-sec-02}

**Slash-Weiterleitung von `/api` fällt auf HTTP zurück.** Risiko mittel.

1. `GET https://veryops.kintree.eu/api` → 301, `Location: http://veryops.kintree.eu/api/`.
2. `GET http://veryops.kintree.eu/api/` → 301 auf `https://veryops.kintree.eu/api/`.
3. `GET https://veryops.kintree.eu/api/` → 404, `{"error":"not found"}`.

`GET https://veryops.kintree.eu/faq` leitet auf `https://…/faq/` um, ohne
Klartext. Der Unterschied sitzt auf dem API-Pfad (die 301-Seite nennt
nginx). Heute kein Nutzdatenkörper und kein Cookie auf dem Hop. Das Muster
wird hoch, sobald `/api` etwas Authentifiziertes ausliefert: ein klares
HTTP dazwischen ist dann ein Abhörpunkt. Der öffentliche Pfad ist als
bestandener Test festgehalten, der API-Pfad als xfail.

## DEF-PRIV-01 {#def-priv-01}

**Web-Analytics-Beacon, das die Datenschutzerklärung nicht nennt.** Risiko mittel.

Das HTML der Startseite bindet
`https://static.cloudflareinsights.com/beacon.min.js/…` ein
(`data-cf-beacon`). Abschnitt 8 der Datenschutzerklärung sagt, die Website
setze keine Cookies zu Tracking- oder Analysezwecken und keine
Analysewerkzeuge ein, und nennt Google Analytics als Beispiel. Abschnitt 2
nennt Cloudflare als CDN und Auftragsverarbeiter, dazu Network Error
Logging. Das Wortlaut zu Analysewerkzeugen und das Beacon passen nicht
zusammen.

Ob das Snippet aus dem Cloudflare-Dashboard injiziert wird oder im Template
steht, ändert die Pflicht nicht, es zu erwähnen oder abzuschalten. Ich
habe das Beacon in den Browser-Tests per Route abgebrochen, damit die Suite
nicht noch zusätzliche Analyse-Hits erzeugt. Der HTTP-Test liest das
ausgelieferte HTML und bleibt xfail, solange das Beacon da ist und der
Text es nicht nennt.

Wirkung: Vertrauens- und Transparenzlücke, kein nachgewiesener Abfluss von
Formulardaten. Auf einem Portal mit Gesundheitsdaten wäre dieselbe Lücke
hoch. Hier bleibt sie mittel, mit dieser Begründung.

## DEF-A11Y-01 {#def-a11y-01}

**Sprachschalter: der sichtbare Text steht nicht im barrierefreien Namen.**
Risiko mittel.

Auf jeder geprüften Seite (`/`, `/audit/`, `/faq/`, `/angebot/`,
`/impressum/`) meldet axe-core genau einen serious-Verstoß,
`label-content-name-mismatch`. Der Knoten ist der Sprachschalter:

```html
<a class="lang-switch" href="/en/" hreflang="en" aria-label="Switch to English">EN</a>
```

Die englische Seite spiegelt das mit „DE“ und „Auf Deutsch wechseln“.
WCAG 2.5.3 verlangt, dass der sichtbare Text im barrierefreien Namen
enthalten ist. Ein Spracheingabe-Nutzer, der „EN“ sagt, trifft den
Schalter nicht. Der Name selbst ist verständlich, deshalb ist die Wirkung
mittel: ein echter Verstoß, kein unbenutzbarer Ablauf. Andere critical-
oder serious-Funde hatte dieser Lauf nicht. Der Test lässt nur diese
bekannte ID als xfail durch und fällt bei jeder weiteren ID hart.

## DEF-LINK-01 {#def-link-01}

**Verschleierte E-Mail-Links antworten ohne Skript mit 404.** Risiko niedrig.

`href="/cdn-cgi/l/email-protection#…"` auf der Startseite antwortet 404.
Das Decode-Skript von Cloudflare soll daraus im Browser ein `mailto`
machen. Unmittelbar daneben steht `mailto:veryops@kintree.eu`. Der
Kontaktweg ist nicht zu. Ohne JavaScript ist der verschleierte Link eine
Sackgasse. Niedrig, weil der Ersatz sichtbar ist. Der Test auf den
Klartext-Mailto besteht, der Test auf den verschleierten Href ist xfail.

## Kein Befund, aber leicht zu verwechseln

- `/admin/`, `/dashboard/`, `/login/` sind 404, keine Anmeldeseite. Das ist
  kein Defect und kein bestandener Rollen-Test. `REQ-AUTH-03` ist N/A.
- `OPTIONS /` antwortet 405 ohne `Allow`. Der Zustand ist notiert, nicht
  als Defect geführt: die Methode verändert nichts, HEAD und GET bleiben
  in Ordnung.
- Die 404-Seite ist zweisprachig und hat einen Weg zur Startseite. Das
  ist der Soll-Zustand von `REQ-ERR-01`, kein Defect.
