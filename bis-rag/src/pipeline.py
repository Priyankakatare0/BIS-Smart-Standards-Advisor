import time
from src.retriever import hybrid_retrieve
from src.reranker  import rerank
from src.llm       import generate_rationale

def run_pipeline(query: str) -> tuple:
    """
    Returns (recommendations, latency_seconds)
    recommendations: [{"standard_id": str, "rationale": str}, ...]
    """
    t0 = time.time()

    candidates      = hybrid_retrieve(query, top_k=10)
    top_chunks      = rerank(query, candidates, top_k=5)
    recommendations = generate_rationale(query, top_chunks)

    latency = round(time.time() - t0, 3)
    return recommendations, latency