"""United States District Court, District of New Hampshire.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

nhd quirk: these judges number footnotes continuously through the ruling, so a
page whose footnote block runs long carries a tall stack of numeric labels
('4' … '17') at the left text margin — which the shared base's *pleading
line-number rail* sniffer reads as a line-number gutter and then filters away,
shaving the first glyph off every body line on that page ('Strafford' →
'trafford'). A real rail numbers the WHOLE text block, so the stack is
re-qualified by its vertical extent here (see ``_pleading_gutter_by_numbers``).
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfNewHampshire(DistrictBase):
    court_id = "nhd"
    court_label = "United States District Court, District of New Hampshire."

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """A left-margin stack of integers is a pleading LINE-NUMBER RAIL only
        if it numbers the whole text block: it opens in the top margin band and
        runs down to the bottom one. A footnote-label column — the same digits,
        the same x, also mostly sequential — sits entirely in the lower part of
        the page, so the vertical extent separates the two structurally.

        Without this the footnote labels are taken for a gutter and every char
        left of their right edge is filtered off the page, which eats the first
        letter of every line on the page (nhd 65578 p2, nhd 67562 p2)."""
        gx = DistrictBase._pleading_gutter_by_numbers(page)
        if gx is None:
            return None
        tops = [
            w["top"]
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if not tops:
            return None
        if min(tops) > page.height * 0.2:
            return None  # the stack starts mid-page: footnote labels
        if (max(tops) - min(tops)) < page.height * 0.5:
            return None  # too short to be numbering every line
        return gx
