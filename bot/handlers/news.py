from aiogram import Router
from aiogram.types import Message

from database.connection import AsyncSessionLocal
from database.queries import get_latest_news

from cache.redis_client import redis_client


router = Router()

CACHE_KEY = "latest_news_report"
CACHE_TTL = 60 * 60 * 4  # 4 hours


@router.message(lambda m: m.text == "چه خبر از ایران؟")
async def latest_news(message: Message):

    # 1️⃣ check redis cache
    cached_report = redis_client.get(CACHE_KEY)

    if cached_report:
        await message.answer(cached_report)
        return

    # 2️⃣ query database if cache miss
    async with AsyncSessionLocal() as session:

        news_list = await get_latest_news(session)

        if not news_list:
            await message.answer("فعلاً خبری در دسترس نیست.")
            return

        text = "📰 مهم‌ترین خبرهای اخیر ایران:\n\n"

        for news in news_list:

            text += f"🔹 {news.title}\n"
            text += f"{news.summary}\n"

            if news.url:
                text += f"🔗 {news.url}\n"

            text += "\n"

    # 3️⃣ save report in redis cache
    redis_client.setex(
        CACHE_KEY,
        CACHE_TTL,
        text
    )

    # 4️⃣ send message
    await message.answer(text)
