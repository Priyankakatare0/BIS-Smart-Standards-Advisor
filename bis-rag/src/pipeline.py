import time

from src.retriever import hybrid_retrieve
from src.chunker import detect_category
from src.reranker  import rerank
from src.llm       import generate_rationale
from src.query_expansion import expand_query

def run_pipeline(query: str) -> tuple:
    """
    Returns (recommendations, latency_seconds)
    recommendations: [{"standard_id": str, "rationale": str}, ...]
    """
    t0 = time.time()

    # Step 1: Query Expansion

    query = expand_query(query)

    # Step 2: Metadata Filtering
    category = detect_category(query)
    if category == "general":
        category = None

    candidates      = hybrid_retrieve(query, top_k=10, category=category)
    top_chunks      = rerank(query, candidates, top_k=5)
    recommendations = generate_rationale(query, top_chunks)

    latency = round(time.time() - t0, 3)
    return recommendations, latency