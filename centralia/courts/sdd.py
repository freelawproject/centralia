"""United States District Court, District of South Dakota.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Half of this corpus is flatbed SCANS with no usable text layer; those are
correctly refused as non-born-digital and are not parsed.
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfSouthDakota(DistrictBase):
    court_id = "sdd"
    court_label = "United States District Court, District of South Dakota."

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """A left-margin stack of integers is a pleading LINE-NUMBER RAIL only
        if it numbers the whole text block: it opens in the top margin band and
        runs down to the bottom one. This judge footnotes heavily and numbers
        them continuously, so a page's footnote-label column ('8' … '21') is
        the same digits at the same x, also sequential — but it sits entirely
        in the lower part of the page. Without the extent test the labels are
        taken for a gutter and every char left of their right edge is filtered
        off the page, eating the first letter of every line (sdd 81136 pp. 2-3).
        """
        gx = DistrictBase._pleading_gutter_by_numbers(page)
        if gx is None:
            return None
        tops = [
            w["top"]
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if not tops:
            return None
        if min(tops) > page.height * 0.2:
            return None  # the stack starts mid-page: footnote labels
        if (max(tops) - min(tops)) < page.height * 0.5:
            return None  # too short to be numbering every line
        return gx

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
