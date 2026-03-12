from datetime import datetime
from database.models import News


SOURCE_WEIGHTS = {
    "Reuters": 3.0,
    "BBC": 2.8,
    "Al Jazeera": 2.5,
    "The Guardian": 2.3,
    "Associated Press": 2.8,
}


KEYWORDS = [
    "iran",
    "nuclear",
    "sanctions",
    "israel",
    "oil",
    "hezbollah",
    "missile",
]


def keyword_score(text: str) -> float:

    score = 0

    text_lower = text.lower()

    for kw in KEYWORDS:
        if kw in text_lower:
            score += 1

    return score


def recency_score(published_at):

    if not published_at:
        return 0

    hours = (datetime.utcnow() - published_at).total_seconds() / 3600

    if hours < 6:
        return 3

    if hours < 24:
        return 2

    if hours < 72:
        return 1

    return 0.5


def source_score(source):

    if not source:
        return 1

    return SOURCE_WEIGHTS.get(source, 1)


def compute_importance(news: News):

    score = 0

    score += recency_score(news.published_at)

    score += source_score(news.source)

    score += keyword_score(news.title + " " + (news.content or ""))

    return score


def rank_news(news_list):

    ranked = sorted(
        news_list,
        key=lambda n: compute_importance(n),
        reverse=True
    )

    return ranked
