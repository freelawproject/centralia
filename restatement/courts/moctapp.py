"""Missouri Court of Appeals.

The author is signed at the end as 'NAME, Judge' / 'NAME, Chief Judge', in
Title-Case or ALL-CAPS ('EDWARD R. ARDINI, JR., JUDGE', 'JAMES M. DOWD, JUDGE').
The shared MissouriStyle matches the title case-insensitively; the appellate base
drops the trial-judge / panel-roster lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._missouri import MissouriStyle


class MissouriCourtOfAppeals(MissouriStyle, StateAppellate):
    court_id = "moctapp"
    court_label = "Missouri Court of Appeals."
