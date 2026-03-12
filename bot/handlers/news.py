from aiogram import Router
from aiogram.types import Message

from database.connection import AsyncSessionLocal
from database.queries import get_latest_news


router = Router()


@router.message(lambda m: m.text == "چه خبر از ایران؟")
async def latest_news(message: Message):

    async with AsyncSessionLocal() as session:

        news_list = await get_latest_news(session)

        if not news_list:
            await message.answer("فعلاً خبری در دسترس نیست.")
            return

        text = "📰 مهم‌ترین خبرهای اخیر ایران:\n\n"

        for news in news_list:

            text += f"🔹 {news.title}\n"
            text += f"{news.summary}\n\n"

        await message.answer(text)
