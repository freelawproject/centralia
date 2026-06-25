"""Louisiana Court of Appeal.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class LouisianaCourtOfAppeal(StateAppellate):
    def _abbrev_parse(self, text):
        r = super()._abbrev_parse(text)
        if r is not None:
            return r
        # 'MARCOTTE, J' — the Second Circuit omits the period on the title
        t = text.strip()
        if t.endswith((", J", ", C.J", ", P.J")):
            return super()._abbrev_parse(t + ".")
        return None

    court_id = "lactapp"
    court_label = "Louisiana Court of Appeal."
    # Legal-size pages (612x1008): content runs to y~880, so the letter-size
    # bottom margin must not chop it. Body anchored at x~108 with 36pt
    # paragraph indents.
    margin_bottom = 985
    body_baseline_x0 = 108.0
