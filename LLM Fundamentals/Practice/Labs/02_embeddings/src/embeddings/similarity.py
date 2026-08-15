from sentence_transformers import SentenceTransformer
from sentences.sentences import texts
from sklearn.metrics.pairwise import cosine_similarity


embedding_model = SentenceTransformer("BAAI/bge-m3")

subtexts = [texts[3], texts[4]]

embeddings = embedding_model.encode(subtexts, convert_to_numpy=True, normalize_embeddings=True)

similarity = cosine_similarity(embeddings)

print(f'Similarity between "{subtexts[0]}" and "{subtexts[1]}"')
print(similarity)