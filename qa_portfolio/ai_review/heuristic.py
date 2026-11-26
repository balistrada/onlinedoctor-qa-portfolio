"""Keyword heuristic that suggests a risk level. It does not call a model.

The suggestion is a triage hint for a new requirement or a change description.
A person still sets the risk in ``requirements/catalog.yml``.
"""

from __future__ import annotations

import argparse
import json
import re

# Longer phrases first so "personal data" wins over a short token.
_HIGH = (
    ("personal data", "personenbezogene Daten"),
    ("payment", "Zahlung"),
    ("stripe", "Zahlungsdienstleister"),
    ("password", "Geheimnis"),
    ("patient", "Gesundheitsbezug"),
    ("medical", "Medizinprodukt-Kontext"),
    ("datenschutz", "Datenschutz"),
    ("privacy", "Datenschutz"),
    ("session", "Sitzung"),
    ("login", "Anmeldung"),
    ("auth", "Authentifizierung"),
    ("certificate", "Zertifikat"),
    ("tls", "Transportverschlüsselung"),
)
_MEDIUM = (
    ("accessibility", "Barrierefreiheit"),
    ("barriere", "Barrierefreiheit"),
    ("sitemap", "Auffindbarkeit"),
    ("redirect", "Weiterleitung"),
    ("language", "Sprache"),
    ("form", "Formular"),
    ("wcag", "WCAG"),
    ("a11y", "Barrierefreiheit"),
    ("i18n", "Sprache"),
    ("seo", "Sichtbarkeit"),
)


def suggest_risk(text: str) -> dict:
    folded = text.casefold()
    hits: list[dict[str, str]] = []
    level = "low"
    for needle, why in _HIGH:
        if _hit(folded, needle):
            hits.append({"term": needle, "signal": why, "level": "high"})
            level = "high"
    if level != "high":
        for needle, why in _MEDIUM:
            if _hit(folded, needle):
                hits.append({"term": needle, "signal": why, "level": "medium"})
                level = "medium"
    note = (
        "Heuristik ohne Modell, nur Schlüsselwörter. "
        "Sie ersetzt weder die Risikomatrix noch ein Review."
    )
    if not text.strip():
        note = "Leere Beschreibung: kein Signal, Vorschlag low ist ein Platzhalter."
    return {"suggested": level, "hits": hits, "note": note}


def _hit(folded: str, needle: str) -> bool:
    if " " in needle:
        return needle in folded
    return re.search(rf"\b{re.escape(needle)}\b", folded) is not None


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest a test risk level from text.")
    parser.add_argument("text", help="Requirement or change description")
    args = parser.parse_args()
    print(json.dumps(suggest_risk(args.text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
