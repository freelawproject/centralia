"""Oregon Court of Appeals.

Intermediate appellate court in the same Oregon Reports layout as the Supreme
Court (narrow page, NewCenturySchlbk body, star + numbered footnotes — shared via
``OregonReports``). Author byline at the opinion start ('NAME, J.' / 'PER
CURIAM'); the appellate base reuses the abbreviated-title parser and drops the
trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._oregon import OregonReports


class OregonCourtOfAppeals(OregonReports, StateAppellate):
    court_id = "orctapp"
    court_label = "Oregon Court of Appeals."

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        self._apply_or_facets(doc, pdf_path)
        return doc
