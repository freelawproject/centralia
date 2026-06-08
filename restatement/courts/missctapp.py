"""Mississippi Court of Appeals.

Intermediate appellate court that uses the same name-first, role-closing-with-a-
colon byline as the Supreme Court ('EMFINGER, J., FOR THE COURT:' /
'CARLTON, P.J., FOR THE COURT:'), but with Judge titles. It reuses the shared
:class:`MississippiStyle` over the appellate base (so the trial-judge / panel-
roster caption lines are still dropped). See :mod:`_mississippi`.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._mississippi import MississippiStyle


class MississippiCourtOfAppeals(MississippiStyle, StateAppellate):
    court_id = "missctapp"
    court_label = "Mississippi Court of Appeals."
    _MS_TITLE_MAP = {
        "JUDGE": "Judge",
        "PRESIDING JUDGE": "Presiding Judge",
        "CHIEF JUDGE": "Chief Judge",
        "J.": "Judge",
        "P.J.": "Presiding Judge",
        "C.J.": "Chief Judge",
    }
