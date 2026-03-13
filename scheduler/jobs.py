import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.news_collector.rss_collector import collect_rss_news
from services.news_processor import process_news
from services.news_retention import cleanup_old_news


async def run_news_pipeline():

    print("Starting news pipeline...")

    await collect_rss_news()

    await process_news()

    print("News pipeline completed.")


scheduler = AsyncIOScheduler()


def start_scheduler():

    # اجرای pipeline خبر
    scheduler.add_job(
        lambda: asyncio.create_task(run_news_pipeline()),
        "interval",
        hours=1
    )

    # پاک کردن خبرهای قدیمی
    scheduler.add_job(
        lambda: asyncio.create_task(cleanup_old_news()),
        "interval",
        hours=12
    )

    scheduler.start()
