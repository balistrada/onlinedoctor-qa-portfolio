# Grenzen, ohne Beschönigung

- Das System under Test ist nicht das Medizinprodukt von OnlineDoctor.
  Ich habe keinen Zugang dazu und tue nicht so. veryops ist eine
  öffentliche Marketing- und Angebotsseite.
- Es gibt kein Staging. Der Gate trifft die Produktion, lesend und klein.
  In einem echten Team wäre das die Ausnahme für einen dünnen Smoke, nicht
  der Alltag.
- Es gibt keinen Login. Authentifizierung und Rechte sind als Negativprobe
  und als N/A dokumentiert. Ich habe keine 401-Antwort erfunden, wo die
  Seite 404 sagt.
- Visuelle Regression fehlt, weil keine Baseline existiert. Ein
  Screenshot-Vergleich gegen Produktion wäre Rauschen.
- axe ist ein Smoke auf fünf Seiten und zwei Wirkstufen. Es ist kein
  WCAG-Audit und kein Ersatz für Tastatur und Zoom.
- Die bekannten mittleren Defects sind xfail. Die Pipeline bleibt grün,
  die Freigabe wird davon CONDITIONAL. Wer nur auf den grünen Haken schaut,
  übersieht das. Deshalb steht das Urteil im Bericht und in der README,
  nicht nur in der Check-Farbe.
- Allure-HTML wird nicht im Runner gebaut. Die Rohdaten liegen bei, die
  lesbare Fassung ist pytest-html plus die eigenen Berichte.
- CircleCI ist konfiguriert und auf diesem Repository nicht angeschlossen.
  GitHub Actions ist der Lauf, der wirklich passiert.
- Die React-Komponente prüft eine Empfehlung, die Python schon getroffen
  hat. Sie testet veryops nicht.
- Die Heuristik und die Prompt-Vorlagen ersetzen kein Review. Ein Coding-Agent
  hat die Suite mitgeschrieben. Aufgenommen wurde, was gegen die live
  gelesene Seite hält.
- Ich habe die Seite nicht unter Last gesetzt, nicht gescannt und kein
  Formular abgeschickt. Manches, das nur beim echten Absenden sichtbar
  würde (Mail kommt an, PDF stimmt, Stripe nimmt das Geld), ist ungeprüft.
  Das steht so in der Strategie, damit es nicht wie eine Abdeckung aussieht.
- Die Risikozahlen sind Urteile mit Begründung, keine Messung. Eine andere
  Person kann R-PRIV auf hoch setzen. Dann wäre die Freigabe NO-GO. Die
  Begründung, warum ich bei mittel bleibe, steht in der Risikoanalyse und
  lässt sich angreifen. Das ist der Punkt.
