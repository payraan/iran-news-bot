from collections import Counter


TOPIC_KEYWORDS = {
    "برنامه هسته‌ای": [
        "nuclear",
        "uranium",
        "enrichment",
        "atomic"
    ],

    "تنش ایران و اسرائیل": [
        "israel",
        "hezbollah",
        "tel aviv",
        "missile"
    ],

    "تحریم‌ها": [
        "sanctions",
        "embargo",
        "restriction"
    ],

    "بازار نفت": [
        "oil",
        "energy",
        "barrel",
        "opec"
    ],

    "اقتصاد ایران": [
        "economy",
        "inflation",
        "currency",
        "rial"
    ]
}


def detect_topics(news_list):

    counter = Counter()

    for news in news_list:

        text = (news.title + " " + (news.content or "")).lower()

        for topic, keywords in TOPIC_KEYWORDS.items():

            for kw in keywords:

                if kw in text:

                    counter[topic] += 1

                    break

    return counter.most_common(5)
