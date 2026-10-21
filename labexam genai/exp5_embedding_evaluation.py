"""
Lab 5: Embedding Evaluations
- Load news/article dataset
- Create doc representation using Word2Vec, GloVe, BERT
- Implement KNN based retrieval using cosine/euclidean distance
- Retrieve top-5 most relevant docs
"""
import numpy as np
import gensim.downloader as gensim_api
from sklearn.datasets import fetch_20newsgroups
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer

NUM_DOCS = 200
TOP_K = 5
QUERY = "space exploration and satellites"

# Load a news/article dataset
docs = fetch_20newsgroups(subset="train", remove=("headers", "footers", "quotes")).data[:NUM_DOCS]
docs = [d for d in docs if d.strip()][:NUM_DOCS]

def word2vec_doc_vectors(documents, model):
    vectors = []
    for doc in documents:
        words = [w for w in doc.lower().split() if w in model]
        vectors.append(np.mean(model[words], axis=0) if words else np.zeros(model.vector_size))
    return np.array(vectors)

def top5_matches(doc_vectors, query_vector, documents, metric="cosine"):
    knn = NearestNeighbors(n_neighbors=TOP_K, metric=metric).fit(doc_vectors)
    _, indices = knn.kneighbors([query_vector])
    return [documents[i][:80].replace("\n", " ") for i in indices[0]]

# --- Word2Vec representation (pretrained word2vec-google-news) ---
word2vec_model = gensim_api.load("word2vec-google-news-300")
w2v_doc_vecs = word2vec_doc_vectors(docs, word2vec_model)
w2v_query_vec = word2vec_doc_vectors([QUERY], word2vec_model)[0]
print("Top-5 (Word2Vec, cosine):")
for match in top5_matches(w2v_doc_vecs, w2v_query_vec, docs):
    print(" -", match)

# --- GloVe representation ---
glove_model = gensim_api.load("glove-wiki-gigaword-100")
glove_doc_vecs = word2vec_doc_vectors(docs, glove_model)
glove_query_vec = word2vec_doc_vectors([QUERY], glove_model)[0]
print("\nTop-5 (GloVe, euclidean):")
for match in top5_matches(glove_doc_vecs, glove_query_vec, docs, metric="euclidean"):
    print(" -", match)

# --- BERT representation (sentence-transformers) ---
bert_model = SentenceTransformer("all-MiniLM-L6-v2")
bert_doc_vecs = bert_model.encode(docs)
bert_query_vec = bert_model.encode([QUERY])[0]
print("\nTop-5 (BERT, cosine):")
for match in top5_matches(bert_doc_vecs, bert_query_vec, docs):
    print(" -", match)
