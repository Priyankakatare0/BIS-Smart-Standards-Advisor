import time

from src.retriever import hybrid_retrieve
from src.chunker import detect_category
from src.reranker  import rerank
from src.llm       import generate_rationale
from src.query_expansion import expand_query
from src.query_normalizer import normalize_query

def run_pipeline(query: str) -> tuple:
    """
    Returns (recommendations, latency_seconds)
    recommendations: [{"standard_id": str, "rationale": str}, ...]
    """
    t0 = time.time()



    # Step 1: Query Normalization and Product Keyword Extraction
    query, product_keywords = normalize_query(query, return_keywords=True)

    # Step 2: Query Expansion
    query = expand_query(query)

    # Step 3: Metadata Filtering (use product keywords to boost category detection)
    category = detect_category(product_keywords or query)
    if category == "general":
        category = None

    # Step 4: Hybrid Retrieval (boost with product keywords)
    retrieval_query = f"{query} {product_keywords}" if product_keywords else query
    candidates      = hybrid_retrieve(retrieval_query, top_k=10, category=category)
    top_chunks      = rerank(query, candidates, top_k=5)
    recommendations = generate_rationale(query, top_chunks)

    latency = round(time.time() - t0, 3)
    return recommendations, latency