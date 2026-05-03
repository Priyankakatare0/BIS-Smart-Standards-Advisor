# BIS Smart Standards Advisor

## Project Overview
A tool to help Indian MSEs instantly find the right BIS (Bureau of Indian Standards) standards for building material products, using advanced retrieval, reranking, and explainability features.

---

## Features Implemented

### 1. Automated IS Number Extraction
- Script to extract all IS numbers from large PDF documents.
- Ensures only valid IS numbers are used in recommendations and checks.

### 2. Automated Hallucination Check
- Script to check for hallucinated (invalid or out-of-scope) IS numbers in system output.
- Ensures recommendations are trustworthy and evaluation-ready.

### 3. Hybrid Retrieval System
- Combines dense (semantic) retrieval using sentence-transformers and sparse (BM25) retrieval.
- Improves both recall and precision of recommended standards.

### 4. Query Expansion
- Expands user queries with synonyms and related terms.
- Increases the chance of matching relevant standards.

### 5. Metadata Filtering
- Detects product categories and filters standards accordingly.
- Reduces irrelevant matches and boosts precision.

### 6. Cross-Encoder Reranking
- Reranks candidate standards using a cross-encoder model.
- Assigns a `rerank_score` (confidence score) to each candidate.

### 7. Rationale Generation
- Generates a clear, product-specific rationale for each recommended standard.
- Includes the rerank_score in the output for transparency.

### 8. Gradio User Interface
- User-friendly UI for entering product descriptions and viewing recommendations.
- Displays IS numbers, rationales, and color-coded confidence scores (green = high, orange = medium, red = low).

### 9. Evaluation and Testing
- Scripts for manual and automated evaluation.
- Ensures no hallucinations and high relevance.
- Tested with diverse queries for robustness.

### 10. Innovation Points
- Query expansion, metadata filtering, confidence scoring, hallucination checks, and hybrid retrieval all implemented.

---

## Current Status
- All core features are implemented, tested, and working.
- System is robust, user-friendly, and ready for demo, hackathon submission, or further extension.

---

## How to Use
1. Run the Gradio app (`python -m src.app`).
2. Enter a building material product description.
3. View the recommended BIS standards, rationales, and confidence scores.
4. Use the provided scripts for evaluation and hallucination checks as needed.

---

## Example Output
```
1. IS 1608 : 1995 (Confidence: 5.024)
   This standard applies to the product as it specifies requirements for mild steel and medium tensile steel bars used as reinforcement in concrete, which is relevant to TMT steel reinforcement bars.

2. IS 1786 : 1985 (Confidence: 3.147)
   This standard applies to the product as it covers plain high strength deformed steel bars and wires for concrete reinforcement, which is related to the TMT steel reinforcement bars for reinforced cement concrete construction.

...etc.
```

---

## Contact & Credits
- Developed for the BIS Smart Standards Hackathon.
- For questions or contributions, contact the project team.
