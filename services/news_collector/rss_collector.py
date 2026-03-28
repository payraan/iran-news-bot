import asyncio
import feedparser
import urllib.parse
from datetime import datetime
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import News
from database.queries import news_exists

# ----------------------------
# Base RSS feeds
# ----------------------------
BASE_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.reuters.com/world/middle-east/rss",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://rss.politico.com/politics-news.xml",
    "https://feeds.bbci.co.uk/persian/rss.xml",
    "https://iranwire.com/fa/feed",
]

# ----------------------------
# Google News queries
# ----------------------------
GOOGLE_NEWS_QUERIES = [
    "iran", "tehran", "iran war", "iran israel", "iran nuclear",
    "iran sanctions", "iran military", "iran economy", "iran inflation",
    "iran rial", "iran dollar", "iran oil", "iran government",
    "iran protests", "iran elections", "iran internet", "iran censorship",
    "iran cyber attack", "persian gulf tension", "strait of hormuz",
]

RSS_FEEDS = list(BASE_RSS_FEEDS)
for query in GOOGLE_NEWS_QUERIES:
    encoded = urllib.parse.quote(query)
    RSS_FEEDS.append(f"https://news.google.com/rss/search?q={encoded}")

IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "khamenei", "ayatollah",
    "israel iran", "iran nuclear", "iran missile", "iran sanctions",
    "iran oil", "persian gulf",
]

def is_about_iran(title: str, content: str) -> bool:
    text = f"{title} {content}".lower()
    # اگر حتی یک کلمه کلیدی هم پیدا شد، خبر تایید است
    for keyword in IRAN_KEYWORDS:
        if keyword in text:
            return True
    return False

def extract_source(entry, feed):
    try:
        if hasattr(entry, "source") and entry.source:
            source_title = entry.source.get("title")
            if source_title: return source_title
    except Exception: pass
    try:
        if hasattr(feed, "feed"): return feed.feed.get("title", "unknown")
    except Exception: pass
    return "unknown"

async def process_feed(feed_url, session):
    try:
        feed = feedparser.parse(feed_url)
    except Exception:
        return
    if not feed.entries:
        return

    for entry in feed.entries[:50]:
        title = getattr(entry, "title", "")
        content = entry.get("summary", "")

        if not title or not is_about_iran(title, content):
            continue

        try:
            exists = await news_exists(session, entry.link)
            if exists: continue
        except Exception:
            continue

        published = datetime.utcnow()
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6])
            except Exception:
                pass

        source = extract_source(entry, feed)

        try:
            news = News(
                title=title,
                content=content,
                source=source,
                url=entry.link,
                published_at=published
            )
            session.add(news)
        except Exception:
            continue

async def collect_rss_news():
    async with AsyncSessionLocal() as session:
        tasks = [process_feed(url, session) for url in RSS_FEEDS]
        await asyncio.gather(*tasks)
        await session.commit()
        print("RSS collection completed.")
