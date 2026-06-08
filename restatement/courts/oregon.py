"""Supreme Court of the State of Oregon.

Filed under ``oregon`` because ``or`` is a Python keyword (the court id stays
``or``). The Oregon Reports use a narrow (~5.5") page: width ~396, body text at
x0 ~45 with paragraph indents at ~60, and a running header at the very top of
every page ('150 April 9, 2026 No. 18' / 'Cite as 375 Or 150 (2026) 151').
The author byline is an abbreviated-title form ('BUSHONG, J.' / 'FLYNN, C.J.');
many dispositions are 'PER CURIAM'. A 'Before ...' panel roster is excluded by
the shared base.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class OregonSupreme(AbbrevTitleSupreme):
    court_id = "or"
    court_label = "Supreme Court of the State of Oregon."
    # Narrow reporter page: body sits at x0 ~45, not the 72 of letter-size courts.
    body_baseline_x0 = 45.0
    # Drop the top-of-page running header (top ~36); body proper starts ~63.
    margin_top = 45.0

    # Style-preserving headmatter (the shared 'Florida look').
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

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
        return doc
