"""United States District Court, District of Rhode Island.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

**Roman-numeral folios.** Several rid filings are long briefs whose front matter
(table of contents, table of authorities) is paged in lower-case roman numerals
— a centred 'vii' / 'viii' in the bottom margin. The base's folio detector only
recognises arabic digits, so those pages' folios were read as body content.
Accepting the roman form registers them as the page's printed folio, which is
both what the page marker should say and what keeps them out of the body.
"""

from __future__ import annotations

from ._district import DistrictBase

_ROMAN = frozenset("ivxlcdm")


class DistrictOfRhodeIsland(DistrictBase):
    court_id = "rid"
    court_label = "United States District Court, District of Rhode Island."

    @staticmethod
    def _page_number_value(text: str) -> str | None:
        """Also read a lower-case roman folio ('vii') as a page number.

        Restricted to lower-case and to two glyphs or more, so a caption's
        'v.' and an upper-case section head ('III.') can never be mistaken for
        a folio. The caller additionally requires the line to stand alone,
        centred or flush right, in a shallow page margin.
        """
        t = str(text or "").strip().strip("-–—  ")
        if 2 <= len(t) <= 8 and t == t.lower() and set(t) <= _ROMAN:
            return t
        return DistrictBase._page_number_value(text)
