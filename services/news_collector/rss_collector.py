import asyncio
import feedparser
import urllib.parse
from datetime import datetime
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import News
from database.queries import news_exists

# --- تریک هکری: تغییر User-Agent تا گوگل ما را به چشم یک کاربر واقعی (مرورگر کروم) ببیند ---
feedparser.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BASE_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.reuters.com/world/middle-east/rss",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://feeds.bbci.co.uk/persian/rss.xml",
    "https://iranwire.com/fa/feed",
]

# کوئری‌های ترکیبی برای گوگل نیوز
GOOGLE_NEWS_QUERIES = [
    "iran", "tehran", "iran war", "iran sanctions", 
    "اقتصاد ایران", "اخبار ایران", "قیمت دلار تهران"
]

RSS_FEEDS = list(BASE_RSS_FEEDS)
for query in GOOGLE_NEWS_QUERIES:
    encoded = urllib.parse.quote(query)
    RSS_FEEDS.append(f"https://news.google.com/rss/search?q={encoded}")

# --- حل باگ زبان: اضافه شدن کلمات کلیدی فارسی ---
IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "khamenei", "ayatollah", "israel", "nuclear",
    "ایران", "تهران", "خامنه‌ای", "سپاه", "تحریم", "اسرائیل", "دلار", "تورم", "جنگ"
]

def is_about_iran(title: str, content: str) -> bool:
    text = f"{title} {content}".lower()
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
        # اجرای feedparser در یک ترد (Thread) جداگانه تا سیستم هنگ نکند
        feed = await asyncio.to_thread(feedparser.parse, feed_url)
    except Exception as e:
        print(f"Error fetching {feed_url}")
        return
        
    if not feed.entries:
        return

    for entry in feed.entries[:30]:
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

        try:
            news = News(
                title=title,
                content=content,
                source=extract_source(entry, feed),
                url=entry.link,
                published_at=published
            )
            session.add(news)
        except Exception:
            continue

async def collect_rss_news():
    async with AsyncSessionLocal() as session:
        # --- حل باگ اسپم گوگل: پردازش یکی یکی با تاخیر نیم ثانیه‌ای ---
        print("Starting safe RSS collection...")
        for url in RSS_FEEDS:
            await process_feed(url, session)
            await asyncio.sleep(0.5) 
            
        await session.commit()
        print("RSS collection completed successfully.")
