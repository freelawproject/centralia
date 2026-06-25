"""Tennessee Court of Appeals.

Intermediate appellate court; all the layout mechanics — the prose
'delivered' byline, the OPINION-heading opinion start, caption-footnote
routing, e-filing stamp drop (Arial on most files, Helvetica on some),
page-number folding — live in the shared Tennessee appellate base.
"""

from __future__ import annotations

from ._tennessee import TennesseeAppellate


class TennesseeCourtOfAppeals(TennesseeAppellate):
    court_id = "tennctapp"
    court_label = "Tennessee Court of Appeals."
