from aiogram import Router
from aiogram.types import Message

from database.connection import AsyncSessionLocal
from services.news_ranker import get_top_news
from services.topic_detector import detect_topics

from cache.redis_client import redis_client

import re


router = Router()

CACHE_KEY = "latest_news_report"
CACHE_TTL = 60 * 30  # 30 minutes


def clean_text(text: str):

    if not text:
        return ""

    # حذف HTML
    text = re.sub(r"<.*?>", "", text)

    # حذف newline اضافی
    text = text.replace("\n", " ").strip()

    return text


def build_message(topics, news_list):

    text = "🔥 موضوعات داغ:\n\n"

    if topics:
        for i, topic in enumerate(topics, start=1):

            if isinstance(topic, tuple):
                topic_name = topic[0]
            else:
                topic_name = topic

            text += f"{i}️⃣ {topic_name}\n"

    text += "\n📰 مهم‌ترین خبرهای اخیر ایران:\n\n"

    for news in news_list:

        summary = news.summary

        if not summary:
            summary = news.content[:200] if news.content else ""

        summary = clean_text(summary)

        text += f"🔹 {news.title}\n"
        text += f"{summary}\n"
        text += f"{news.url}\n\n"

    return text


async def send_long_message(message: Message, text: str):

    MAX_LENGTH = 4000

    for i in range(0, len(text), MAX_LENGTH):
        chunk = text[i:i + MAX_LENGTH]
        await message.answer(chunk)


@router.message(lambda m: m.text == "چه خبر از ایران؟")
async def latest_news(message: Message):

    cached = redis_client.get(CACHE_KEY)

    if cached:
        await send_long_message(message, cached)
        return

    async with AsyncSessionLocal() as session:

        news_list = await get_top_news(session)

        topics = detect_topics(session)

        text = build_message(topics, news_list)

        redis_client.setex(CACHE_KEY, CACHE_TTL, text)

        await send_long_message(message, text)
