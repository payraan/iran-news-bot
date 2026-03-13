from collections import Counter


def detect_breaking_news(news_list, threshold=3):

    """
    اگر یک عنوان خبر در چند منبع تکرار شود
    به عنوان breaking news در نظر گرفته می‌شود
    """

    titles = [n.title for n in news_list if n.title]

    counter = Counter(titles)

    breaking = []

    for title, count in counter.items():

        if count >= threshold:
            breaking.append(title)

    return breaking
