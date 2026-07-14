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
    # Block quotes are indented on both margins and single-spaced at ~14pt —
    # below gap_tight_max, so the gap bands read them as 'notice'. Re-tag them
    # by their both-margins indent (the body is 1.5/double-spaced at ~24-28pt).
    blockquote_by_indent = True
    # Iowa's separator is a fixed ~2-inch rule (~144-155pt). Its long page-1
    # caption is bracketed by full-measure rules, and the lower one sits in the
    # bottom half — without this cap the finder takes that full-width divider
    # for the separator and shoves the disposition block into a phantom footnote.
    footnote_sep_max_width = 200.0
