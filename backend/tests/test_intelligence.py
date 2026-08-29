from datetime import UTC, datetime, timedelta

from app.services.intelligence import infer_topic, similarity, trend_score


def test_related_titles_score_higher_than_unrelated_titles():
    related = similarity(
        "OpenAI launches a new reasoning model", "New OpenAI reasoning model launches"
    )
    unrelated = similarity(
        "OpenAI launches a new reasoning model", "Linux kernel security patch released"
    )
    assert related > unrelated
    assert related >= 0.42


def test_topic_inference_uses_title_and_categories():
    assert infer_topic("Critical Linux security vulnerability fixed", []) == "Cybersecurity"
    assert infer_topic("A completely neutral headline", ["AI"]) == "Artificial intelligence"


def test_recent_diverse_coverage_trends_higher():
    now = datetime.now(UTC)
    assert trend_score(5, 4, now) > trend_score(5, 1, now - timedelta(hours=48))
