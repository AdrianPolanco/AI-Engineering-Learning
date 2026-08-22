from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer("BAAI/bge-m3")
embeddings = embedding_model.encode_document()