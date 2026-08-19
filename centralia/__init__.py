"""centralia v2 — court PDF opinion extractor.

Public API (lands in Phase 6):

    from centralia import extract
    result = extract(pdf_path, court_id="mont")
    result.document   # typed Document
    result.trace      # per-decision evidence chains
    result.status     # valid | review | failed
"""
