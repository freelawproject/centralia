"""Supreme Court of Texas.

Byline leads with the title: 'JUSTICE BUSBY delivered the opinion of the
Court.' / 'CHIEF JUSTICE BLACKLOCK delivered ...' / 'JUSTICE HUDDLE filed an
opinion concurring in part and dissenting in part.'. Title-case mentions in the
body ('Justice Marshall explained ...') are not all-caps and are ignored.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class TexasSupreme(ReversedJusticeSupreme):
    court_id = "tex"
    court_label = "Supreme Court of Texas."

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    # ---- footnotes -------------------------------------------------------
    #
    # Texas draws exactly two thin rules, and they are cleanly separated
    # (measured over all 50 documents / 323 thin rules in the corpus):
    #
    #   * the footnote separator — 144.0pt wide, starting either ON the page's
    #     own left text rail (228 of them) or one half-inch inside it (48);
    #   * the disposition rule under 'OPINION DELIVERED' — 180pt wide, starting
    #     216pt right of the rail, in the page's right half (47).
    #
    # Neither width nor offset overlaps, and no page carries two separators.
    # 275 of the 276 separators are corroborated by footnote-size text or a
    # raised label beneath them; the 47 right-hand rules corroborate as neither.
    #
    # The shared finder loses 23 of those separators — every one on a page
    # whose footnote is long enough to push its own rule above mid-page (the
    # dissent in greystar_1 p8 runs from y=331 to y=665, so its rule sits at
    # y=323 of 792). Those pages fall through to ``_fenceless_sep``, which
    # asks for the rule at ``body_baseline_x0 + 4`` = 76 — Texas sets its body
    # at 108 and indents the rule to 144 in some documents, so nothing matched
    # and every footnote on the page was delivered as prose.
    def _fenceless_sep(self, page):
        """The 2-inch separator, read at the page's OWN measured rail and with
        no vertical fence. Corroborated by what sits beneath it, so the
        right-hand disposition rule cannot stand in for it."""
        rail = self._page_rail(page)
        if rail is None:
            return super()._fenceless_sep(page)
        tops = [
            r["top"]
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2.5
            and abs((r["x1"] - r["x0"]) - 144.0) <= 6.0
            and -4.0 <= r["x0"] - rail <= 40.0
            and (
                self._rule_over_footnotes(page, r["top"])
                or self._labelled_note_below(page, r["top"])
            )
        ]
        return min(tops) if tops else super()._fenceless_sep(page)

    @staticmethod
    def _page_rail(page):
        """The page's own left text rail — the leftmost x0 that RECURS among
        its full-measure lines. Recurrence is what makes 'leftmost' safe: one
        outdented stray cannot move the rail."""
        xs: dict = {}
        for line in page.extract_text_lines():
            if line.get("x1", 0) - line.get("x0", 0) < page.width * 0.45:
                continue
            key = round(line.get("x0", 0))
            xs[key] = xs.get(key, 0) + 1
        recurring = [x for x, hits in xs.items() if hits >= 2]
        return float(min(recurring)) if recurring else None
