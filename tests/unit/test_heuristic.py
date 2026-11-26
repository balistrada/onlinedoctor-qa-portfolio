from qa_portfolio.ai_review.heuristic import suggest_risk


def test_payment_language_is_high() -> None:
    result = suggest_risk("Stripe checkout collects payment data")
    assert result["suggested"] == "high"
    assert any(hit["term"] == "payment" for hit in result["hits"])
    assert "kein" in result["note"].lower() or "Heuristik" in result["note"]


def test_sitemap_without_payment_is_medium() -> None:
    result = suggest_risk("Update the sitemap index")
    assert result["suggested"] == "medium"


def test_empty_text_stays_low() -> None:
    result = suggest_risk("   ")
    assert result["suggested"] == "low"
    assert result["hits"] == []


def test_auth_inside_a_word_does_not_fire() -> None:
    result = suggest_risk("authoritative copy on the homepage")
    assert result["suggested"] == "low"
