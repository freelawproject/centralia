"""Intermediate Court of Appeals of West Virginia.

The Intermediate Court publishes the same two shapes as the Supreme Court of
Appeals — a signed opinion (reversed 'CHIEF JUDGE GREEAR delivered the Opinion
of the Court.' or colon 'WHITE, Judge:') and a per-curiam 'MEMORANDUM DECISION'
(its Rule 21 affirmance, with no byline) — so it reuses the shared
:class:`WestVirginiaStyle` over the reversed-title base (this court seats
Judges, a valid author title there). See :mod:`_westvirginia`.

It carries the same clerk's electronic FILED stamp on the title page ('ASHLEY
N. DEEM, CHIEF DEPUTY CLERK / INTERMEDIATE COURT OF APPEALS / OF WEST
VIRGINIA'), interleaved into the caption rows, so it reuses
:class:`WestVirginiaFiledStamp` as well.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme
from ._westvirginia import WestVirginiaStyle
from .wva import WestVirginiaFiledStamp


class IntermediateCourtOfAppealsOfWestVirginia(
    WestVirginiaFiledStamp, WestVirginiaStyle, ReversedJusticeSupreme
):
    court_id = "wvactapp"
    court_label = "Intermediate Court of Appeals of West Virginia."
