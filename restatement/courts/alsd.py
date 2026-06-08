"""United States District Court, Southern District of Alabama.

Shares the Alabama-district caption style (parties | case numbers separated by a
stacked ')' divider column), rendered as a whitespace-preserved facsimile by the
shared base. Opinion opens at the centered, bold document title; signature-block
author; blue bates stamp in the top margin excluded.
"""

from __future__ import annotations

from ._aldistrict import AlabamaDistrictBase


class SouthernDistrictOfAlabama(AlabamaDistrictBase):
    court_id = "alsd"
    court_label = "United States District Court, Southern District of Alabama."
