from sqlalchemy import select
from database.models import News


async def get_latest_news(session, limit=5):

    result = await session.execute(
        select(News)
        .where(News.summary != None)
        .order_by(News.published_at.desc())
        .limit(limit)
    )

    return result.scalars().all()
