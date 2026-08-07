"""Supreme Court of the State of Utah.

Reversed-title byline. The opinion body opens with 'JUSTICE NIELSEN, opinion of
the Court:' (majority) or 'JUSTICE PETERSEN, concurring:' / '..., dissenting:'
(separate writings). The title-page authorship summary ('JUSTICE NIELSEN
authored the opinion of the Court, in which CHIEF JUSTICE DURRANT ... joined.')
and its joinder roster are left as headmatter — only the body byline starts the
opinion, so the two don't double-count. 'ASSOCIATE CHIEF JUSTICE' is a title.
The shared reversed-title base handles these forms.
"""

from __future__ import annotations

from typing import Optional

from ._reversedjustice import ReversedJusticeSupreme


class UtahSupreme(ReversedJusticeSupreme):
    court_id = "utah"
    court_label = "Supreme Court of the State of Utah."
    # Footnote separator is a full-measure line of '_' text (not a vector
    # rule), footnotes set at body size — detect the underscore line by width.
    footnote_sep_text_min_width = 200

    # A typed rule is the footnote separator when it spans the page's own text
    # measure and starts at the page's own left rail. Both facets are read off
    # the page; these are the tolerances, not the measurements. Over the 487
    # typed rules in the corpus the two populations do not come close to
    # touching: every one of the 482 separators measures >= 0.964 of the
    # measure and starts within 6.4pt of the rail, while all 5 non-separators
    # (the caption dividers of the Menzies / Davies / R.P. title pages, and one
    # 90pt ornament) measure <= 0.848 and start >= 25pt inside it.
    footnote_sep_text_measure_frac = 0.95
    footnote_sep_text_rail_slack = 12.0

    @staticmethod
    def _is_typed_rule(line) -> bool:
        """Is ``line`` a typed rule — a row of nothing but underscores?"""
        text = (line.get("text") or "").strip()
        return len(text) >= 6 and all(c == "_" for c in text)

    def _footnote_sep_text(self, page) -> Optional[float]:
        """Top of Utah's TYPED footnote separator — a row of '_' glyphs set at
        the body's own measure — read without a page-position fence.

        Utah draws no vector rule anywhere in the corpus: ``page.rects`` and
        ``page.lines`` are both empty on every page, so the typed rule is the
        only separator there is. The notes below it are set at BODY size (12pt
        over 12pt), so no drop in type marks the zone either, and only the
        label digit is raised.

        The base finder fences the typed rule to the bottom half of the page,
        and that fence is what lost the footnotes in 19 of 50 documents: a note
        long enough to fill the rest of the sheet pushes its own separator up
        the page (gardner_v._norman p8 rules at y=361 of 792, walgreen_v.
        _jensen p11 at y=155, state_v._najera p31 at y=99) and the whole zone
        was then delivered as body prose. A label below the rule cannot stand
        in for the fence either: a zone carried over from the previous page
        opens mid-sentence, with no label to read, and those are exactly the
        long notes that push the rule up.

        Position is therefore not read at all. The rule is identified by its
        own geometry against the page's: it spans the measure, and it starts at
        the rail. Utah's layout puts the body above the rule and the notes
        below it, running to the foot of the page, on every page including a
        carried-over zone — so the zone is the rule's remainder."""
        lines = page.extract_text_lines()
        others = [ln for ln in lines if not self._is_typed_rule(ln)]
        if not others:
            return None
        # The page's own measure and left rail, taken from its text.
        measure = max(ln["x1"] - ln["x0"] for ln in others)
        rail = min(ln["x0"] for ln in others)

        best = None
        for ln in lines:
            if not self._is_typed_rule(ln):
                continue
            if (ln["x1"] - ln["x0"]) < measure * self.footnote_sep_text_measure_frac:
                continue
            if ln["x0"] - rail > self.footnote_sep_text_rail_slack:
                continue
            if best is None or ln["top"] < best:
                best = ln["top"]
        return best
