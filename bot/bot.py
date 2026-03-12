import asyncio

from aiogram import Bot, Dispatcher

from config.settings import settings
from bot.handlers import start
from bot.handlers import news


async def start_bot():

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(news.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
