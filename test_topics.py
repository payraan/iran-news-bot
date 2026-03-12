import asyncio

from database.connection import AsyncSessionLocal
from database.queries import get_latest_news

from services.topic_detector import detect_topics


async def main():

    async with AsyncSessionLocal() as session:

        news = await get_latest_news(session)

        topics = detect_topics(news)

        print("\n🔥 موضوعات داغ:\n")

        for topic, count in topics:

            print(topic, count)


asyncio.run(main())
