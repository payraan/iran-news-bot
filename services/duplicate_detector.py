from google import genai
from config.settings import settings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def compute_embedding(text: str):
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text
    )
    # حتماً باید تبدیل به Numpy Array بشه تا متد tolist در فایل‌های دیگه ارور نده
    return np.array(response.embeddings[0].values)

def is_duplicate(new_embedding, existing_embeddings, threshold=0.85):
    if len(existing_embeddings) == 0:
        return False

    similarities = cosine_similarity(
        [new_embedding], 
        existing_embeddings
    )[0]
    
    return max(similarities) > threshold
