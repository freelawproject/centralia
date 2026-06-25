"""New York Family Court, published as 'NY Slip Op' (U).

Shares the NewYorkSlipOp cover-page + e-filed-decision format.
"""

from __future__ import annotations

from ._nyslipop import NewYorkSlipOp


class NewYorkFamilyCourt(NewYorkSlipOp):
    court_id = "nyfamct"
    court_label = "Family Court of the State of New York."
