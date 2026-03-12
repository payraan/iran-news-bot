from google import genai
from config.settings import settings
import asyncio


client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def summarize_news(title: str, content: str):

    prompt = f"""
تو یک تحلیلگر اخبار ژئوپلیتیک هستی.

خبر زیر را در ۳ تا ۵ جمله کوتاه **به زبان فارسی** خلاصه کن.

قوانین:
- فقط فارسی بنویس
- خلاصه واضح و قابل فهم باشد
- تحلیل اضافه نکن
- فقط خلاصه خبر را بده

عنوان خبر:
{title}

متن خبر:
{content}
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text

        except Exception as e:

            print("Gemini error:", e)

            await asyncio.sleep(2)

    return "خلاصه خبر در حال حاضر در دسترس نیست."
