from google import genai
from config.settings import settings

from services.trend_analyzer import build_weekly_report


client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_scenarios():

    # -------------------------
    # build weekly analysis report
    # -------------------------

    weekly_report = await build_weekly_report()

    if not weekly_report:
        return "در ۷ روز گذشته داده خبری کافی برای تحلیل وجود ندارد."

    # -------------------------
    # build AI prompt
    # -------------------------

    prompt = f"""
تو یک تحلیلگر ژئوپلیتیک هستی.

بر اساس گزارش تحلیلی زیر از خبرهای ۷ روز گذشته درباره ایران،
سناریوهای احتمالی برای هفته آینده در ایران را پیش‌بینی کن.

قوانین مهم:

- فقط از اطلاعات موجود در گزارش استفاده کن
- اطلاعات جدید یا فرضی اضافه نکن
- تحلیل منطقی و واقع‌گرایانه باشد
- هر سناریو حداکثر 4 جمله باشد
- پاسخ به زبان فارسی باشد

ساختار پاسخ باید دقیقاً این باشد:

🔮 پیش‌بینی هفته آینده در ایران

🔴 بدترین سناریو
(تحلیل کوتاه)

🟡 سناریوی محتمل
(تحلیل کوتاه)

🟢 بهترین سناریو
(تحلیل کوتاه)

گزارش تحلیلی:
{weekly_report}
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

async def generate_daily_report_text():
    from datetime import datetime, timedelta
    from sqlalchemy import select
    from database.connection import AsyncSessionLocal
    from database.models import News

    async with AsyncSessionLocal() as session:
        window = datetime.utcnow() - timedelta(hours=24)
        result = await session.execute(
            select(News).where(News.published_at > window).where(News.summary != None)
        )
        news_list = result.scalars().all()

        if not news_list:
            return "در ۲۴ ساعت گذشته خبر مهمی برای تحلیل یافت نشد."

        news_summaries = "\n".join([f"- {n.title}" for n in news_list[:30]])

        prompt = f"""
        تو یک تحلیلگر ارشد اخبار هستی. اخبار ۲۴ ساعت گذشته ایران را در یک پاراگراف کوتاه (حداکثر 4 خط) به زبان فارسی تحلیل و خلاصه کن. 
        لحنت حرفه‌ای، بی‌احساس و شبیه به گزارش‌های محرمانه باشد.
        
        اخبار:
        {news_summaries}
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return response.text
        except:
            return "خطا در ارتباط با هوش مصنوعی برای تحلیل ۲۴ ساعته."
