"""New York Supreme Court (trial-level), published as 'NY Slip Op' (U).

Machine-generated cover page + e-filed decision; the shared NewYorkSlipOp base
reads the author from the cover's 'Judge:' line, takes the decision from page 2
on, and drops the republication notice + NYSCEF stamps.
"""

from __future__ import annotations

from ._nyslipop import NewYorkSlipOp


class NewYorkSupremeCourt(NewYorkSlipOp):
    court_id = "nysupct"
    court_label = "Supreme Court of the State of New York."
