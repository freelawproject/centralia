"""Supreme Court of Minnesota.

Standard bold all-caps byline ('THISSEN, Justice.' / 'MOORE III, Justice.' /
'MCKEIG, Justice (concurring).'); the shared state-supreme base handles it.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class MinnesotaSupreme(StateSupreme):
    court_id = "minn"
    court_label = "Supreme Court of Minnesota."
