from datetime import datetime, timedelta
from sqlalchemy import select

from database.models import News


SOURCE_WEIGHTS = {
    "Reuters": 5,
    "The Guardian": 4,
    "The Economist": 4,
    "New York Times": 4,
    "BBC": 4,
    "NBC News": 3,
    "Al Jazeera": 3
}


def source_score(source: str):
    for key in SOURCE_WEIGHTS:
        if key.lower() in source.lower():
            return SOURCE_WEIGHTS[key]
    return 1


def recency_score(published_at):
    hours = (datetime.utcnow() - published_at).total_seconds() / 3600
    return max(0, 10 - hours)


def importance_score(news):

    s_score = source_score(news.source or "")
    r_score = recency_score(news.published_at)

    score = (0.6 * s_score) + (0.4 * r_score)

    return score


async def get_top_news(session, limit=15):

    # فقط خبرهای 48 ساعت اخیر
    window = datetime.utcnow() - timedelta(hours=12)

    result = await session.execute(
        select(News)
        .where(News.published_at > window)
    )

    news_list = result.scalars().all()

    scored = []

    for news in news_list:
        score = importance_score(news)
        scored.append((score, news))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [n for _, n in scored[:limit]]
