import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


settings = Settings()
