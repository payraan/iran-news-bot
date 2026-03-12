from aiogram import Router
from aiogram.types import Message

from database.connection import AsyncSessionLocal
from database.queries import get_latest_news

from services.news_ranker import rank_news
from services.topic_detector import detect_topics

from cache.redis_client import redis_client


router = Router()

CACHE_KEY = "latest_news_report"
CACHE_TTL = 60 * 30


@router.message(lambda m: m.text == "چه خبر از ایران؟")
async def latest_news(message: Message):

    cached = redis_client.get(CACHE_KEY)

    if cached:
        await message.answer(cached)
        return

    async with AsyncSessionLocal() as session:

        news_list = await get_latest_news(session)

        if not news_list:
            await message.answer("فعلاً خبری در دسترس نیست.")
            return

        # Topic detection
        topics = detect_topics(news_list)

        # Ranking
        ranked_news = rank_news(news_list)
        top_news = ranked_news[:5]

        text = "🔥 موضوعات داغ:\n\n"

        for i, (topic, count) in enumerate(topics[:3], start=1):
            text += f"{i}️⃣ {topic}\n"

        text += "\n📰 مهم‌ترین خبرهای اخیر ایران:\n\n"

        for news in top_news:

            text += f"🔹 {news.title}\n"
            text += f"{news.summary}\n"
            text += f"{news.url}\n\n"

        redis_client.setex(
            CACHE_KEY,
            CACHE_TTL,
            text
        )

        await message.answer(text)
