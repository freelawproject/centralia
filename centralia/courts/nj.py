"""Supreme Court of New Jersey.

Byline leads with the title: 'JUSTICE NORIEGA delivered the opinion of the
Court.' / 'JUSTICE FASCIALE, dissenting.'. Each opinion is preceded by a
syllabus headed 'JUSTICE X, writing for a unanimous Court.' — that heading is
not an opinion verb phrase, so the reversed-justice base treats it as headmatter
and only the 'delivered'/kind byline starts the opinion.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class NewJerseySupreme(ReversedJusticeSupreme):
    court_id = "nj"
    court_label = "Supreme Court of New Jersey."
