"""United States District Court, Western District of Louisiana.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

**Footnote labels are not a pleading-paper line-number rail.** lawd rulings set
footnotes at the left text margin, each opening with its number ('6 Id. at 3.' /
'7 …'), so a page carrying eight or more footnotes shows a far-left column of
small sequential integers — the shape the shared base's no-rule pleading-gutter
fallback looks for. It then filtered out every char starting left of that
column's right edge, which on lawd IS the body's own left margin, deleting the
first glyph of every body line on the page. See
``_pleading_gutter_by_numbers``.
"""

from __future__ import annotations

from ._district import DistrictBase

# A pleading-paper line-number rail runs 1-28 down the full height of the
# sheet. A footnote-label column occupies only the bottom fifth of it.
_GUTTER_MIN_SPAN = 0.5
_GUTTER_MIN_COUNT = 15


class WesternDistrictOfLouisiana(DistrictBase):
    court_id = "lawd"
    court_label = "United States District Court, Western District of Louisiana."

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """Accept a number-inferred line-number gutter only when the number
        column really runs down the page: ~25 numbers spanning most of the
        sheet's height. A footnote block gives 8-10 numbers inside the bottom
        fifth, and treating those as a gutter destroys the body text.
        """
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
        if len(tops) < _GUTTER_MIN_COUNT:
            return None
        span = (max(tops) - min(tops)) / max(page.height, 1.0)
        return gx if span >= _GUTTER_MIN_SPAN else None
