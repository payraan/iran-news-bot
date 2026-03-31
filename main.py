import asyncio
import logging

# تنظیمات حرفه‌ای برای نمایش گزارش لحظه‌به‌لحظه در ترمینال
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

from bot.bot import start_bot
from scheduler.jobs import start_scheduler

async def main():
    logging.info("Starting Project ORACLE Server...")
    start_scheduler()
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shut down manually.")
