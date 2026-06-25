"""Supreme Court of Georgia."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class GeorgiaSupreme(StateSupreme):
    court_id = "ga"
    court_label = "Supreme Court of Georgia."
    author_titles = ("Justice", "Chief Justice", "Presiding Justice")
    # Page numbers print as bare numbers between paragraphs — fold them into
    # page-break markers so the wrapped paragraphs rejoin.
    fold_page_numbers = True
    # Georgia's body is single-spaced (~16pt line gap) with a wide left margin
    # (baseline x0≈126, paragraphs indented to ≈162). The default thresholds
    # (tuned for double-spaced, baseline-72 courts) misread the ~16pt gap as a
    # 'notice' and split every line. Retune so the body reads as 'body' and is
    # split on the paragraph indent.
    gap_tight_max = 11
    gap_single_max = 14
    gap_double_max = 27
    body_baseline_x0 = 126.0  # base splits paragraphs at body_baseline_x0+28
    # Georgia prints a small (~8pt) 'NOTICE: ...' publication advisory at the
    # top; the caption/body is ~13pt, so this cleanly removes the whole notice.
    notice_max_size = 10.0
