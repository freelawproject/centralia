"""Office of the Attorney General of Maryland. ('mdag') — AG letter/formal opinions on the shared AG base."""

from __future__ import annotations

from collections import Counter

from ._agletter import AGLetterBase


class MarylandAttorneyGeneral(AGLetterBase):
    court_id = "mdag"
    court_label = "Office of the Attorney General of Maryland."

    # ------------------------------------------------------------------
    # Footnote separator
    #
    # These opinions are set on a deep left margin — the body rail is at
    # x=133 of 612 (and at x=75 on the reduced-scale copies of the same
    # documents that also sit in the corpus). The Word separator is the
    # 2-inch rule at that rail: 144pt on the full-size sheet, 117.8pt on
    # the reduced one. Two things in the inherited chain miss it:
    #
    #   * ``StateSupreme`` fences the rule to the bottom half of the page.
    #     An AG opinion often runs a page with more footnote than body —
    #     108oag64 p3 puts the rule at y=348 of 792, 109oag3 p5 at y=253 —
    #     and every note on such a page was read as prose. That is the
    #     whole of this court's loss: 15 of 30 documents, always a
    #     CONTIGUOUS run of numbers (footnotes 5-10, 3-7), because a whole
    #     page's zone goes at once.
    #   * the fenceless second pass (``footnote_sep_fixed_left_rule``)
    #     anchors on ``body_baseline_x0`` (72pt), so a rule at this
    #     court's 133pt rail is out of its window before it is looked at.
    #
    # Read the rail off the page instead of assuming one, and take the
    # rule by its proportion of that page's own measure: the separator is
    # ~0.42 of the measure on both scalings, and the only other rule the
    # template draws at the rail is the letterhead rule at 1.0. There is
    # no overlap, so no position fence is needed — and none is used.
    # ------------------------------------------------------------------

    @staticmethod
    def _measured_rail(page):
        """The page's own left text rail and text measure, read off the
        lines it sets at full measure. Recurrence is what makes 'leftmost'
        safe — one outdented stray cannot move the rail."""
        counts, right = Counter(), []
        for line in page.extract_text_lines():
            if (line["x1"] - line["x0"]) < page.width * 0.45:
                continue
            counts[round(line["x0"])] += 1
            right.append(line["x1"])
        recurring = [x for x, hits in counts.items() if hits >= 2]
        if not recurring:
            return None, None
        rail = float(min(recurring))
        return rail, max(right) - rail

    def find_footnote_separator(self, page):
        sep = self._measured_footnote_rule(page)
        if sep is not None:
            return sep
        return super().find_footnote_separator(page)

    def _measured_footnote_rule(self, page):
        rail, measure = self._measured_rail(page)
        if rail is None or not measure:
            return None
        text_lines = [
            line
            for line in page.extract_text_lines()
            if (line.get("text") or "").strip()
        ]
        best = None
        for objs in (page.rects, page.lines):
            for shape in objs:
                if abs(shape["bottom"] - shape["top"]) >= 3:
                    continue
                x0 = min(shape["x0"], shape["x1"])
                x1 = max(shape["x0"], shape["x1"])
                width = x1 - x0
                if abs(x0 - rail) > 3:
                    continue
                # Well short of the measure: the letterhead rule at the
                # same rail spans it whole.
                if not (measure * 0.2 <= width <= measure * 0.6):
                    continue
                # A rule inside a text line's band underlines that line.
                if any(
                    line["top"] - 1 <= shape["top"] <= line["bottom"] + 5
                    and line["x0"] < x1
                    and line["x1"] > x0
                    for line in text_lines
                ):
                    continue
                if not any(line["top"] > shape["top"] + 1 for line in text_lines):
                    continue
                if best is None or shape["top"] < best:
                    best = shape["top"]
        return best
