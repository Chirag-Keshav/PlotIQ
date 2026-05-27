"""Document completeness scorer — 0-100 based on which doc types are present."""
from __future__ import annotations

# Weight of each document type toward the total score
DOC_WEIGHTS = {
    "ec": 30,             # Encumbrance Certificate — critical
    "sale_deed": 30,      # Sale Deed — critical
    "layout_approval": 20, # HMDA/DTCP approval
    "mutation_register": 10,
    "patta": 10,
}
REQUIRED_DOCS = set(DOC_WEIGHTS.keys())


def document_completeness_scorer(doc_types_present: list[str]) -> int:
    """
    Return 0-100 score based on which document types have been uploaded.
    
    Score = sum of weights for each present doc type.
    Max possible = 100 (all docs present).
    """
    present = set(d.lower() for d in doc_types_present)
    score = sum(weight for doc, weight in DOC_WEIGHTS.items() if doc in present)
    return max(0, min(100, score))
