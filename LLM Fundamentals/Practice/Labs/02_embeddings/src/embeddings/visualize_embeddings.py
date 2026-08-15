from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sentences.sentences import texts
from matplotlib import pyplot as plt

embedding_model = SentenceTransformer("BAAI/bge-m3")
embeddings = embedding_model.encode(texts, convert_to_numpy=True)

pca = PCA(n_components=2)
points = pca.fit_transform(embeddings)

plt.figure(figsize=(10,7))
plt.scatter(points[:,0], points[:,1])

for i, text in enumerate(texts):
    plt.annotate(text, (points[i,0], points[i,1]))

plt.xlabel('Componente 1')
plt.ylabel('Componente 2')
plt.title('Representacion de embeddings en 2 dimensiones')

plt.show()