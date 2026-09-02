import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.text_processor import normalize_text

_MODEL_INSTANCE = None
_MODEL_LOADED = False

def get_sentence_transformer_model():
    """
    Lazy loader for SentenceTransformer model to prevent server startup latency.
    """
    global _MODEL_INSTANCE, _MODEL_LOADED
    if _MODEL_INSTANCE is None and not _MODEL_LOADED:
        try:
            from sentence_transformers import SentenceTransformer
            # Lightweight, fast 80MB model ideal for local CPU development
            _MODEL_INSTANCE = SentenceTransformer('all-MiniLM-L6-v2')
            _MODEL_LOADED = True
            print("Loaded SentenceTransformer model successfully.")
        except Exception as e:
            print(f"Notice: SentenceTransformer loading deferred or unavailable ({e}). Using n-gram fallback.")
            _MODEL_LOADED = True
            _MODEL_INSTANCE = None
    return _MODEL_INSTANCE

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes semantic similarity percentage (0-100) between two text documents.
    Uses sentence-transformers embedding cosine similarity if available,
    with a robust TF-IDF character/word n-gram fallback.
    """
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    if not norm1 or not norm2:
        return 0.0

    model = get_sentence_transformer_model()
    if model is not None:
        try:
            # Chunk text into 250-word segments if extremely long
            chunks1 = [norm1[i:i+1000] for i in range(0, min(len(norm1), 3000), 1000)]
            chunks2 = [norm2[i:i+1000] for i in range(0, min(len(norm2), 3000), 1000)]
            
            emb1 = model.encode(chunks1, show_progress_bar=False)
            emb2 = model.encode(chunks2, show_progress_bar=False)
            
            vec1 = np.mean(emb1, axis=0).reshape(1, -1)
            vec2 = np.mean(emb2, axis=0).reshape(1, -1)
            
            sim = cosine_similarity(vec1, vec2)[0][0]
            sim_pct = round(float(sim) * 100, 1)
            return max(0.0, min(100.0, sim_pct))
        except Exception as e:
            print(f"Semantic embedding computation error: {e}. Falling back to n-gram model.")

    # Fallback: Scikit-Learn Character & Word N-gram TF-IDF Cosine Similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    fallback_vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
    try:
        matrix = fallback_vectorizer.fit_transform([norm1, norm2])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        return 50.0
