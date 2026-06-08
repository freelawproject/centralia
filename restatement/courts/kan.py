"""Supreme Court of the State of Kansas.

Abbreviated-title byline with a colon, running inline with the opinion text,
not bold: 'STEGALL, J.: Bethany King ...' / 'WALL, J.: This single-issue
appeal ...' / 'PER CURIAM: ...'. A 'STEGALL, J., not participating.' line is a
non-participation note (a bare comma-continuation, not a byline) and is left as
body. The shared abbreviated-title base handles the colon form; the shared
:class:`KansasStyle` lifts the 'SYLLABUS BY THE COURT' block into the syllabus
field and opens an order (no byline) at its centered type header.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._kansas import KansasStyle


class KansasSupreme(KansasStyle, AbbrevTitleSupreme):
    court_id = "kan"
    court_label = "Supreme Court of the State of Kansas."
