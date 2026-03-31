import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.news_collector.rss_collector import collect_rss_news
from services.news_processor import process_news
from services.news_retention import cleanup_old_news
from services.scenario_generator import generate_daily_report_text
from cache.redis_client import redis_client

async def run_news_pipeline():
    print("--- Starting Scheduled News Pipeline (Every 15m) ---")
    
    # ۱. جمع‌آوری اخبار جدید از تمام منابع
    await collect_rss_news()

    # ۲. تحلیل، خلاصه سازی و امتیازدهی توسط جمینای
    await process_news()

    # ۳. بروزرسانی گزارش تحلیلی ۲۴ ساعته روی داشبورد
    print("Generating 24h AI report...")
    try:
        daily_report = await generate_daily_report_text()
        redis_client.set("daily_report", daily_report)
        print("24h AI report updated on dashboard.")
    except Exception as e:
        print(f"Failed to generate 24h report: {e}")

    print("--- News pipeline completed. ---")

scheduler = AsyncIOScheduler()

def start_scheduler():
    # تغییر بازه زمانی به ۱۵ دقیقه (بجای ۱ ساعت)
    scheduler.add_job(
        lambda: asyncio.create_task(run_news_pipeline()),
        "interval",
        minutes=15
    )

    # پاک کردن خبرهای بسیار قدیمی (هر ۱۲ ساعت یک‌بار)
    scheduler.add_job(
        lambda: asyncio.create_task(cleanup_old_news()),
        "interval",
        hours=12
    )

    scheduler.start()
