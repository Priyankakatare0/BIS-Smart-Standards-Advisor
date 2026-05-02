import os, pickle
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from src.chunker import chunk_pages

CHROMA_DIR = "./chroma_db"
BM25_PATH  = "./chroma_db/bm25_index.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

def parse_pdf(path: str) -> list:
    pages = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            text = pg.extract_text()
            if text:
                pages.append({"text": text, "page_number": pg.page_number})
    print(f"[ingest] parsed {len(pages)} pages")
    return pages

def build_index(pdf_path: str = "data/dataset.pdf"):
    # 1. Parse PDF
    pages  = parse_pdf(pdf_path)

    # 2. Chunk
    chunks = chunk_pages(pages)
    texts  = [c["text"] for c in chunks]

    # 3. Embed with sentence transformer
    print("[ingest] encoding embeddings (this takes a few minutes)...")
    model      = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, batch_size=64,
                              show_progress_bar=True,
                              normalize_embeddings=True).tolist()

    # 4. Store in ChromaDB
    print("[ingest] writing to ChromaDB...")
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection("bis_standards")
    except Exception:
        pass
    col = client.create_collection("bis_standards",
                                   metadata={"hnsw:space": "cosine"})

    # Insert in batches of 500 (ChromaDB limit)
    ids   = [f"c{i}" for i in range(len(chunks))]
    metas = [{"standard_id": c["standard_id"],
              "category":    c["category"],
              "page":        c["page"],
              "chunk_type":  c["chunk_type"]} for c in chunks]

    for i in range(0, len(chunks), 500):
        col.add(documents=texts[i:i+500],
                embeddings=embeddings[i:i+500],
                ids=ids[i:i+500],
                metadatas=metas[i:i+500])
    print(f"[ingest] ChromaDB: {len(chunks)} vectors stored")

    # 5. Build BM25 sparse index
    print("[ingest] building BM25 index...")
    tokenized = [t.lower().split() for t in texts]
    bm25      = BM25Okapi(tokenized)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)
    print(f"[ingest] BM25 saved to {BM25_PATH}")
    print("[ingest] DONE. Ready to query.")

if __name__ == "__main__":
    build_index()