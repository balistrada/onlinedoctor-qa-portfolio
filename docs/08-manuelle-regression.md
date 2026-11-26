# Manuelle Regression

Automatisierung trägt den Vertrag. Diese Liste trägt, was ein Skript
schlecht oder gar nicht entscheiden soll. Sie ist der manuelle Teil von
`REQ-MAN-01` und wird vor einer Freigabe durchgegangen, zusätzlich zum
vollen Lauf. Haken nur setzen, wenn die Zeile in dieser Runde wirklich
angesehen wurde.

Umgebung: Produktions-URL, ein aktueller Desktop-Browser und ein schmales
Fenster oder ein Telefon. Nichts absenden, Stripe nicht öffnen, nirgends
einloggen.

## Vor dem Klicken

- [ ] Der volle Lauf ist durch. Die Empfehlung ist gelesen, offene DEF-IDs
      sind noch die bekannten oder neu bewertet.
- [ ] Keine neue Hochrisiko-Lücke im Katalog ohne Test oder N/A.

## Startseite, beide Sprachen

- [ ] Eine Hauptüberschrift, der Audit-Einstieg ist sichtbar und führt auf
      die Audit-Seite, ohne dass etwas gekauft wird.
- [ ] Preise nennen Setup und Monat. Der Schalter „Jährlich“ ändert den
      Betrag und verspricht −20 %. Ob die Zahl dazu passt, kurz nachrechnen.
- [ ] Sprachwechsel DE ↔ EN behält das Thema der Seite (Start bleibt Start,
      Audit bleibt Audit), nicht nur die Startseite.
- [ ] Hell/Dunkel schaltet ohne Layoutbruch. Nach Reload bleibt die Wahl.

## Angebot

- [ ] Der Senden-Button ist deaktiviert, solange das Captcha nicht fertig ist.
- [ ] Eine offensichtlich falsche E-Mail wird erklärt, ohne dass eine Mail
      ankommt. Dafür den automatisierten Test gelten lassen, nicht selbst
      absenden.
- [ ] Honeypot ist nicht im Tab-Ablauf spürbar.
- [ ] Einwilligungstext verlinkt Datenschutz und AGB.

## Vertrauen

- [ ] Impressum, Datenschutz und AGB öffnen in beiden Sprachen. Die
      englischen Seiten sagen, dass die deutsche Fassung führt, wo das
      bisher so war.
- [ ] Datenschutzerklärung und die tatsächlich geladenen Dritt-Skripte
      passen zusammen (DEF-PRIV-01 im Blick behalten).
- [ ] Kontakt ist über die sichtbare Mailadresse erreichbar, nicht nur
      über den verschleierten Link (DEF-LINK-01).

## Fehler und Mobil

- [ ] Eine erfundene URL zeigt die markierte 404 und einen Weg nach Hause.
- [ ] Bei 390 px Breite lässt sich das Menü öffnen, der Fokus landet nicht
      unter der Leiste, der Skip-Link ist per Tastatur erreichbar
      (`REQ-A11Y-02`).
- [ ] Zoom 200 % auf der Startseite: kein abgeschnittener Preis, kein
      überlagerter Button.

## Bewusst nicht auf der Liste

- Kauf abschließen.
- Angebot absenden, auch nicht mit der eigenen Adresse „nur zum Test“.
- Passwörter ausprobieren.
- Mehrere Tabs parallel gegen die Seite hämmern.
