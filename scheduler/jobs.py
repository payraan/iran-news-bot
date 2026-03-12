import asyncio

from services.news_collector.rss_collector import collect_rss_news
from services.news_processor import process_news


async def run_news_pipeline():

    print("Starting news pipeline...")

    await collect_rss_news()

    await process_news()

    print("News pipeline completed.")

from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()


def start_scheduler():

    scheduler.add_job(
        lambda: asyncio.create_task(run_news_pipeline()),
        "interval",
        hours=4
    )

    scheduler.start()
