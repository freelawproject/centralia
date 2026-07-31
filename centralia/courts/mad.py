"""United States District Court, District of Massachusetts.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfMassachusetts(DistrictBase):
    court_id = "mad"
    court_label = "United States District Court, District of Massachusetts."

    def correct_page_geometry(self, page) -> None:
        """De-interleave a DOUBLED filing strip in the top margin.

        When a court of appeals opinion is docketed back into the district case,
        the sheet carries two electronic filing strips stamped at the same
        height — the appellate one ('Case: 26-1774 Document: 21 Date Filed: …
        Entry ID: …') and the district one ('Case 1:26-cv-11581-IT Document 211
        Filed 07/27/26 Page 1 of 20') — half a point apart, so line clustering
        merges them into one unreadable row ('Case: 26C-1a7s7e4 1 : 2 6D-ocvc-…').
        Each strip is set in its OWN font, so the two are separated by font and
        put on their own baselines (both still inside the top margin). Done in
        this hook, not ``page_lines``, so the completeness audit reads the page
        the same way and recognizes each strip as the repeated page furniture it
        is. Gated on two fonts genuinely OVERLAPPING in x: an ordinary filing,
        whose strip is one font, is untouched.
        """
        super().correct_page_geometry(page)
        self._split_doubled_filing_strip(page)

    def _split_doubled_filing_strip(self, page, offset: float = 11.0) -> None:
        band = [
            c
            for c in page.chars
            if c.get("top", 0) < self.margin_top and (c.get("text") or "").strip()
        ]
        if len(band) < 20:
            return
        groups: dict = {}
        for c in band:
            fam = (c.get("fontname") or "").split("+")[-1]
            groups.setdefault(fam, []).append(c)
        if len(groups) < 2:
            return
        # One row only: every glyph within a line height of the topmost.
        top0 = min(c["top"] for c in band)
        if any(c["top"] - top0 > 6 for c in band):
            return
        spans = {
            fam: (min(c["x0"] for c in cs), max(c["x1"] for c in cs))
            for fam, cs in groups.items()
        }
        order = sorted(groups, key=lambda f: -len(groups[f]))
        keep, rest = order[0], order[1:]
        kx0, kx1 = spans[keep]
        moved = 0
        for fam in rest:
            fx0, fx1 = spans[fam]
            if min(kx1, fx1) - max(kx0, fx0) <= 0:
                continue  # side by side, not interleaved — leave it alone
            moved += 1
            delta = offset * moved
            if top0 + delta >= self.margin_top - 2:
                return  # no room left inside the margin; leave the band as-is
            for c in groups[fam]:
                c["top"] += delta
                c["bottom"] += delta
                c["doctop"] = c.get("doctop", c["top"]) + delta
                if "y0" in c:
                    c["y0"] -= delta
                if "y1" in c:
                    c["y1"] -= delta
