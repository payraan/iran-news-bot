from google import genai
from config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_news_sentiment(title: str, summary: str) -> float:
    text = f"{title} {summary}"
    prompt = f"""
تو یک تحلیلگر احساسات هستی. 
بر اساس این خبر، فقط یک عدد بین -1 تا 1 بده.
-1 یعنی به شدت منفی/پرتنش
0 یعنی خنثی
1 یعنی مثبت/آرام‌بخش

خبر: {text}

فقط عدد را بنویس، بدون هیچ کلمه اضافه‌ای.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        score = float(response.text.strip())
        return max(-1.0, min(1.0, score))
    except Exception as e:
        print("Sentiment Analysis error:", e)
        return 0.0
