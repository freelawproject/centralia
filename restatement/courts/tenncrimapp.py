"""Tennessee Court of Criminal Appeals.

Intermediate appellate court; all the layout mechanics — the prose
'delivered' byline, the OPINION-heading opinion start, caption-footnote
routing, e-filing stamp drop, page-number folding — live in the shared
Tennessee appellate base.
"""

from __future__ import annotations

from ._tennessee import TennesseeAppellate


class TennesseeCourtOfCriminalAppeals(TennesseeAppellate):
    court_id = "tenncrimapp"
    court_label = "Tennessee Court of Criminal Appeals."
