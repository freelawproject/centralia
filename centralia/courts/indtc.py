"""Indiana Tax Court ('indtc').

District-court model: a ')'-railed caption under the 'IN THE / INDIANA TAX
COURT' banner, a centered doc-title heading ('FINAL DECISION ...' /
'ORDER ...'), one ruling by one judge signed at the end.
"""

from __future__ import annotations

from ._district import DistrictBase


class IndianaTaxCourt(DistrictBase):
    court_id = "indtc"
    court_label = "Indiana Tax Court."

    def _is_heading(self, line) -> bool:
        if super()._is_heading(line):
            return True
        low = self.line_plain_text(line).strip().lower()
        return low.startswith(
            ("final decision", "final determination", "order on", "order granting",
             "order denying")
        )
