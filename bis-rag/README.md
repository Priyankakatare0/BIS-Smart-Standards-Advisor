# BIS Standards Recommendation Engine

AI-powered RAG system to help Indian MSEs instantly identify relevant BIS standards
from SP 21 (Building Materials).

## Architecture
- **Chunking**: IS-number boundary splitting + sliding window fallback
- **Dense retrieval**: `all-MiniLM-L6-v2` → ChromaDB (cosine similarity)
- **Sparse retrieval**: BM25 keyword index
- **Fusion**: Reciprocal Rank Fusion (RRF) merge of both
- **Reranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **LLM**: Groq `llama3-8b-8192` for rationale generation
- **UI**: Gradio

## Setup

```bash
git clone <repo-url> && cd bis-rag
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at console.groq.com)
```

## Build the index (once)

Place `BIS_SP21.pdf` in `data/` then:
```bash
python src/ingest.py
```
Takes 3–8 minutes. Creates `chroma_db/`.

## Run the UI
```bash
python src/app.py
# Open http://localhost:7860
```

## Run inference (judge command)
```bash
python inference.py --input public_test_set.json --output data/public_results.json
```

## Evaluation results (public test set)

| Metric | Score |
|---|---|
| Hit Rate @3 | XX% |
| MRR @5 | X.XX |
| Avg Latency | X.Xs |