"""United States District Court, Northern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class NorthernDistrictOfCalifornia(DistrictBase):
    def page_lines(self, page):
        if not hasattr(self, "_cand_dropped"):
            self._cand_dropped = []
        # the court name printed SIDEWAYS up the pleading margin is
        # extracted reversed ('truoC tcirtsiD …') at x≈37, outside the body
        # margins — record it from the RAW chars (the margin filter removes
        # it before line building) and surface it as removed furniture
        rot = "".join(
            (c.get("text") or "")
            for c in page.chars
            if not c.get("upright", True)
        ).strip()
        if rot:
            self._cand_dropped.append(
                "[rotated margin text removed: " + rot[:80] + "]"
            )
        return super().page_lines(page)

    def extract(self, pdf_path: str):
        self._cand_dropped = []
        doc = super().extract(pdf_path)
        if self._cand_dropped:
            seen, extra = set(), []
            for t in self._cand_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    court_id = "cand"
    court_label = "United States District Court, Northern District of California."
