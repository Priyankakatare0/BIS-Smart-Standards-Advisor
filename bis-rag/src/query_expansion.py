# src/query_expansion.py


SYNONYM_MAP = {
    "opc cement": "ordinary portland cement",
    "ordinary portland cement (opc)": "ordinary portland cement",
    "ppc cement": "portland pozzolana cement",
    "portland pozzolana cement (ppc)": "portland pozzolana cement",
    "rcc": "reinforced cement concrete",
    "reinforced concrete": "reinforced cement concrete",
    "flyash": "fly ash",
    "flyash brick": "fly ash brick",
    "aac block": "autoclaved aerated concrete block",
    "aac blocks": "autoclaved aerated concrete block",
    "mortar mix": "mortar",
    "tmt bar": "thermo mechanically treated bar",
    "tmt bars": "thermo mechanically treated bar",
    "m20 concrete": "m 20 grade concrete",
    "m25 concrete": "m 25 grade concrete",
    "m30 concrete": "m 30 grade concrete",
    "pcc": "plain cement concrete",
    "bitumen": "bituminous material",
    "bituminous concrete": "bituminous material",
    "gypsum board": "gypsum plaster board",
    "gypsum plaster": "gypsum plaster",
    "steel rod": "steel bar",
    "steel rods": "steel bar",
    "steel bar": "steel bar",
    "steel bars": "steel bar",
    "aggregate": "coarse aggregate",
    "aggregates": "coarse aggregate",
    "fine aggregate": "fine aggregate",
    "coarse aggregate": "coarse aggregate",
    "clc block": "cellular lightweight concrete block",
    "clc blocks": "cellular lightweight concrete block",
    "pvc pipe": "polyvinyl chloride pipe",
    "pvc pipes": "polyvinyl chloride pipe",
    "hdpe pipe": "high density polyethylene pipe",
    "hdpe pipes": "high density polyethylene pipe",
    "cpvc pipe": "chlorinated polyvinyl chloride pipe",
    "cpvc pipes": "chlorinated polyvinyl chloride pipe",
    "ms pipe": "mild steel pipe",
    "ms pipes": "mild steel pipe",
    "gi pipe": "galvanized iron pipe",
    "gi pipes": "galvanized iron pipe",
    "wpc": "wood plastic composite",
    "wpc board": "wood plastic composite board",
    "wpc boards": "wood plastic composite board",
    "aac": "autoclaved aerated concrete",
    "aac block": "autoclaved aerated concrete block",
    "aac blocks": "autoclaved aerated concrete block",
    # Add more as needed
}

def expand_query(query: str) -> str:
    q = query.lower()
    for k, v in SYNONYM_MAP.items():
        if k in q:
            q = q.replace(k, v)
    return q
