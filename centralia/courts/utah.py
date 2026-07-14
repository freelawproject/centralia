"""Supreme Court of the State of Utah.

Reversed-title byline. The opinion body opens with 'JUSTICE NIELSEN, opinion of
the Court:' (majority) or 'JUSTICE PETERSEN, concurring:' / '..., dissenting:'
(separate writings). The title-page authorship summary ('JUSTICE NIELSEN
authored the opinion of the Court, in which CHIEF JUSTICE DURRANT ... joined.')
and its joinder roster are left as headmatter — only the body byline starts the
opinion, so the two don't double-count. 'ASSOCIATE CHIEF JUSTICE' is a title.
The shared reversed-title base handles these forms.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class UtahSupreme(ReversedJusticeSupreme):
    court_id = "utah"
    court_label = "Supreme Court of the State of Utah."
    # Footnote separator is a full-measure line of '_' text (not a vector
    # rule), footnotes set at body size — detect the underscore line by width.
    footnote_sep_text_min_width = 200
