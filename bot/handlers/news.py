from aiogram import Router
from aiogram.types import Message

from database.connection import AsyncSessionLocal
from services.news_ranker import get_top_news
from services.topic_detector import detect_topics
from services.breaking_news import detect_breaking_news

from cache.redis_client import redis_client

import re


router = Router()

CACHE_KEY = "latest_news_report"
CACHE_TTL = 60 * 30  # 30 minutes


# ----------------------------
# Text cleaning
# ----------------------------

def clean_text(text: str):

    if not text:
        return ""

    # remove HTML
    text = re.sub(r"<.*?>", "", text)

    # remove extra newline
    text = text.replace("\n", " ").strip()

    return text


# ----------------------------
# Topic message
# ----------------------------

def build_topic_message(topics):

    text = "🔥 موضوعات داغ:\n\n"

    if topics:

        for i, topic in enumerate(topics, start=1):

            if isinstance(topic, tuple):
                topic_name = topic[0]
            else:
                topic_name = topic

            text += f"{i}️⃣ {topic_name}\n"

    return text


# ----------------------------
# News message
# ----------------------------

def build_news_message(news):

    summary = news.summary

    if not summary:
        summary = news.content[:200] if news.content else ""

    summary = clean_text(summary)

    text = (
        f"📰 {news.title}\n\n"
        f"{summary}\n\n"
        f"{news.url}"
    )

    return text


# ----------------------------
# Send news list
# ----------------------------

async def send_news_list(message: Message, topics, news_list):

    # Breaking news detection
    breaking = detect_breaking_news(news_list)

    if breaking:

        alert = "🚨 خبر فوری:\n\n"

        for title in breaking:
            alert += f"• {title}\n"

        await message.answer(alert)


    # Topics
    topic_text = build_topic_message(topics)
    await message.answer(topic_text)


    # Send news (one message per news)
    for news in news_list:

        text = build_news_message(news)

        await message.answer(text)


# ----------------------------
# Telegram handler
# ----------------------------

@router.message(lambda m: m.text == "چه خبر از ایران؟")
async def latest_news(message: Message):

    cached = redis_client.get(CACHE_KEY)

    # اگر cache وجود داشت فقط پیام ساده بده
    if cached:

        await message.answer("⏱ در حال حاضر آخرین گزارش ارسال شده است. کمی بعد دوباره امتحان کنید.")
        return


    async with AsyncSessionLocal() as session:

        news_list = await get_top_news(session, limit=20)

        topics = detect_topics(session)

        await send_news_list(message, topics, news_list)

        # set cache
        redis_client.setex(CACHE_KEY, CACHE_TTL, "sent")
