from datetime import datetime, timedelta
from sqlalchemy import select

from database.models import News

from services.news_cluster import cluster_news


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

        if key.lower() in (source or "").lower():
            return SOURCE_WEIGHTS[key]

    return 1


def recency_score(published_at):

    hours = (datetime.utcnow() - published_at).total_seconds() / 3600

    return max(0, 10 - hours)


def importance_score(news):

    s_score = source_score(news.source)
    r_score = recency_score(news.published_at)

    score = (0.6 * s_score) + (0.4 * r_score)

    return score


async def get_top_news(session, limit=15):

    window = datetime.utcnow() - timedelta(hours=12)

    result = await session.execute(
        select(News).where(News.published_at > window)
    )

    news_list = result.scalars().all()

    # -----------------------
    # cluster similar news
    # -----------------------

    clusters = cluster_news(news_list)

    representatives = []

    for cluster in clusters:

        # انتخاب بهترین خبر داخل هر cluster
        best = max(cluster, key=lambda n: importance_score(n))

        representatives.append(best)

    # -----------------------
    # ranking
    # -----------------------

    scored = []

    for news in representatives:

        score = importance_score(news)

        scored.append((score, news))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [n for _, n in scored[:limit]]
