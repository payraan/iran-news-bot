import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models import News

async def main():
    async with AsyncSessionLocal() as session:
        total = await session.scalar(select(func.count(News.id)))
        with_summary = await session.scalar(select(func.count(News.id)).where(News.summary != None))
        print("📊 وضعیت دیتابیس:")
        print(f"🔸 کل اخبار جمع‌آوری شده: {total}")
        print(f"🔹 اخباری که با جمینای خلاصه شدند: {with_summary}")

if __name__ == "__main__":
    asyncio.run(main())
