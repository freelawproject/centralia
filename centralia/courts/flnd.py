"""United States District Court, Northern District of Florida.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Report-and-Recommendation filings close with a 'NOTICE TO THE PARTIES' block
(the 14-day objection notice). That is procedural ending matter, not part of the
recommendation, so it is routed to the trailer.
"""

from __future__ import annotations

import re

from ._district import DistrictBase

_TAG = re.compile(r"<[^>]+>")


class NorthernDistrictOfFlorida(DistrictBase):
    court_id = "flnd"
    court_label = "United States District Court, Northern District of Florida."

    def find_footnote_separator(self, page):
        """flnd footnotes are body-sized (only the label digit is raised), so
        the size-below scan can't see the boundary; detection relies on the
        fixed 2-inch (144pt) left-margin rule. Some flnd templates indent that
        rule to ~1.5 inch (x0=108) rather than the body margin (x0=72), so the
        base fixed-rule fence (x0<=76) misses it and the footnote is dropped.
        Widen the left-edge window:
          - page 1: gate on a real footnote label below, so a heading or
            redaction underline at the indent isn't taken for a separator;
          - continuation pages: a footnote that wraps to the next page reopens
            with no label, so accept the rule on its exact 144pt signature
            alone. The tight tolerance keeps block-quote/heading underlines
            drawn at the same indent (seen at ~133 / 150pt) out."""
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        if page.page_number == 1:
            cand = self.footnote_sep_fixed_left_rule(page, x0_max=112.0)
            if cand is not None and self._opens_footnote_zone(page, cand):
                return cand
        else:
            cand = self.footnote_sep_fixed_left_rule(page, x0_max=112.0, tol=1.0)
            if cand is not None:
                return cand
        return None

    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            cut = next(
                (
                    i
                    for i, b in enumerate(op.blocks)
                    if b.kind in ("p", "heading")
                    and _TAG.sub("", b.text)
                    .strip()
                    .upper()
                    .startswith("NOTICE TO THE PART")
                ),
                None,
            )
            if cut is not None:
                tail = [_TAG.sub("", b.text).strip() for b in op.blocks[cut:]]
                op.blocks = op.blocks[:cut]
                doc.trailer = list(doc.trailer) + tail
                break
        return doc
