import math
import re
from datetime import UTC, datetime

STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "for",
    "from",
    "in",
    "is",
    "it",
    "new",
    "of",
    "on",
    "the",
    "to",
    "with",
}
TOPICS = {
    "Artificial intelligence": {"ai", "artificial", "chatgpt", "llm", "model", "openai"},
    "Cybersecurity": {"breach", "cybersecurity", "hack", "malware", "security", "vulnerability"},
    "Cloud & infrastructure": {"aws", "cloud", "database", "kubernetes", "server"},
    "Developer ecosystem": {"developer", "github", "linux", "open-source", "python"},
    "Consumer technology": {"android", "apple", "device", "google", "iphone"},
}


def title_tokens(title: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]+", title.lower())
        if token not in STOP_WORDS and (len(token) > 2 or token == "ai")
    }


def similarity(left: str, right: str) -> float:
    a, b = title_tokens(left), title_tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0


def infer_topic(title: str, categories: list[str]) -> str:
    tokens = title_tokens(f"{title} {' '.join(categories)}")
    scores = {topic: len(tokens & keywords) for topic, keywords in TOPICS.items()}
    topic, score = max(scores.items(), key=lambda item: item[1])
    return topic if score else "Technology"


def trend_score(article_count: int, source_count: int, last_seen: datetime) -> float:
    age_hours = max((datetime.now(UTC) - last_seen).total_seconds() / 3600, 0)
    recency = math.exp(-age_hours / 36)
    diversity = min(source_count / 4, 1)
    coverage = min(math.log1p(article_count) / math.log(8), 1)
    return round(100 * recency * (0.6 * diversity + 0.4 * coverage), 1)
