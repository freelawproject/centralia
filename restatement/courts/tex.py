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
