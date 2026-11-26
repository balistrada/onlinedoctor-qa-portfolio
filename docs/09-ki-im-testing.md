# KI im Testing

## Grundsatz

Ein Modell darf Entwürfe, Sortierung und Formulierungen liefern. Es darf
keine Freigabe erteilen und keine Anforderung für erfüllt erklären, die
niemand am System gesehen hat. Für Software im Medizinprodukt-Umfeld gilt
das schärfer: ein generierter Test ist ein ungeprüftes Dokument, bis ein
Review ihn gegen die Anforderung und gegen eine beobachtete Antwort hält.
Geschwindigkeit ist kein Beleg.

## Review, bevor ein KI-Test in den Gate darf

1. Jede URL, jedes Feld und jeder Status wurde vorher gelesen oder im
   Browser gesehen. Steht es nur im Vorschlag, fliegt es raus.
2. Der Test kann nichts schreiben, kaufen, einloggen oder löschen. Im
   Zweifel sperrt die Route, nicht das gute Zureden im Prompt.
3. Die Erwartung ist der Soll-Zustand. Der heutige Fehlzustand steht als
   `xfail` mit `DEF-…` da, nicht als `assert` auf den Bug.
4. Risiko, Stufe und Anforderungs-ID hängen am Test.
5. Ein zweites Mal lesen: würde der Test ein ernstes Risiko grün malen,
   weil er nur den glücklichen Pfad anfasst?

Die Prompt-Vorlagen dazu liegen in
`qa_portfolio/ai_review/prompts/`:

- `01-testfaelle-aus-anforderung.md`
- `02-review-ki-test.md`
- `03-fehler-triage.md`

## Heuristik ohne Modell

`python -m qa_portfolio.ai_review.heuristic "Text der Änderung"` zählt
Schlüsselwörter und schlägt hoch, mittel oder niedrig vor. „Stripe“ und
„Datenschutz“ ziehen nach oben, „Sitemap“ nach mittel, ein leerer Text
bleibt niedrig mit dem Hinweis, dass das kein Signal ist. Die Heuristik
schreibt nicht in den Katalog. Sie ist ein Sortierhilfe für eine neue
Zeile, nichts weiter. Tests dazu stehen in `tests/unit/test_heuristic.py`.

Ich nehme absichtlich kein Modell für diese Stelle. Ein Netzaufruf wäre
eine Abhängigkeit, die ich im Gate nicht erklären will, und die Antwort
wäre nicht stabiler als die Wortliste.

## Wie KI in diesem Repository benutzt wurde

Die Suite ist mit einem Coding-Agenten entworfen worden. Danach, und das
ist die Prüfung, nicht der Entwurf:

- Die Seiten, die Sitemap, `robots.txt`, `llms.txt`, das Angebots-Skript
  und die Header wurden gelesen, bevor eine Erwartung im Code landete.
- Pfade, die es nicht gibt, sind N/A oder eine feste Negativprobe, keine
  erfundenen Dashboards.
- Bekannte Lücken sind Defects mit xfail, nicht wegassertiert.
- Die Sicherheitsregeln (kein POST, kein Stripe, kein Login) stehen im
  Client und in der Playwright-Route, nicht nur im Prompt.
- Jeder automatisierte Test ist lokal gegen die öffentliche Seite gelaufen.
  Was rot war, wurde entweder korrigiert, weil der Test falsch lag, oder
  als Defect stehen gelassen.

## Grenzen, konkret

- Ein Modell halluziniert Selektoren. Deshalb hängen die fragilen Texte
  an Rollen oder an `#quote-strings`, das die Seite selbst ausliefert.
- Ein Modell erklärt einen Fehlschlag gern zur Umgebung. Die Triage-Vorlage
  verlangt Indizien aus dem Auszug und einen nächsten Schritt, keine
  erfundene Logzeile.
- Für ein Medizinprodukt reicht „die KI hat die Tests geschrieben“ nicht
  als Verifikationsnachweis. Der Nachweis ist die Matrix: Anforderung,
  Test, Ergebnis, Defect, Evidenz, und ein Mensch, der das Urteil trägt.
- Die Heuristik übersieht Risiken ohne die Wörter, die ich ihr gegeben
  habe. Ein stiller Datenfluss mit unauffälligem Namen bleibt unsichtbar.
  Deshalb bleibt die Matrix in `docs/02-risikoanalyse.md` von Hand
  begründet.
