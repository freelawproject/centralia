"""centralia — court-pluggable PDF opinion extractor.

    from centralia import get_extractor
    doc = get_extractor("ala").extract("path/to/opinion.pdf")
    # doc is an ExtractedDocument: doc.doc_type, doc.opinions, ...

    from centralia.render import render_casebody
    xml = render_casebody(doc)
"""

from .base import BaseExtractor
from .models import (
    Block,
    DocType,
    ExtractedDocument,
    Footnote,
    Opinion,
)
from .registry import EXTRACTORS, get_extractor

__all__ = [
    "BaseExtractor",
    "Block",
    "DocType",
    "ExtractedDocument",
    "Footnote",
    "Opinion",
    "EXTRACTORS",
    "get_extractor",
]
