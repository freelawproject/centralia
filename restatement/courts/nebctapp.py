"""Nebraska Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.'
/ 'NAME, J.' / 'PER CURIAM'). Shares the Nebraska Advance Sheets reporter format
(running-header furniture dropped, numbered syllabus routed to the syllabus
field) via NebraskaReporterStyle.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._nebraska import NebraskaReporterStyle


class NebraskaCourtOfAppeals(NebraskaReporterStyle, StateAppellate):
    court_id = "nebctapp"
    court_label = "Nebraska Court of Appeals."
