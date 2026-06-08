"""Intermediate Court of Appeals of West Virginia.

The Intermediate Court publishes the same two shapes as the Supreme Court of
Appeals — a signed opinion (reversed 'CHIEF JUDGE GREEAR delivered the Opinion
of the Court.' or colon 'WHITE, Judge:') and a per-curiam 'MEMORANDUM DECISION'
(its Rule 21 affirmance, with no byline) — so it reuses the shared
:class:`WestVirginiaStyle` over the reversed-title base (this court seats
Judges, a valid author title there). See :mod:`_westvirginia`.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme
from ._westvirginia import WestVirginiaStyle


class IntermediateCourtOfAppealsOfWestVirginia(
    WestVirginiaStyle, ReversedJusticeSupreme
):
    court_id = "wvactapp"
    court_label = "Intermediate Court of Appeals of West Virginia."
