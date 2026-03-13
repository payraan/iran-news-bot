from datetime import datetime, timedelta
from sqlalchemy import delete

from database.connection import AsyncSessionLocal
from database.models import News


async def cleanup_old_news():

    async with AsyncSessionLocal() as session:

        cutoff = datetime.utcnow() - timedelta(days=7)

        await session.execute(
            delete(News).where(News.published_at < cutoff)
        )

        await session.commit()

        print("Old news cleanup completed.")
