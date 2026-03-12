from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import News

from services.summarizer import summarize_news


async def process_news():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(News).where(News.summary == None)
        )

        news_items = result.scalars().all()

        for news in news_items:

            summary = await summarize_news(
                news.title,
                news.content or ""
            )

            news.summary = summary

        await session.commit()
