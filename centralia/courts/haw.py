"""Supreme Court of the State of Hawaiʻi.

Byline is an opinion-of-the-court heading: 'OPINION OF THE COURT BY GINOZA, J.'
/ 'CONCURRING OPINION BY X, J.' / 'DISSENTING OPINION BY X, J.'; a disposition
is an 'ORDER ...' header with a '(By: <panel>)' line (per curiam). The shared
HawaiiStyle restricts the author search to those forms and drops the 'FOR
PUBLICATION ...' banner and the red electronic-filing stamp.
"""

from __future__ import annotations

from ._hawaii import HawaiiStyle
from ._statesupreme import StateSupreme


class HawaiiSupreme(HawaiiStyle, StateSupreme):
    court_id = "haw"
    court_label = "Supreme Court of the State of Hawaiʻi."
