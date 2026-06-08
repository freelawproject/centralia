"""United States District Court, Central District of California.

Two filing shapes share this court: a regular memorandum/order (handled by the
district base — signature block + document-type heading) and the 'CIVIL MINUTES
- GENERAL' minute order, whose author is the 'Present: The Honorable NAME,
UNITED STATES DISTRICT JUDGE' line and whose ruling begins at 'Proceedings:'.
"""

from __future__ import annotations

from ._district import DistrictBase


class CentralDistrictOfCalifornia(DistrictBase):
    court_id = "cacd"
    court_label = "United States District Court, Central District of California."

    def find_authors(self, all_segments) -> list:
        self._district_author = (
            self._present_author(all_segments)
            or self._signature_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        # Minute order: the ruling proper starts at the 'Proceedings:' line.
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self.line_plain_text(seg[0]).strip().lower().startswith(
                "proceedings:"
            ):
                return [i]
        return super().find_authors(all_segments)
