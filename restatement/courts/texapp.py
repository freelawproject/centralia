"""Texas Court of Appeals.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from ._district import DistrictBase


class TexasCourtOfAppeals(DistrictBase):
    court_id = "texapp"
    court_label = "Texas Court of Appeals."
