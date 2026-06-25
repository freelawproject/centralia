"""Delaware Court of Common Pleas ('delctcompl').

Every PDF in the corpus is a scanned image with no text layer (0 chars on
every page), so there is nothing to extract without OCR. The class exists
to label the court and to say so explicitly instead of emitting a silently
empty document.
"""

from __future__ import annotations

from .generic import GenericExtractor


class DelawareCommonPleas(GenericExtractor):
    court_id = "delctcompl"
    court_label = "Court of Common Pleas of the State of Delaware."

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        if not doc.opinions and not doc.summary and not doc.headmatter_lines:
            doc.warnings.append(
                "scanned image-only PDF — no text layer to extract (needs OCR)"
            )
        return doc
