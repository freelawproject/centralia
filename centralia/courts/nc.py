"""Supreme Court of North Carolina.

Standard bold all-caps byline ('DIETZ, Justice.' / 'EARLS, Justice.' /
'PER CURIAM.'); the shared state-supreme base handles it directly.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class NorthCarolinaSupreme(StateSupreme):
    court_id = "nc"
    court_label = "Supreme Court of North Carolina."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers
