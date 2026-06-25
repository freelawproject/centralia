"""New York Surrogate's Court, published as 'NY Slip Op' (U).

Shares the NewYorkSlipOp cover-page + e-filed-decision format.
"""

from __future__ import annotations

from ._nyslipop import NewYorkSlipOp


class NewYorkSurrogatesCourt(NewYorkSlipOp):
    court_id = "nysurct"
    court_label = "Surrogate's Court of the State of New York."
