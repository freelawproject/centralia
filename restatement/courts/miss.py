"""Supreme Court of Mississippi.

Byline is name-first, bold, all-caps, with a spelled-out title and a role,
closing with a colon ('SULLIVAN, JUSTICE, FOR THE COURT:' /
'KING, JUSTICE, CONCURRING:'). The shared :class:`MississippiStyle` parses it;
this court's titles are Justices.
"""

from __future__ import annotations

from ._mississippi import MississippiStyle
from ._statesupreme import StateSupreme


class MississippiSupreme(MississippiStyle, StateSupreme):
    court_id = "miss"
    court_label = "Supreme Court of Mississippi."
    _MS_TITLE_MAP = {
        "JUSTICE": "Justice",
        "PRESIDING JUSTICE": "Presiding Justice",
        "CHIEF JUSTICE": "Chief Justice",
        "C.J.": "Chief Justice",
        "P.J.": "Presiding Justice",
    }
