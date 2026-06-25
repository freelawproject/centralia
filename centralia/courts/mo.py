"""Supreme Court of Missouri.

The author is signed at the end as 'NAME, Judge' — Title-Case ('Zel M. Fischer,
Judge', 'Ginger K. Gooch, Judge') or ALL-CAPS ('KELLY C. BRONIEC, JUDGE'). The
shared MissouriStyle matches the title case-insensitively; the 'The Honorable
..., Judge' trial-judge history line is excluded by the shared base.
"""

from __future__ import annotations

from ._missouri import MissouriStyle
from ._statesupreme import StateSupreme


class MissouriSupreme(MissouriStyle, StateSupreme):
    court_id = "mo"
    court_label = "Supreme Court of Missouri."
