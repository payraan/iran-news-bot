from datetime import datetime, timedelta
from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import News

from services.topic_detector import detect_topics
from services.news_cluster import cluster_news
from services.news_ranker import importance_score
from services.geopolitical_signals import detect_geopolitical_signals

async def build_weekly_report():

    async with AsyncSessionLocal() as session:

        # -------------------------
        # get last 7 days news
        # -------------------------

        window = datetime.utcnow() - timedelta(days=7)

        result = await session.execute(
            select(News)
            .where(News.published_at > window)
            .where(News.summary != None)
        )

        news_list = result.scalars().all()

        if not news_list:
            return "در ۷ روز گذشته داده خبری کافی برای تحلیل وجود ندارد."

        # -------------------------
        # cluster similar news
        # -------------------------

        clusters = cluster_news(news_list)

        representatives = []

        for cluster in clusters:
            best = max(cluster, key=lambda n: importance_score(n))
            representatives.append(best)

        # -------------------------
        # ranking
        # -------------------------

        scored = []

        for news in representatives:
            score = importance_score(news)
            scored.append((score, news))

        scored.sort(key=lambda x: x[0], reverse=True)

        top_news = [n for _, n in scored[:20]]

        # -------------------------
        # topic detection
        # -------------------------

        topics = detect_topics(top_news)

        # -------------------------
        # geopolitical signals
        # -------------------------

        signals = detect_geopolitical_signals(top_news)

        # -------------------------
        # sentiment distribution
        # -------------------------

        negative = 0
        neutral = 0
        positive = 0

        for news in news_list:

            if news.sentiment is None:
                continue

            if news.sentiment < 0:
                negative += 1
            elif news.sentiment > 0:
                positive += 1
            else:
                neutral += 1

        total_sentiment = negative + neutral + positive

        if total_sentiment > 0:

            neg_pct = round((negative / total_sentiment) * 100)
            neu_pct = round((neutral / total_sentiment) * 100)
            pos_pct = round((positive / total_sentiment) * 100)

        else:

            neg_pct = neu_pct = pos_pct = 0

        # -------------------------
        # build report
        # -------------------------

        report = "تحلیل خبرهای ۷ روز گذشته درباره ایران\n\n"

        report += f"تعداد کل خبرها: {len(news_list)}\n"
        report += f"تعداد خبرهای یکتا بعد از حذف تکراری‌ها: {len(representatives)}\n\n"

        report += "توزیع احساس اخبار:\n"
        report += f"- منفی: {neg_pct}%\n"
        report += f"- خنثی: {neu_pct}%\n"
        report += f"- مثبت: {pos_pct}%\n\n"

        report += "موضوعات اصلی:\n"

        for topic, count in topics:
            report += f"- {topic} ({count} خبر)\n"

        report += "\nسیگنال‌های ژئوپلیتیک:\n"

        for signal, count in signals:
            report += f"- {signal} ({count})\n"

        report += "\nمهم‌ترین خبرهای هفته:\n"

        for news in top_news:
            report += f"- {news.title}\n"

        return report
