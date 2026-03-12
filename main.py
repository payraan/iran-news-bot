import asyncio

from bot.bot import start_bot
from scheduler.jobs import start_scheduler


async def main():

    # start background scheduler
    start_scheduler()

    # start telegram bot
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
