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
