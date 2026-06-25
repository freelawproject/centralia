"""Massachusetts Appeals Court.

Intermediate appellate court that prints the same slip-opinion front matter as
the Supreme Judicial Court — the publication NOTICE, the 'Present: NAME, ...
JJ.' panel, and the reporter headnotes — so it reuses the shared
:class:`MassachusettsStyle` (NOTICE -> dropped, headnotes -> syllabus, per-curiam
order handling, page-number folding). The author byline opens each opinion
('NAME, J.' / 'NAME, Judge.'); the appellate base reuses the abbreviated-title
parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._massachusetts import MassachusettsStyle


class MassachusettsAppealsCourt(MassachusettsStyle, StateAppellate):
    court_id = "massappct"
    court_label = "Massachusetts Appeals Court."
