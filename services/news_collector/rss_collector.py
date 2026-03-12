import feedparser
from datetime import datetime

from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import News
from database.queries import news_exists

from services.duplicate_detector import compute_embedding, is_duplicate


RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://news.google.com/rss/search?q=iran"
]


async def collect_rss_news():

    async with AsyncSessionLocal() as session:

        # گرفتن embedding خبرهای قبلی
        result = await session.execute(select(News.embedding))
        existing_embeddings = [
            eval(row[0]) for row in result.fetchall() if row[0]
        ]

        for feed_url in RSS_FEEDS:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:

                # URL duplicate check
                exists = await news_exists(session, entry.link)

                if exists:
                    continue

                # ساخت embedding عنوان خبر
                embedding = compute_embedding(entry.title)

                # semantic duplicate detection
                if is_duplicate(embedding, existing_embeddings):
                    continue

                news = News(
                    title=entry.title,
                    content=entry.get("summary", ""),
                    source=feed.feed.get("title", "unknown"),
                    url=entry.link,
                    embedding=str(embedding.tolist()),
                    published_at=datetime.utcnow()
                )

                session.add(news)

        await session.commit()
