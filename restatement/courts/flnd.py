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
