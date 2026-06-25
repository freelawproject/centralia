"""Washington Court of Appeals.

Same slip-print anatomy as the Washington Supreme Court (wash.py): the
em-dash byline ('BIRK, J. — The Washington State Health Care Authority …'),
two page-1 filing stamps above the banner, a ')'-rail caption whose closing
shelf must not be taken for a footnote separator (the real one is a typed
underscore run or a thin rule with footnote-sized text below), running
heads, and bottom page numbers that restart per writing. Inherits all of
it; only the identity differs. Division-specific quirks land here.
"""

from __future__ import annotations

from .wash import WashingtonSupreme


class WashingtonCourtOfAppeals(WashingtonSupreme):
    court_id = "washctapp"
    court_label = "Washington Court of Appeals."
