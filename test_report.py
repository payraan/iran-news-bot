import asyncio
from services.scenario_generator import generate_daily_report_text
from cache.redis_client import redis_client

async def main():
    print("🚀 Force-starting 24h AI Report Generation...")
    
    # اجرای مستقیم تابع هوش مصنوعی
    report = await generate_daily_report_text()
    
    # ذخیره اجباری در کشِ داشبورد
    redis_client.set("daily_report", report)
    
    print("✅ Report successfully generated and pushed to Redis!")
    print("Refresh your Cyberpunk Dashboard now.")

if __name__ == "__main__":
    asyncio.run(main())
