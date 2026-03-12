from google import genai
from config.settings import settings

from database.connection import AsyncSessionLocal
from database.models import News

from sqlalchemy import select


client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_scenarios():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(News)
            .where(News.summary != None)
            .order_by(News.published_at.desc())
            .limit(15)
        )

        news_list = result.scalars().all()

        if not news_list:
            return "داده خبری کافی برای تحلیل وجود ندارد."

        news_text = ""

        for news in news_list:
            news_text += f"خبر: {news.title}\n"
            news_text += f"خلاصه: {news.summary}\n\n"

    prompt = f"""
تو یک تحلیلگر ژئوپلیتیک هستی.

بر اساس خبرهای زیر درباره ایران، آینده کوتاه‌مدت ایران را تحلیل کن.

قوانین مهم:
- فقط از اطلاعات موجود در خبرها استفاده کن
- اگر خبری به ایران مربوط نیست آن را نادیده بگیر
- اطلاعات جدید یا فرضی اضافه نکن
- تحلیل مختصر و واضح باشد
- هر سناریو حداکثر 4 جمله باشد
- پاسخ به زبان فارسی باشد

ساختار پاسخ باید دقیقاً این باشد:

🔴 بدترین سناریو
(تحلیل کوتاه)

🟡 سناریوی محتمل
(تحلیل کوتاه)

🟢 بهترین سناریو
(تحلیل کوتاه)

خبرها:
{news_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Scenario generation error:", e)

        return "در حال حاضر امکان تحلیل سناریو وجود ندارد."
