import re

# Matches: IS 383 : 1970  OR  IS 1489 : (Part 1) : 1991  OR  IS 12269 : 1987
IS_ID_RE = re.compile(
    r'IS\s+(\d{2,6})\s*(?::\s*(?:\(Part\s*\d+\)\s*)?:\s*\d{4}|:\s*\d{4})?',
    re.IGNORECASE
)

# Split pages on "SUMMARY OF" — that's how SP21 separates each standard
SUMMARY_SPLIT = re.compile(r'(?=SUMMARY OF\s*\n)', re.IGNORECASE)

CATEGORIES = {
    "cement":     ["cement", "portland", "pozzolana", "clinker", "slag cement",
                   "masonry cement", "hydrophobic", "high alumina", "super sulphated"],
    "steel":      ["steel", "iron", "tmt", "rebar", "reinforcement", "structural steel",
                   "wire", "strand", "bar"],
    "concrete":   ["concrete", "rcc", "prestressed", "mortar", "grout", "precast"],
    "aggregates": ["aggregate", "sand", "gravel", "crushed stone",
                   "coarse aggregate", "fine aggregate", "lightweight aggregate"],
    "bricks":     ["brick", "block", "masonry unit", "clay unit", "fly ash brick",
                   "autoclaved"],
    "tiles":      ["tile", "ceramic", "flooring", "roofing tile", "terrazzo"],
    "asbestos":   ["asbestos", "corrugated sheet", "semi-corrugated"],
    "pipes":      ["pipe", "conduit", "drainage", "sewer", "water fitting"],
    "timber":     ["timber", "wood", "plywood", "hardboard", "fibreboard"],
    "bitumen":    ["bitumen", "tar", "asphalt", "bituminous"],
    "glass":      ["glass", "glazing", "window pane"],
    "lime":       ["lime", "calcined", "hydraulic lime"],
    "gypsum":     ["gypsum", "plaster of paris"],
}

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORIES.items():
        if any(k in t for k in kws):
            return cat
    return "general"

def extract_is_id(text: str) -> str:
    """
    Extract IS number in normalized format: 'IS 269 : 1989'
    Handles:
      IS 269 : 1989
      IS 1489 : (Part 1) : 1991
      IS 383 : 1970
    """
    # Try to find full IS number with year
    full = re.search(
        r'IS\s+(\d{2,6})\s*:\s*(?:\(Part\s*\d+\)\s*:\s*)?(\d{4})',
        text, re.IGNORECASE
    )
    if full:
        return f"IS {full.group(1)} : {full.group(2)}"

    # Fallback: just IS + number
    short = re.search(r'IS\s+(\d{2,6})', text, re.IGNORECASE)
    if short:
        return f"IS {short.group(1)}"

    return "UNKNOWN"

def sliding_window(text: str, size: int = 300, overlap: int = 60) -> list:
    words = text.split()
    step  = size - overlap
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+size])
        if len(chunk.strip()) > 40:
            chunks.append(chunk)
    return chunks

def chunk_pages(pages: list) -> list:
    """
    SP21 structure: each standard starts with 'SUMMARY OF'
    followed by 'IS XXXX : YYYY  TITLE OF STANDARD'
    We split on this boundary to get one chunk per standard.
    """
    chunks = []

    # Join all page text together first (SP21 standards can span pages)
    full_text = ""
    page_map  = {}  # character offset → page number
    offset    = 0
    for page in pages:
        text = page["text"] or ""
        full_text += text + "\n"
        page_map[offset] = page["page_number"]
        offset += len(text) + 1

    # Split on "SUMMARY OF" boundaries
    blocks = SUMMARY_SPLIT.split(full_text)
    blocks = [b.strip() for b in blocks if len(b.strip()) > 50]

    for block in blocks:
        sid  = extract_is_id(block)
        cat  = detect_category(block)
        # Approximate page number
        pos  = full_text.find(block[:50])
        pgnum = 1
        for off, pg in page_map.items():
            if off <= pos:
                pgnum = pg

        text_chunk = block[:1000]

        # Full chunk
        chunks.append({
            "text":        text_chunk,
            "standard_id": sid,
            "category":    cat,
            "page":        pgnum,
            "chunk_type":  "full"
        })

        # Title-only mini chunk (first 2 lines — boosts exact match recall)
        first_lines = " ".join(block.split("\n")[:3]).strip()
        if len(first_lines) > 15:
            chunks.append({
                "text":        first_lines,
                "standard_id": sid,
                "category":    cat,
                "page":        pgnum,
                "chunk_type":  "title"
            })

    # If "SUMMARY OF" split produced nothing, fallback to sliding window
    if len(chunks) < 10:
        print("[chunker] WARNING: SUMMARY OF split failed, using sliding window fallback")
        for page in pages:
            text = page["text"] or ""
            for w in sliding_window(text):
                sid = extract_is_id(w)
                chunks.append({
                    "text":        w,
                    "standard_id": sid,
                    "category":    detect_category(w),
                    "page":        page["page_number"],
                    "chunk_type":  "full"
                })

    # Deduplicate
    seen, out = set(), []
    for c in chunks:
        key = (c["standard_id"], c["chunk_type"], c["text"][:60])
        if key not in seen:
            seen.add(key)
            out.append(c)

    known   = sum(1 for c in out if c["standard_id"] != "UNKNOWN")
    unknown = sum(1 for c in out if c["standard_id"] == "UNKNOWN")
    print(f"[chunker] {len(out)} chunks — {known} with IS id, {unknown} unknown")
    return out