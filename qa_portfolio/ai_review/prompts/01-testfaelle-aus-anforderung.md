# Prompt: Testfälle aus einer Anforderung

Nutze diese Vorlage nur als Entwurf. Jede Aussage gegen das laufende System
prüfen, bevor sie ein Test wird. Keine erfundenen Seiten, keine Zugangsdaten,
keine Last, keine Exploits.

```text
Du bist Senior QA. Entwirf Testfälle für genau diese Anforderung.

Anforderung:
<ID und Wortlaut>

Bekannte Oberflächen (nur diese verwenden):
<Liste echter URLs und beobachteter Elemente>

Risiko (hoch/mittel/niedrig) und warum:
<aus der Risikomatrix, nicht neu schätzen lassen>

Grenzen:
- Nur lesende Prüfungen, wenn das System Produktion ist.
- Keine Formular-Absends, keine Logins, keine Scanner.
- Sage ausdrücklich, welche Fälle automatisierbar sind und welche explorativ bleiben.
- Wenn die Oberfläche die Anforderung nicht hergibt (zum Beispiel kein Login),
  schreibe N/A mit Begründung, erfinde keinen Flow.

Ausgabe je Fall: Titel, Stufe (API/Integration/E2E/manuell), Schritte,
Erwartung, benötigte Testdaten, was schiefgehen kann.
```
