import asyncio

from database.connection import AsyncSessionLocal
from services.news_ranker import get_top_news


async def main():

    async with AsyncSessionLocal() as session:

        ranked_news = await get_top_news(session)

        for news in ranked_news:
            print(news.title)


if __name__ == "__main__":
    asyncio.run(main())
