from collections import Counter


# ----------------------------
# Geopolitical signal keywords
# ----------------------------

SIGNAL_KEYWORDS = {

    "military_escalation": [
        "missile",
        "drone",
        "strike",
        "attack",
        "military",
        "airstrike",
        "bomb",
        "explosion"
    ],

    "economic_pressure": [
        "sanctions",
        "inflation",
        "currency",
        "rial",
        "economy",
        "oil price",
        "energy crisis"
    ],

    "internal_unrest": [
        "protest",
        "demonstration",
        "riot",
        "arrest",
        "crackdown",
        "security forces"
    ],

    "diplomatic_activity": [
        "negotiation",
        "talks",
        "agreement",
        "meeting",
        "diplomatic",
        "delegation"
    ],

    "energy_market_shock": [
        "oil",
        "opec",
        "barrel",
        "energy",
        "hormuz"
    ]
}


# ----------------------------
# Detect geopolitical signals
# ----------------------------

def detect_geopolitical_signals(news_list):

    counter = Counter()

    for news in news_list:

        text = (news.title + " " + (news.summary or "")).lower()

        for signal, keywords in SIGNAL_KEYWORDS.items():

            for kw in keywords:

                if kw in text:

                    counter[signal] += 1
                    break

    return counter.most_common()
