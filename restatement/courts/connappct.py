"""Connecticut Appellate Court.

Intermediate appellate court. Author byline at the opinion start ('NAME, J.' /
'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and
drops the trial-judge / panel-roster caption lines. The Connecticut front matter
(the 'officially released' notice and the 'Syllabus') is handled by the shared
``ConnecticutStyle`` — the same as the Supreme Court.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._connecticut import ConnecticutStyle


class ConnecticutAppellateCourt(ConnecticutStyle, StateAppellate):
    court_id = "connappct"
    court_label = "Connecticut Appellate Court."
