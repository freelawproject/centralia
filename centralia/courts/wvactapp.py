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

It also sets its footnotes off the same template — at BODY size (13pt), with
only the label digit raised (8.5pt) — under the same short 2-inch rule at the
page's left text rail. The shared 'is the text under the rule smaller?' test
cannot see that zone, so 9 of 30 documents delivered whole footnote zones as
body prose (chandra_t. footnote 5, bellomy 14 and 20, bradley_a._reed 11-13 and
22). Measured over this court's 185 thin rules the separator is unmistakable:
every one of the 180 rules standing on the rail spans 0.306-0.334 of its page's
measured text width and is a footnote separator; the only others (0.03 and 0.37
of the measure) stand 156-266pt inside the rail. So it reuses
:class:`WestVirginiaFootnoteRule`, which identifies the separator by exactly
that — a short rule on the page's own rail — with no size or position test.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme
from ._westvirginia import WestVirginiaStyle
from .wva import WestVirginiaFiledStamp, WestVirginiaFootnoteRule


class IntermediateCourtOfAppealsOfWestVirginia(
    WestVirginiaFiledStamp,
    WestVirginiaFootnoteRule,
    WestVirginiaStyle,
    ReversedJusticeSupreme,
):
    court_id = "wvactapp"
    court_label = "Intermediate Court of Appeals of West Virginia."
