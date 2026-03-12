import asyncio
from services.news_processor import process_news


async def main():
    await process_news()
    print("News processing completed")


if __name__ == "__main__":
    asyncio.run(main())
