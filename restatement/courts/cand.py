"""United States District Court, Northern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class NorthernDistrictOfCalifornia(DistrictBase):
    court_id = "cand"
    court_label = "United States District Court, Northern District of California."
