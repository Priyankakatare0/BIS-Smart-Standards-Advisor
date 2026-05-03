import os, json
from dotenv import load_dotenv
load_dotenv()

def _call_groq(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=700,
    )
    return r.choices[0].message.content

def _parse_json(raw: str) -> list:
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return []
    try:
        return json.loads(raw[start:end])
    except Exception:
        return []

def generate_rationale(query: str, chunks: list) -> list:
    """
    chunks: output of rerank() — list of dicts with standard_id and text
    Returns: [{"standard_id": "IS XXX", "rationale": "..."}, ...]
    """
    allowed = [c["standard_id"] for c in chunks if c["standard_id"] != "UNKNOWN"]
    if not allowed:
        return []

    # Map standard_id to rerank_score for easy lookup
    score_map = {c["standard_id"]: c.get("rerank_score", None) for c in chunks if c["standard_id"] != "UNKNOWN"}

    context = "\n\n".join(
        f"[{c['standard_id']}]\n{c['text'][:450]}" for c in chunks
        if c["standard_id"] != "UNKNOWN"
    )

    prompt = f"""You are a BIS (Bureau of Indian Standards) compliance expert.

A small business describes their product as:
"{query}"

The following BIS standards were retrieved from SP 21 (Building Materials):

{context}

TASK: Select the 3 to 5 most applicable standards from the list above and write one sentence explaining why each applies to this product.

RULES (strictly follow):
1. Only use standard IDs from this exact set: {allowed}
2. Do NOT invent, guess, or use any IS number not in the set above.
3. Each rationale: one clear sentence, specific to the product.
4. Return ONLY a JSON array. No explanation, no markdown, no extra text.

JSON format:
[
  {{"standard_id": "IS XXXX", "rationale": "Sentence explaining relevance."}},
  ...
]"""

    raw     = _call_groq(prompt)
    results = _parse_json(raw)

    # Safety: strip any hallucinated IDs
    results = [r for r in results if r.get("standard_id") in allowed]

    # Attach rerank_score to each result
    for r in results:
        r["rerank_score"] = score_map.get(r["standard_id"])

    # Fallback if LLM returns nothing valid
    if not results:
        results = [{"standard_id": c["standard_id"], "rationale": "Relevant based on retrieval.", "rerank_score": c.get("rerank_score", None)}
                   for c in chunks[:3] if c["standard_id"] != "UNKNOWN"]

    return results