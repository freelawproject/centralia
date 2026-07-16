"""Supreme Court of the State of Oregon.

Filed under ``oregon`` because ``or`` is a Python keyword (the court id stays
``or``). The Oregon Reports layout (narrow page, NewCenturySchlbk body, star +
numbered footnotes) is shared with the Court of Appeals via ``OregonReports``.
The author byline is an abbreviated-title form ('BUSHONG, J.' / 'FLYNN, C.J.');
many dispositions are 'PER CURIAM'. A 'Before ...' panel roster is excluded by
the shared base.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._oregon import OregonReports


class OregonSupreme(OregonReports, AbbrevTitleSupreme):
    court_id = "or"
    court_label = "Supreme Court of the State of Oregon."

    def extract(self, pdf_path):
        """Each opinion is signed twice — once over the one-paragraph disposition
        summary near the caption ('BUSHONG, J. The decision ... is affirmed.'),
        then again over the opinion proper on the next page. Collapse consecutive
        writings by the same author so the summary opens its own opinion rather
        than producing a duplicate."""
        doc = super().extract(pdf_path)
        merged = []
        for op in doc.opinions:
            if merged and merged[-1].author == op.author and merged[-1].type == op.type:
                merged[-1].blocks.extend(op.blocks)
                merged[-1].footnotes.extend(op.footnotes)
            else:
                merged.append(op)
        doc.opinions = merged
        self._apply_or_facets(doc, pdf_path)
        return doc
