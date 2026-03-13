from difflib import SequenceMatcher


SIMILARITY_THRESHOLD = 0.65


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def cluster_news(news_list):

    clusters = []
    used = set()

    for i, news in enumerate(news_list):

        if i in used:
            continue

        cluster = [news]
        used.add(i)

        for j, other in enumerate(news_list):

            if j in used:
                continue

            score = similarity(news.title, other.title)

            if score > SIMILARITY_THRESHOLD:

                cluster.append(other)
                used.add(j)

        clusters.append(cluster)

    return clusters
