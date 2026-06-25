"""United States District Court, Northern District of Alabama.

Shares the Alabama-district caption style — parties | case numbers separated by a
stacked divider column (']' here) — rendered as a whitespace-preserved facsimile
by the shared base (split by x-gap, so the ']' divider is handled the same as
the Middle/Southern districts' ')'). Opinion opens at the centered, bold
document title; signature-block author; bates / clerk 'FILED' stamp in the top
margin excluded.
"""

from __future__ import annotations

from ._aldistrict import AlabamaDistrictBase


class NorthernDistrictOfAlabama(AlabamaDistrictBase):
    court_id = "alnd"
    court_label = "United States District Court, Northern District of Alabama."
