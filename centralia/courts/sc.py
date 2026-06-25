"""Supreme Court of South Carolina.

Reversed-title byline with a colon, bold, running inline with the opinion text:
'JUSTICE JAMES: In this case ...' / 'CHIEF JUSTICE KITTREDGE: ...' /
'PER CURIAM: ...'. A 'KITTREDGE, C.J., FEW, JAMES, HILL and VERDIN, JJ.,
concur.' line is a concurrence-vote roster (surname-first, no leading title),
not an opinion start, and is left as body. The shared reversed-title base
handles the colon form.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class SouthCarolinaSupreme(ReversedJusticeSupreme):
    court_id = "sc"
    court_label = "The Supreme Court of South Carolina."
