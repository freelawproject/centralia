"""United States District Court, Middle District of Louisiana.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

lamd quirk — FOOTNOTE LABELS ARE NOT A PLEADING RAIL. This district cites in
footnotes rather than in text, so a busy page stacks eight-plus label numerals
('14' … '21') hard against the left margin down the footnote zone. That column
is the same shape the shared pleading-paper heuristic looks for (a far-left run
of ascending integers), so it was read as a California-style line-number gutter
and every glyph left of the labels' right edge was filtered away — clipping the
first one to three characters off EVERY body line on the page ('is not aware' →
'not aware', 'its opposition' → 'opposition'). A real rail is distinguished
structurally, not by text: see ``_pleading_gutter_by_numbers`` below.
"""

from __future__ import annotations

from ._district import DistrictBase


class MiddleDistrictOfLouisiana(DistrictBase):
    court_id = "lamd"
    court_label = "United States District Court, Middle District of Louisiana."

    def _pleading_gutter_by_numbers(self, page):
        """Right edge of a pleading-paper line-number gutter, or None.

        Tightens the shared fallback with the three properties that separate a
        printed line-number rail from an accidental column of numerals:

        * it numbers every typed line, so it is DENSE (>= 14 numerals a page);
        * it runs the full text block, so it SPANS most of the sheet;
        * it is absolute, so it STARTS AT 1 (or 2, when the header eats one).

        A footnote-label column fails all three: it is short, confined to the
        footnote zone at the foot of the page, and starts wherever the
        document's running footnote count happened to reach.
        """
        nums = [
            (int(w["text"]), w["x1"], w["top"])
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if len(nums) < 14:
            return None
        tops = [n[2] for n in nums]
        if (max(tops) - min(tops)) < page.height * 0.55:
            return None
        if min(n[0] for n in nums) > 2:
            return None
        return super()._pleading_gutter_by_numbers(page)
