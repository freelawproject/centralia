"""Idaho Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class IdahoCourtOfAppeals(StateAppellate):
    court_id = "idahoctapp"
    court_label = "Idaho Court of Appeals."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers

    # Senior/visiting judges sit by designation as 'NAME, Judge Pro Tem'
    # (no trailing period). Add the spelled-out pro-tempore titles so the
    # byline grammar recognizes the opinion start; without them the whole
    # document falls into headmatter (state_v._reyes).
    author_titles = ("Judge Pro Tempore", "Judge Pro Tem") + StateAppellate.author_titles

    # Idaho sets the body at 1.5 leading (~21pt) and single-spaces block quotes
    # / footnotes at ~14pt. The default bands (single<22) read the 21pt body as
    # a block quote, tagging the whole opinion as quoted. Shift the bands down
    # so 14→single (block quote) and 21→body.
    gap_tight_max = 11
    gap_single_max = 17

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Fold the ')'-railed caption (The Banded Bracket) into a two-column
        block so parties sit left of the centered rail and the docket/clerk
        column sits right — like delch/wash."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d
