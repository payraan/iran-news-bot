import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.news_collector.rss_collector import collect_rss_news
from services.news_collector.telegram_collector import collect_telegram_news
from services.news_processor import process_news
from services.news_retention import cleanup_old_news
from services.scenario_generator import generate_daily_report_text
from cache.redis_client import redis_client

logger = logging.getLogger(__name__)

# قفل برای جلوگیری از اجرای همزمان pipeline
_pipeline_lock = asyncio.Lock()

# تایم‌اوت کلی برای کل pipeline (10 دقیقه)
PIPELINE_TIMEOUT = 60 * 10


async def run_news_pipeline():
    """
    Pipeline اصلی با سه لایه محافظ:
    1. Lock: جلوگیری از اجرای همزمان
    2. Timeout: جلوگیری از هنگ کردن ابدی
    3. Try/Except: جلوگیری از کرش بی‌صدا
    """

    # اگر pipeline قبلی هنوز در حال اجراست، این دور رو skip می‌کنیم
    if _pipeline_lock.locked():
        logger.warning("⚠ Pipeline already running. Skipping this cycle.")
        return

    async with _pipeline_lock:
        try:
            logger.info("--- 🚀 Starting News Pipeline ---")

            await asyncio.wait_for(
                _execute_pipeline(),
                timeout=PIPELINE_TIMEOUT
            )

            logger.info("--- ✅ News Pipeline Completed ---")

        except asyncio.TimeoutError:
            logger.error(
                f"🔴 PIPELINE TIMEOUT: Execution exceeded {PIPELINE_TIMEOUT}s. "
                "Forcing reset for next cycle."
            )
        except Exception as e:
            logger.exception(f"🔴 PIPELINE FATAL ERROR: {e}")


async def _execute_pipeline():
    """منطق اصلی pipeline که داخل تایم‌اوت اجرا می‌شه."""

    # ۱. جمع‌آوری اخبار
    logger.info("[1/3] Collecting RSS news...")
    await collect_rss_news()

    logger.info("[1/3] Collecting Telegram news...")
    await collect_telegram_news()

    # ۲. پردازش با Gemini
    logger.info("[2/3] Processing news with AI...")
    await process_news()

    # ۳. آپدیت گزارش داشبورد
    logger.info("[3/3] Generating 24h AI report...")
    try:
        daily_report = await generate_daily_report_text()
        redis_client.set("daily_report", daily_report)
        logger.info("✅ 24h report updated.")
    except Exception as e:
        # این بخش non-critical است - خطا pipeline رو متوقف نمی‌کنه
        logger.error(f"⚠ Failed to generate daily report: {e}")


async def run_cleanup():
    """پاک‌سازی اخبار قدیمی."""
    try:
        await cleanup_old_news()
    except Exception as e:
        logger.error(f"⚠ Cleanup failed: {e}")


scheduler = AsyncIOScheduler()


def start_scheduler():
    # Pipeline اصلی: هر ۱۵ دقیقه
    # نکته مهم: تابع async رو مستقیم پاس می‌دیم، نه داخل lambda
    scheduler.add_job(
        run_news_pipeline,   # ← مستقیم، بدون lambda یا create_task
        trigger="interval",
        minutes=5,
        next_run_time=datetime.now(),
        id="news_pipeline",
        max_instances=1,     # ← APScheduler خودش هم جلوی تداخل رو می‌گیره
        coalesce=True,       # ← اگر چند دور جا موند، فقط یکی اجرا بشه
        misfire_grace_time=60
    )

    # پاک‌سازی: هر ۱۲ ساعت
    scheduler.add_job(
        run_cleanup,
        trigger="interval",
        hours=12,
        id="cleanup",
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    logger.info("✅ Scheduler started.")
