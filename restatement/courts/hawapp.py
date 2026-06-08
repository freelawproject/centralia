"""Intermediate Court of Appeals of Hawaiʻi.

Shares the Hawaiʻi appellate format (HawaiiStyle): each writing opens with an
'OPINION OF THE COURT BY <NAME>' / 'CONCURRING/DISSENTING OPINION BY <NAME>'
heading (or an 'ORDER ...' disposition header), and the 'FOR PUBLICATION ...'
banner + red e-filing stamp are dropped. Restricting the author search to those
headings stops a '<Counsel>, Presiding Judge' / trial-judge line being taken as
the author.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._hawaii import HawaiiStyle


class IntermediateCourtOfAppealsOfHawaii(HawaiiStyle, StateAppellate):
    court_id = "hawapp"
    court_label = "Intermediate Court of Appeals of Hawaiʻi."
