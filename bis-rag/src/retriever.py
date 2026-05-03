import pickle
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

CHROMA_DIR = "./chroma_db"
BM25_PATH  = "./chroma_db/bm25_index.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

# --- Singletons (loaded once per process) ---
_model      = None
_collection = None
_bm25       = None
_bm25chunks = None

def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def _load_collection():
    global _collection
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection("bis_standards")
    return _collection

def _load_bm25():
    global _bm25, _bm25chunks
    if _bm25 is None:
        data        = pickle.load(open(BM25_PATH, "rb"))
        _bm25       = data["bm25"]
        _bm25chunks = data["chunks"]
    return _bm25, _bm25chunks

# --- Dense search ---
def _dense_search(query: str, top_k: int = 10, category: str = None) -> list:
    model  = _load_model()
    col    = _load_collection()
    vec    = model.encode(query, normalize_embeddings=True).tolist()
    res    = col.query(query_embeddings=[vec], n_results=top_k*2,  # fetch more for filtering
                       include=["documents","metadatas","distances"])
    hits = []
    for doc, meta, dist in zip(res["documents"][0],
                                res["metadatas"][0],
                                res["distances"][0]):
        if category and meta.get("category") != category:
            continue
        hits.append({
            "text":        doc,
            "standard_id": meta["standard_id"],
            "category":    meta["category"],
            "score_dense": float(1 - dist),
        })
        if len(hits) >= top_k:
            break
    return hits

# --- BM25 keyword search ---
def _bm25_search(query: str, top_k: int = 10, category: str = None) -> list:
    bm25, chunks = _load_bm25()
    tokens       = query.lower().split()
    scores       = bm25.get_scores(tokens)
    top_idx      = np.argsort(scores)[::-1]
    hits = []
    for i in top_idx:
        if scores[i] > 0:
            if category and chunks[i]["category"] != category:
                continue
            hits.append({
                "text":        chunks[i]["text"],
                "standard_id": chunks[i]["standard_id"],
                "category":    chunks[i]["category"],
                "score_bm25":  float(scores[i]),
            })
            if len(hits) >= top_k:
                break
    return hits

# --- Reciprocal Rank Fusion ---
def _rrf_merge(dense: list, sparse: list, k: int = 60) -> list:
    scores = {}
    for rank, hit in enumerate(dense):
        sid = hit["standard_id"]
        scores.setdefault(sid, {"rrf": 0.0, **hit})
        scores[sid]["rrf"] += 1.0 / (k + rank + 1)
    for rank, hit in enumerate(sparse):
        sid = hit["standard_id"]
        scores.setdefault(sid, {"rrf": 0.0, **hit})
        scores[sid]["rrf"] += 1.0 / (k + rank + 1)
    return sorted(scores.values(), key=lambda x: x["rrf"], reverse=True)

# --- Public API ---
def hybrid_retrieve(query: str, top_k: int = 10, category: str = None) -> list:
    dense  = _dense_search(query, top_k=top_k, category=category)
    sparse = _bm25_search(query, top_k=top_k, category=category)
    merged = _rrf_merge(dense, sparse)
    return merged[:top_k]

def preload():
    """Call at app startup to warm all singletons."""
    _load_model(); _load_collection(); _load_bm25()