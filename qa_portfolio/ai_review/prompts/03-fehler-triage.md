# Prompt: Triage eines fehlgeschlagenen Laufs

Die Heuristik und das Modell dürfen einen Fehlschlag sortieren. Die Ursache
bleibt eine Hypothese, bis jemand sie am System oder am Diff belegt.

```text
Hier ist ein pytest-Fehlschlag (Auszug, keine Secrets).

Klassifiziere ihn als eines von:
- Produktregression
- bekanntes Defect (nenne die DEF-ID, falls der Text eine enthält)
- Umgebungsrauschen (Timeout, DNS, TLS-Handshake, 5xx am Rand)
- brüchiger Test (Selektor, Textkopie, Reihenfolge)

Gib die Klasse, die zwei stärksten Indizien und den nächsten einzelnen
Prüfschritt an. Erfinde keine Logs, die nicht im Auszug stehen.

Auszug:
<Fehlermeldung und die letzten relevanten Zeilen>
```

Umgebungslärm darf einmal wiederholt werden (`pytest-rerunfailures`, ein
Wiederholversuch). Was danach rot bleibt, ist bis zum Beweis das Produkt
oder der Test, nicht "Flake".
