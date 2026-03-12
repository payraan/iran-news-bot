from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_embedding(text: str):
    return model.encode(text)


def is_duplicate(new_embedding, existing_embeddings, threshold=0.85):

    if len(existing_embeddings) == 0:
        return False

    similarities = cosine_similarity(
        [new_embedding],
        existing_embeddings
    )[0]

    return max(similarities) > threshold
