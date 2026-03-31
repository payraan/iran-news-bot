import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import News
from database.queries import news_exists

# اسم کانال‌های عمومی تلگرام (بدون @)
CHANNELS = ["AdsVipz", "IranintlTV", "bbcpersian"]

# فیلتر هوشمند برای اینکه تبلیغات کانال‌ها رو به عنوان خبر ذخیره نکنیم
IRAN_KEYWORDS = [
    "iran", "tehran", "ایران", "تهران", "خامنه‌ای", "سپاه", "تحریم", 
    "اسرائیل", "دلار", "تورم", "جنگ", "دولت", "نظامی", "حمله", "اقتصاد"
]

def is_relevant(text: str) -> bool:
    text = text.lower()
    for kw in IRAN_KEYWORDS:
        if kw in text:
            return True
    return False

async def scrape_channel(channel: str, session):
    url = f"https://t.me/s/{channel}"
    
    # تغییر هویت ربات به مرورگر کرومِ ویندوز برای فریب سیستم امنیتی تلگرام
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            response = await client.get(url, timeout=15.0)
            if response.status_code != 200:
                print(f"Failed to fetch @{channel}: {response.status_code}")
                return

            # شکافتن کدهای HTML سایت تلگرام
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message')

            for msg in messages:
                text_div = msg.find('div', class_='tgme_widget_message_text')
                if not text_div:
                    continue
                
                content = text_div.get_text(separator='\n', strip=True)
                
                # دور ریختن پیام‌های تبلیغاتی و بی‌ربط
                if not is_relevant(content):
                    continue

                # استخراج لینک اختصاصی اون خبر در تلگرام
                date_a = msg.find('a', class_='tgme_widget_message_date')
                if not date_a or not date_a.get('href'):
                    continue
                msg_url = date_a['href']

                # بررسی اینکه آیا قبلاً این خبر رو خوندیم یا نه
                exists = await news_exists(session, msg_url)
                if exists:
                    continue

                # استخراج زمان انتشار
                time_tag = date_a.find('time')
                published_at = datetime.utcnow()
                if time_tag and time_tag.get('datetime'):
                    try:
                        published_at = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00')).replace(tzinfo=None)
                    except Exception:
                        pass

                # چون تلگرام تایتل نداره، ۶۰ حرف اول رو می‌کنیم تیتر خبر
                title = content[:60] + "..." if len(content) > 60 else content

                news = News(
                    title=title.replace('\n', ' '),
                    content=content,
                    source=f"Telegram (@{channel})",
                    url=msg_url,
                    published_at=published_at
                )
                session.add(news)

    except Exception as e:
        print(f"Error scraping Telegram @{channel}: {e}")

async def collect_telegram_news():
    print("Starting Telegram Web Scraping...")
    async with AsyncSessionLocal() as session:
        for channel in CHANNELS:
            await scrape_channel(channel, session)
            # دو ثانیه صبر می‌کنیم تا تلگرام متوجه ربات بودن ما نشه
            await asyncio.sleep(2) 
        await session.commit()
        print("Telegram collection completed.")
