"""Supreme Court of Iowa.

Title-case byline ('Christensen, Chief Justice.' / 'Mansfield, Justice.'); the
shared state-supreme base handles it.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class IowaSupreme(StateSupreme):
    court_id = "iowa"
    court_label = "Supreme Court of Iowa."
    # Page numbers print as bare numbers between paragraphs — fold them into
    # page-break markers so the wrapped paragraphs rejoin.
    fold_page_numbers = True
