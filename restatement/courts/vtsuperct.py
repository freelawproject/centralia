"""Vermont Superior Court.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from ._district import DistrictBase


class VermontSuperiorCourt(DistrictBase):
    court_id = "vtsuperct"
    court_label = "Vermont Superior Court."
