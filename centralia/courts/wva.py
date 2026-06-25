"""Supreme Court of Appeals of West Virginia.

Two byline forms (a reversed 'JUSTICE WOOTON delivered the Opinion of the
Court.' and a bold all-caps colon 'TRUMP, Justice:' / 'WHITE, Judge,
concurring:') plus a per-curiam 'DISMISSAL ORDER', and the title-page caption-
divider footnote fix — all shared with the Intermediate Court of Appeals in
:mod:`_westvirginia`.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme
from ._westvirginia import WestVirginiaStyle


class WestVirginiaSupreme(WestVirginiaStyle, ReversedJusticeSupreme):
    court_id = "wva"
    court_label = "Supreme Court of Appeals of West Virginia."
