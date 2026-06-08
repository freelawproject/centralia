"""Supreme Judicial Court of Massachusetts.

Byline abbreviates the title and runs inline with the opinion text, not bold:
'GAZIANO, J. This case arises ...' / 'KAFKER, J. After ...'. The panel line
('Present: Budd, C.J., ...') and the trial-judge history ('The case was heard
by Michael K. Callan, J.') are excluded by the abbreviated-title base. The slip
front matter (NOTICE -> dropped, reporter headnotes -> syllabus, per-curiam
orders) is shared with the Appeals Court in :mod:`_massachusetts`.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._massachusetts import MassachusettsStyle


class MassachusettsSupreme(MassachusettsStyle, AbbrevTitleSupreme):
    court_id = "mass"
    court_label = "Supreme Judicial Court of Massachusetts."
