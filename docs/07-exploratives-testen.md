# Exploratives Testen

## Charta-Vorlage

| Feld | Inhalt |
| --- | --- |
| Charta | Ein Satz: was ich verstehen will, und was ich nicht anfasse |
| Zeit | Begrenzt, typisch 45–60 Minuten |
| Setup | URL, Viewport, Browser, Sprache. Keine Zugangsdaten |
| Daten | Was ich eingeben darf. Auf Produktion: nichts absenden |
| Notizen | Zeit, Beobachtung, Erwartung, Frage |
| Befunde | DEF-ID oder „kein Defect, nur Notiz“ |
| Abdeckung | Welche REQ-IDs diese Session berührt hat |

Session-Notizen bleiben im Repo, wenn sie eine Aussage tragen. Lose
Klickprotokolle nicht.

## Session 2026-11-26 — Vertrauensflächen der öffentlichen Seite

**Charta.** In 60 Minuten die öffentliche Informationsarchitektur und die
Stellen verstehen, an denen die Seite Vertrauen behauptet (HTTPS, Datenschutz,
Kontakt, Kauf, Angebot). Nicht anfassen: Absenden, Stripe, Login-Versuche,
Scanner.

**Setup.** `https://veryops.kintree.eu`, curl und ein HTML-Parser, Desktop.
Browserflüsse kamen danach als Automatisierung, nicht in dieser Session.

**Was ich gesehen habe.**

- Die Sitemap nennt 14 URLs: Startseite und Englisch, Audit, FAQ, Angebot
  und Quote, Impressum und Imprint, Datenschutz und Privacy, AGB und die
  englischen AGB. Dazu Anker auf der Startseite (`#pricing`, `#team`, …).
- `robots.txt` erlaubt alles und zeigt auf `sitemap-index.xml`.
  `sitemap.xml` leitet dorthin. `llms.txt` existiert und beschreibt das
  Angebot.
- JSON-LD: Organization und WebSite auf den Seiten, FAQPage auf der FAQ,
  Service/Offer auf dem Audit.
- Das Angebotsformular hat `novalidate`, Pflichtfelder Name und E-Mail,
  ein Honeypot `company_fax`, eine Einwilligung und Turnstile. Der
  Senden-Button startet deaktiviert. Der Handler prüft E-Mail, Einwilligung
  und Captcha und postet erst dann an `/api/proposal`.
- Kauf-Links zeigen auf `https://buy.stripe.com/…`. Nicht geöffnet.
- `/admin/`, `/dashboard/`, `/login/`, `/wp-admin/` sind eine markierte
  404-Seite. `/api/` und `/api/proposal` sind JSON `{"error":"not found"}`.
  Es gibt keinen Login. `REQ-AUTH-03` ist deshalb N/A.
- Unbekannte Pfade: ohne Slash ein 301 auf die Slash-Variante über HTTPS,
  mit Slash die zweisprachige 404 mit „Zur Startseite“.
- HTTP auf der Apex springt auf HTTPS. TLS 1.3, Zertifikat `*.kintree.eu`.

**Befunde aus der Session.**

- DEF-SEC-01: die HTML-Dokumente senden die üblichen Härtungs-Header nicht.
  Ein Cloudflare-Sonderpfad unter `/cdn-cgi/` setzt welche. Die Dokumente
  nicht.
- DEF-SEC-02: `GET /api` leitet auf `http://veryops.kintree.eu/api/` um,
  von dort zurück auf HTTPS. `/faq` bleibt auf HTTPS. Heute kein
  Datenkörper außer dem JSON-404.
- DEF-PRIV-01: das HTML lädt `static.cloudflareinsights.com/beacon.min.js`.
  Abschnitt 8 der Datenschutzerklärung sagt, es würden keine
  Analysewerkzeuge eingesetzt. Cloudflare als CDN ist in Abschnitt 2
  genannt, das Beacon nicht.
- DEF-LINK-01: `/cdn-cgi/l/email-protection#…` antwortet 404. Daneben steht
  `mailto:veryops@kintree.eu`.

**Nicht verfolgt.** Ob der Jahrespreis rechnerisch 20 % unter zwölf
Monatspreisen liegt. Ob der Skip-Link bei Tastaturbedienung sichtbar wird.
Beides steht in der Checkliste und in der nächsten Charta, nicht als
behaupteter Defect.

**Abdeckung.** Die Session hat die Anforderungen vorbereitet, die danach
automatisiert wurden. Sie ersetzt den Gate nicht.

## Offene Chartas

| Charta | Warum noch offen | Grenze |
| --- | --- | --- |
| Tastatur, Zoom 200 %, Skip-Link (`REQ-A11Y-02`) | axe sieht den Fokus nicht | 45 Minuten, ein Browser, kein Formular absenden |
| Preislogik Monat gegen Jahr | Rechnen, nicht klicken um zu kaufen | nur die sichtbaren `data-monthly` / `data-annual` Werte |
| Englische Angebotsseite gegen die deutsche | dieselben drei Fehlertexte, andere Sprache | kein Absenden |
| Rechtstexte auf interne Widersprüche | Lesen, nicht scrapen | Impressum nicht ins Repo kopieren |
