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
        rail = self._page_text_rail(page)
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

    # ``_page_rail`` was a third copy of ``BaseExtractor._page_text_rail``;
    # it calls the shared one now. The method itself stays: the shared
    # ``footnote_sep_fixed_left_rule`` reads only ``page.rects`` and takes a
    # rule on width and position alone, where Texas also needs the stroked
    # vector lines, a window out to the half-inch indent some documents use,
    # and corroboration to tell its 144pt separator from the 180pt
    # 'OPINION DELIVERED' rule.
