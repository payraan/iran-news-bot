import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models import News

async def check_status():
    async with AsyncSessionLocal() as session:
        total = await session.scalar(select(func.count(News.id)))
        with_summary = await session.scalar(select(func.count(News.id)).where(News.summary != None))
        
        twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)
        recent = await session.scalar(select(func.count(News.id)).where(News.created_at >= twelve_hours_ago))
        
        print("=================================")
        print(" 📊 SYSTEM DIAGNOSTIC REPORT")
        print("=================================")
        print(f"🔸 کل اخبار دیتابیس: {total}")
        print(f"🔹 اخباری که خلاصه شدند: {with_summary}")
        print(f"⏰ اخبار جمع‌آوری شده در ۱۲ ساعت گذشته: {recent}")
        print("=================================")

if __name__ == "__main__":
    asyncio.run(check_status())
