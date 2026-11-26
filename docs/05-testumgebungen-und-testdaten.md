# Testumgebungen und Testdaten

## Profile

`config/environments.yml` kennt drei Namen. `TEST_ENV` wählt eines, wenn
`BASE_URL` nicht gesetzt ist. Voreinstellung ist `prod`.

| Profil | URL | Stand |
| --- | --- | --- |
| prod | `https://veryops.kintree.eu` | die öffentliche Seite, lesend |
| staging | `https://staging.veryops.kintree.eu` | Platzhalter, nicht provisioniert |
| local | `http://127.0.0.1:4321` | Platzhalter, es wird kein Server gestartet |

`BASE_URL` gewinnt immer. Eine URL mit Benutzer oder Passwort wird
abgelehnt. TLS- und HTTPS-Tests überspringen sich, wenn das Schema nicht
`https` ist, damit ein lokaler HTTP-Preview nicht rot wird, nur weil er
kein Zertifikat hat.

## Warum hier trotzdem Produktion

Ein Gate gehört auf Staging. Das sage ich in der Strategie und richte die
Konfiguration so ein, dass Staging nur eine Zeile entfernt ist. Für diese
Mappe gibt es keines. Die öffentliche Seite ist statisch genug, dass eine
kleine, serielle, lesende Suite vertretbar ist. Sie ist kein Ersatz für
eine Umgebung mit Testdaten, Feature-Flags und einem Weg, einen Stand zu
zerstören, ohne dass es jemand merkt.

Der Kompromiss hat Regeln: kein POST, kein Checkout, kein Login, kein
Zeitplan, Abstand zwischen den Requests, Browser im Volllauf nacheinander.

## Testdaten

| Datei | Inhalt |
| --- | --- |
| `tests/data/site.yml` | Kernpfade, SEO-Stichprobe, Negativpfade, die eine fehlende URL, die öffentliche Mailadresse, die Soll-Header |
| `requirements/catalog.yml` | Anforderungen, keine Personendaten |
| `defects/register.yml` | Befunde |

Im Angebots-Test steht als E-Mail `qa-portfolio@example.com`. `example.com`
ist reserviert und kein Postfach eines Menschen. Der Name im Feld ist
`QA Portfolio`. Das Honeypot-Feld `company_fax` wird nicht gefüllt. Es wird
nur geprüft, dass es existiert und `aria-hidden` ist.

Es werden keine Kundendaten, keine Zugangsdaten und kein Inhalt des
Impressums über die öffentliche Erreichbarkeit hinaus ins Repository
kopiert. Die Tests verlangen einen Status und eine Überschrift, nicht die
Anschrift.

## Was ein Test nicht tun darf

- `POST /api/proposal`, auch nicht „nur mal sehen“.
- Stripe öffnen. Die Route-Sperre bricht `buy.stripe.com` ab, falls ein
  Test es doch versucht.
- Turnstile lösen.
- Weitere Pfade erraten. Die Negativliste ist fest und kurz.

## Fixtures

`sut_url` und `http` sind session-scoped. Der HTTP-Client cached GET-200
und wartet zwischen echten Requests. Ein zweiter Test auf dieselbe URL
trifft die Produktion nicht noch einmal. Redirects werden nicht als
Dokument gecached, damit ein 301 sichtbar bleibt.
