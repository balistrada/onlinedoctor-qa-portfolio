# Prompt: Review eines KI-erzeugten Tests

Der Reviewer (Mensch oder ein zweites, eng geführtes Durchsehen) arbeitet
diese Liste ab. Ein Test ohne diesen Review landet nicht im Gate.

```text
Prüfe den folgenden Test gegen die Anforderung <ID> und gegen die
tatsächlich beobachtete Antwort des Systems. Antworte nur mit Befunden.

1. Behauptet der Test eine Seite, ein Feld oder einen Status, den niemand
   live gesehen hat?
2. Kann der Test etwas schreiben, kaufen, einloggen oder löschen?
3. Ist die Erwartung das gewünschte Verhalten oder nur das heutige Fehlverhalten,
   festgeschrieben ohne Defect-ID?
4. Gibt es eine Anforderungs-ID, ein Risikosignal und eine Stufe?
5. Was passiert bei einem leeren, langsamen oder falschen Host?
6. Würde der Test ein Medizinprodukt-Risiko verdecken, indem er zu grob ist?

Test:
<Code>
```

Aufgenommen wird der Test nur, wenn 1 und 2 sauber sind und 3 entweder ein
echter Soll-Zustand oder ein `xfail` mit `DEF-…` ist.
