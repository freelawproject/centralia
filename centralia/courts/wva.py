"""Supreme Court of Appeals of West Virginia.

Two byline forms (a reversed 'JUSTICE WOOTON delivered the Opinion of the
Court.' and a bold all-caps colon 'TRUMP, Justice:' / 'WHITE, Judge,
concurring:') plus a per-curiam 'DISMISSAL ORDER', and the title-page caption-
divider footnote fix — all shared with the Intermediate Court of Appeals in
:mod:`_westvirginia`.

Both West Virginia appellate courts stamp the title page with the clerk's
electronic FILED block, pinned in the top-right corner:

    FILED
    May 13, 2026
    No. 24-765 released at 3:00 p.m.
    C. CASEY FORBES, CLERK
    SUPREME COURT OF APPEALS
    OF WEST VIRGINIA

It is set in a DIFFERENT TYPEFACE from the document (Arial against the
opinion's Times New Roman) at 7-14pt, and its rows are interleaved between the
caption's rows rather than sitting above or below them. Line clustering
therefore folds the stamp into the caption a glyph at a time — 'Petitioner
Below, Petitioner ASINHTLEEYR MNE. DDEIAETME, ...' — and where a stamp row
lands beside a byline it destroys the byline outright ('TITUS, Justice, joined
by Bunn, Chief Justice, dissenting: C. CASEY FORBES, CLERK' parsed to no
author, so the whole document came back with zero opinions).

:class:`WestVirginiaFiledStamp` removes it by the one structural cue that
identifies it — a top-of-page, flush-right run set in a font family the
document does not otherwise use — in ``correct_page_geometry``, the hook the
completeness sweep and the audit read the page through, and records every
removed row in the Removed box.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme
from ._westvirginia import WestVirginiaStyle


class WestVirginiaFiledStamp:
    """Drop the clerk's electronic FILED stamp off the title page.

    Belongs in :mod:`_westvirginia` beside the rest of the shared West
    Virginia template; it lives here because both WV courts import it and this
    module is the senior of the pair.
    """

    # The stamp sits in the top-right corner of the title page: every row's
    # right edge reaches past 72% of the page width, and the whole block ends
    # inside the top third.
    stamp_right_frac = 0.72
    stamp_top_frac = 0.35

    @staticmethod
    def _font_family(char) -> str:
        """Typeface family of ``char``, ignoring the subset tag and the style.

        'BCDGEE+TimesNewRomanPS-ItalicMT' and 'TimesNewRomanPSMT' are one
        family; 'BCDGEE+Arial-BoldMT' and 'ArialMT' are another.
        """
        name = (char.get("fontname") or "").split("+")[-1]
        name = name.split(",")[0].split("-")[0]
        if name.endswith("MT"):
            name = name[:-2]
        return name

    def correct_page_geometry(self, page) -> None:
        if page.page_number == 1:
            self._strip_filed_stamp(page)
        super().correct_page_geometry(page)

    def _strip_filed_stamp(self, page) -> None:
        chars = page.chars
        if not chars:
            return
        families: dict = {}
        for char in chars:
            families[self._font_family(char)] = (
                families.get(self._font_family(char), 0) + 1
            )
        body_family = max(families.items(), key=lambda kv: kv[1])[0]
        if len(families) < 2:
            return

        top_limit = page.height * self.stamp_top_frac
        right_limit = page.width * self.stamp_right_frac
        foreign = [
            i
            for i, char in enumerate(chars)
            if self._font_family(char) != body_family and char["top"] < top_limit
        ]
        if not foreign:
            return

        # Group the foreign glyphs into rows; a row belongs to the stamp only if
        # it actually reaches the flush-right corner. That keeps a one-off
        # symbol glyph set in another face inside the caption text.
        rows: dict = {}
        for i in foreign:
            rows.setdefault(round(chars[i]["top"] / 4), []).append(i)
        drop, dropped_rows = [], []
        for _key, row in sorted(rows.items()):
            if max(chars[i]["x1"] for i in row) < right_limit:
                continue
            text = "".join(
                (chars[i].get("text") or "")
                for i in sorted(row, key=lambda i: chars[i]["x0"])
            ).strip()
            if text:
                dropped_rows.append(text)
            drop.extend(row)
        if not drop:
            return
        if getattr(self, "_wv_stamp_dropped", None) is None:
            self._wv_stamp_dropped = []
        self._wv_stamp_dropped.extend(dropped_rows)
        for i in sorted(drop, reverse=True):
            del chars[i]

    def extract(self, pdf_path):
        self._wv_stamp_dropped = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Surface the stamp BEFORE the completeness sweep — the sweep runs
        inside ``super().extract()``, so appending afterwards would leave the
        stamp rows reading as unplaced content."""
        seen, extra = set(), []
        for text in getattr(self, "_wv_stamp_dropped", []) or []:
            if text not in seen:
                seen.add(text)
                extra.append(text)
        if extra:
            doc.dropped = list(doc.dropped) + [
                "[clerk's FILED stamp removed: " + " / ".join(extra) + "]"
            ]
        super()._sweep_residual(doc, source_pages)


class WestVirginiaSupreme(
    WestVirginiaFiledStamp, WestVirginiaStyle, ReversedJusticeSupreme
):
    court_id = "wva"
    court_label = "Supreme Court of Appeals of West Virginia."
