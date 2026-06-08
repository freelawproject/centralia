"""Nebraska Supreme Court.

Advance-sheet format: a caption, a numbered syllabus, the panel that heard the
case ('Funke, C.J., Cassel, Stacy, Papik, Freudenberg, and Bergevin, JJ.'),
then the authoring judge on its own line — a title-case surname with an
abbreviated title: 'Papik, J.' / 'Cassel, J.' / 'Funke, C.J.'. The shared
abbreviated-title base handles 'NAME, J.' once title-case surnames are allowed;
the panel line is a comma-continuation (plural 'JJ.') and is not a byline, and
the trial-court history line ('Martin, Judge. Affirmed.') uses the spelled-out
'Judge' and trails a disposition, so it is not matched either.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._nebraska import NebraskaReporterStyle


class NebraskaSupreme(NebraskaReporterStyle, AbbrevTitleSupreme):
    court_id = "neb"
    court_label = "Nebraska Supreme Court."
    allow_titlecase_name = True
