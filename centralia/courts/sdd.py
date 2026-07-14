"""United States District Court, District of South Dakota.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfSouthDakota(DistrictBase):
    court_id = "sdd"
    court_label = "United States District Court, District of South Dakota."

    def find_authors(self, all_segments) -> list:
        """The document-type title ('ORDER AWARDING / SANCTIONS FOR
        SPOLIATION OF / EVIDENCE') sits INSIDE the caption columns, right of
        the drawn mid vertical — so the generic heading scan runs pages ahead
        to the decretal 'ORDER' section and the whole ruling lands in the
        headmatter. Start the ruling at the first page-1 segment below the
        caption's mid vertical instead (the ncwd/akd model, keyed on the
        drawn '|' rather than a ')' rail)."""
        pw = getattr(self, "_page1_width", None) or 612.0
        mids = [
            bot
            for x, _top, bot in getattr(self, "_p1_vrule_spans", []) or []
            if pw * 0.35 <= x <= pw * 0.65
        ]
        if mids:
            cap_bottom = max(mids)
            self._district_author = (
                self._signature_author(all_segments)
                or self._present_author(all_segments)
                or self._byline_author(all_segments)
                or self._caption_judge(all_segments)
            )
            for i, (pno, seg, _k) in enumerate(all_segments):
                if pno != 1:
                    break
                if seg and seg[0].get("top", 0) > cap_bottom + 4:
                    return [i]
        return super().find_authors(all_segments)
