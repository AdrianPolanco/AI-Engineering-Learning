from sentences.sentences import texts
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('intfloat/multilingual-e5-small')

embeddings = embedding_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

for text, embedding in zip(texts, embeddings):
    print(text)
    print(embedding)
    print(f'Dimensions: {len(embedding)}')