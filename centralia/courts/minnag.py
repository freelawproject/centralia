"""Office of the Minnesota Attorney General. ('minnag') — AG letter/formal opinions on the shared AG base."""

from __future__ import annotations

from ._agletter import AGLetterBase


class MinnesotaAttorneyGeneral(AGLetterBase):
    court_id = "minnag"
    court_label = "Office of the Minnesota Attorney General."
    # The topic headnote starts at y~31, above the default top margin.
    margin_top = 12
