import re

# List of common conversational/filler phrases to remove
FILLER_PATTERNS = [
    r"we manufacture ",
    r"we are manufacturing ",
    r"i want to know ",
    r"what bis standards do i need to follow[\?]?",
    r"which bis standards apply[\?]?",
    r"which is codes?",
    r"what standards should i check[\?]?",
    r"are there any bis codes[\?]?",
    r"suggest bis standards[\?]?",
    r"looking for the right is code[\?]?",
    r"please suggest ",
    r"for use in ",
    r"for ",
    r"used in ",
    r"used for ",
    r"applicable to ",
    r"relevant for ",
    r"relevant to ",
    r"pertains to ",
    r"relates to ",
    # Add more as needed
]


def extract_product_keywords(query: str, categories=None) -> str:
    """
    Extracts the most likely product/material keywords from the query using category keywords.
    Returns a string of keywords for boosting retrieval and category detection.
    """
    if categories is None:
        # fallback: use default CATEGORIES from chunker.py
        categories = {
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
    q = query.lower()
    found = set()
    for kws in categories.values():
        for kw in kws:
            if kw in q:
                found.add(kw)
    # If nothing found, fallback to all words >3 chars
    if not found:
        found = set(w for w in q.split() if len(w) > 3)
    return " ".join(sorted(found))

def normalize_query(query: str, return_keywords=False) -> str:
    """
    Removes conversational/filler phrases and extra whitespace from the query.
    Optionally returns extracted product keywords.
    """
    q = query.lower()
    for pat in FILLER_PATTERNS:
        q = re.sub(pat, "", q)
    # Remove extra whitespace and punctuation
    q = re.sub(r"[\.,;:!?]", "", q)
    q = re.sub(r"\s+", " ", q)
    q = q.strip()
    if return_keywords:
        return q, extract_product_keywords(q)
    return q
