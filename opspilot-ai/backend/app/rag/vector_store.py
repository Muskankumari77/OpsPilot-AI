"""
Lean "embeddings" for RAG.

Groq doesn't currently serve an embeddings endpoint, and a real neural
embedding model (sentence-transformers, OpenAI embeddings) would mean either
a heavy local dependency (torch) or another paid API — both more than a lean
build needs for searching a handful of internal policy documents.

Instead: scikit-learn's HashingVectorizer, a classic (pre-neural) technique
that hashes n-grams into a fixed-size vector with NO fitting/training step —
unlike TF-IDF, it doesn't need to see the whole corpus first, so documents
can be embedded independently and incrementally. This is a real, documented
simplification: it captures lexical/keyword similarity well, not deep
semantic similarity (it won't know "couch" and "sofa" are related). Good
enough for policy-document lookup; swapping in real embeddings later is a
one-file change (this module's `embed_text` is the only place it's computed).
"""
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

EMBEDDING_DIM = 256

_vectorizer = HashingVectorizer(n_features=EMBEDDING_DIM, alternate_sign=False, norm="l2")


def embed_text(text: str) -> list[float]:
    vector = _vectorizer.transform([text]).toarray()[0]
    return vector.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)
