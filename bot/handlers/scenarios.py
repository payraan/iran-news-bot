from aiogram import Router
from aiogram.types import Message

from cache.redis_client import redis_client
from services.scenario_generator import generate_scenarios


router = Router()

CACHE_KEY = "latest_scenarios"
CACHE_TTL = 60 * 60 * 4

MAX_MESSAGE_LENGTH = 4000


def split_text(text, size=MAX_MESSAGE_LENGTH):
    return [text[i:i + size] for i in range(0, len(text), size)]


@router.message(lambda m: m.text == "آینده ایران چی میشه؟")
async def future_scenarios(message: Message):

    cached = redis_client.get(CACHE_KEY)

    if cached:
        parts = split_text(cached)

        for part in parts:
            await message.answer(part)

        return

    scenarios = await generate_scenarios()

    redis_client.setex(
        CACHE_KEY,
        CACHE_TTL,
        scenarios
    )

    parts = split_text(scenarios)

    for part in parts:
        await message.answer(part)
