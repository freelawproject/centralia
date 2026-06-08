"""United States District Court, Eastern District of Missouri.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class EasternDistrictOfMissouri(DistrictBase):
    court_id = "moed"
    court_label = "United States District Court, Eastern District of Missouri."
