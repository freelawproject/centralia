"""Kansas Court of Appeals.

Intermediate appellate court sharing the Kansas front matter: a centered,
all-caps title after the case caption ('SYLLABUS BY THE COURT' for an authored
ruling, or 'ORDER' / 'ORIGINAL PROCEEDING IN DISCIPLINE' for an order). It
reuses :class:`KansasStyle` over the appellate base — the byline ('NAME, J.:' /
'PER CURIAM:') is recognized by the abbreviated-title parser, the syllabus block
is lifted into the syllabus field, and an order (no byline) opens at its centered
type header. See :mod:`_kansas`.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._kansas import KansasStyle


class KansasCourtOfAppeals(KansasStyle, StateAppellate):
    court_id = "kanctapp"
    court_label = "Kansas Court of Appeals."
