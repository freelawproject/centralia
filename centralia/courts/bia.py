"""Board of Immigration Appeals.

Reporter-style headmatter (the 'Cite as 29 I&N Dec. 551 (BIA 2026)' line,
'Matter of X-, Respondent', 'Decided …', the DOJ unit block, a headnote
summary, 'FOR THE RESPONDENT:' counsel, the 'BEFORE: Board Panel:' roster),
then the classic colon byline: 'HUNSUCKER, Appellate Immigration Judge:'
with the opinion body following. Uses the shared state-supreme byline
grammar with the Board's titles.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class BoardOfImmigrationAppeals(StateSupreme):
    court_id = "bia"
    court_label = "Board of Immigration Appeals."
    author_titles = (
        "Deputy Chief Appellate Immigration Judge",
        "Appellate Immigration Judge",
        "Temporary Appellate Immigration Judge",
        "Board Member",
        "Judge",
    )

    def parse_author_line(self, text):
        # the byline ends with a colon ('HANSELL, Appellate Immigration
        # Judge:'); the BEFORE-roster lines end with '.' and name several
        # judges — only the colon form is the author
        t = text.strip()
        if not t.endswith(":"):
            return None
        return super().parse_author_line(t.rstrip(":").strip())
