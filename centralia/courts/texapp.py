"""Texas Court of Appeals.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from statistics import median

from ._district import DistrictBase


class TexasCourtOfAppeals(DistrictBase):
    court_id = "texapp"
    court_label = "Texas Court of Appeals."

    def _rule_over_footnotes(self, page, rule_top) -> bool:
        """Texas draws full-width DOUBLED rules as caption-banner dividers in
        the headmatter ('… EDINBURG' ─── parties ─── 'ON APPEAL …' ───
        'MEMORANDUM OPINION'). The base test — smaller *median* text below —
        misfires here because the whole opinion body (12pt) is smaller than the
        bold 14–16pt caption banner, so the boundary rule reads as a footnote
        separator and swallows the opinion start.

        Decide on the line IMMEDIATELY below the rule instead: a real footnote
        rule has small, non-bold footnote text there; a banner divider has bold
        (and usually larger) banner text. Bold-below ⇒ not a footnote rule."""
        below = above = None
        for ln in page.extract_text_lines():
            chars = ln.get("chars") or []
            sizes = [c["size"] for c in chars if c.get("size")]
            if not sizes:
                continue
            sz = median(sizes)
            bold = any("Bold" in (c.get("fontname") or "") for c in chars)
            dy = ln["top"] - rule_top
            if 2 < dy <= 60 and (below is None or ln["top"] < below[0]):
                below = (ln["top"], sz, bold)
            elif -60 <= dy < -2 and (above is None or ln["top"] > above[0]):
                above = (ln["top"], sz, bold)
        if below is None:
            return False
        _, bsz, bbold = below
        if bbold:
            return False  # a bold caption-banner divider, not a footnote rule
        asz = above[1] if above else bsz + 1.0
        return bsz < asz - 0.75
