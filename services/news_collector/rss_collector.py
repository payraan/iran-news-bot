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


IRAN_KEYWORDS = [
    "iran",
    "iranian",
    "tehran",
    "khamenei",
    "ayatollah",
    "israel iran",
    "iran nuclear",
    "iran missile",
    "iran sanctions",
    "iran oil",
    "persian gulf"
]


def is_about_iran(title: str, content: str) -> bool:
    """
    بررسی می‌کند آیا خبر مربوط به ایران است یا نه
    """

    text = f"{title} {content}".lower()

    return any(keyword in text for keyword in IRAN_KEYWORDS)


async def collect_rss_news():

    async with AsyncSessionLocal() as session:

        # گرفتن embedding خبرهای قبلی
        result = await session.execute(select(News.embedding))

        existing_embeddings = []

        for row in result.fetchall():
            if row[0]:
                try:
                    existing_embeddings.append(eval(row[0]))
                except Exception:
                    continue

        for feed_url in RSS_FEEDS:

            try:
                feed = feedparser.parse(feed_url)
            except Exception:
                continue

            if not feed.entries:
                continue

            for entry in feed.entries[:10]:

                title = entry.title if hasattr(entry, "title") else ""
                content = entry.get("summary", "") if hasattr(entry, "get") else ""

                # فیلتر خبرهای غیر مرتبط با ایران
                if not is_about_iran(title, content):
                    continue

                # بررسی duplicate URL
                try:
                    exists = await news_exists(session, entry.link)
                    if exists:
                        continue
                except Exception:
                    continue

                # ساخت embedding
                try:
                    embedding = compute_embedding(title)
                except Exception:
                    continue

                # semantic duplicate detection
                if is_duplicate(embedding, existing_embeddings):
                    continue

                try:
                    news = News(
                        title=title,
                        content=content,
                        source=feed.feed.get("title", "unknown"),
                        url=entry.link,
                        embedding=str(embedding.tolist()),
                        published_at=datetime.utcnow()
                    )

                    session.add(news)

                    existing_embeddings.append(embedding.tolist())

                except Exception:
                    continue

        await session.commit()
