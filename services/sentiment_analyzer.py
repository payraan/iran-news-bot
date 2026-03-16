from transformers import pipeline

# ----------------------------
# Load sentiment model once
# ----------------------------

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)


# ----------------------------
# Convert label to numeric score
# ----------------------------

def label_to_score(label: str):

    label = label.lower()

    if "negative" in label:
        return -1

    if "neutral" in label:
        return 0

    if "positive" in label:
        return 1

    return 0


# ----------------------------
# Analyze single text sentiment
# ----------------------------

def analyze_sentiment(text: str):

    if not text:
        return 0

    try:
        result = sentiment_pipeline(text[:512])[0]

        label = result["label"]

        return label_to_score(label)

    except Exception:
        return 0


# ----------------------------
# Analyze news item sentiment
# ----------------------------

def analyze_news_sentiment(title: str, summary: str):

    text = f"{title} {summary}"

    return analyze_sentiment(text)
