"""Supreme Court of Connecticut.

Abbreviated-title byline running inline with the opinion text, not bold:
'BRIGHT, J. The plaintiff ...' / 'ALEXANDER, J. A jury found ...'. The shared
abbreviated-title base handles the 'NAME, J. <body>' form directly. The
Connecticut front matter (the 'officially released' notice and the 'Syllabus')
is handled by the shared ``ConnecticutStyle``.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._connecticut import ConnecticutStyle


class ConnecticutSupreme(ConnecticutStyle, AbbrevTitleSupreme):
    court_id = "conn"
    court_label = "Supreme Court of Connecticut."
