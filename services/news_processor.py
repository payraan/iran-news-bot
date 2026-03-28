from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import News

from services.summarizer import summarize_news
from services.sentiment_analyzer import analyze_news_sentiment


BATCH_SIZE = 50


async def process_news():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(News)
            .where(News.summary == None)
            .order_by(News.published_at.desc())
            .limit(BATCH_SIZE)
        )

        news_items = result.scalars().all()

        if not news_items:
            print("No news to process.")
            return

        print(f"Processing {len(news_items)} news summaries...")

        for news in news_items:

            try:

                summary = await summarize_news(
                    news.title,
                    news.content or ""
                )

                news.summary = summary

                # ----------------------------
                # Sentiment analysis
                # ----------------------------

                sentiment_score = await analyze_news_sentiment(
                    news.title,
                    summary
                )

                news.sentiment = sentiment_score

            except Exception as e:

                print(f"Processing failed for: {news.title}")
                print(e)
                continue

        await session.commit()

        print("News processing batch completed.")
