from sentence_transformers import CrossEncoder

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_reranker = None

def _load_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL)
    return _reranker

def rerank(query: str, candidates: list, top_k: int = 5) -> list:
    if not candidates:
        return []

    model  = _load_reranker()
    pairs  = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    # Attach scores
    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)

    sorted_hits = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    # Deduplicate: one chunk per IS number, keep highest score
    seen, out = set(), []
    for h in sorted_hits:
        sid = h["standard_id"]
        if sid == "UNKNOWN":
            continue           # skip unidentified chunks
        if sid not in seen:
            seen.add(sid)
            out.append(h)
        if len(out) >= top_k:
            break

    return out

def preload():
    _load_reranker()