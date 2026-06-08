"""Civil Court of the City of New York, published as 'NY Slip Op' (U).

Shares the NewYorkSlipOp cover-page + e-filed-decision format.
"""

from __future__ import annotations

from ._nyslipop import NewYorkSlipOp


class NewYorkCivilCourt(NewYorkSlipOp):
    court_id = "nycivct"
    court_label = "Civil Court of the City of New York."
