"""Oregon Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class OregonCourtOfAppeals(StateAppellate):
    court_id = "orctapp"
    court_label = "Oregon Court of Appeals."
