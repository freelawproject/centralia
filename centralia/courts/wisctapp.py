"""Wisconsin Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class WisconsinCourtOfAppeals(StateAppellate):
    court_id = "wisctapp"
    court_label = "Wisconsin Court of Appeals."
    strip_para_marker = True  # byline opens with the paragraph marker: "¶1 HRUZ, J."

    def find_footnote_separator(self, page):
        # A long rule separates headmatter from the opinion; only treat a rule
        # with footnote-sized text below it as the footnote separator, so that
        # divider doesn't chop the ¶1 byline + body.
        return self._footnote_sep_small_text_below(page)
