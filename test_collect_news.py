import asyncio

from services.news_collector.rss_collector import collect_rss_news


async def main():
    await collect_rss_news()
    print("News collection completed")


if __name__ == "__main__":
    asyncio.run(main())
