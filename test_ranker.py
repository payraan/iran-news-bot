import asyncio

from database.connection import AsyncSessionLocal
from database.queries import get_latest_news

from services.news_ranker import rank_news


async def main():

    async with AsyncSessionLocal() as session:

        news = await get_latest_news(session)

        ranked = rank_news(news)

        for n in ranked[:5]:
            print(n.title)


asyncio.run(main())
