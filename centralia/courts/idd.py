"""United States District Court, District of Idaho.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

One corpus file is a scanned image whose only text layer is the CM/ECF header
band; it is flagged as scanned rather than emitted silently empty.
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfIdaho(DistrictBase):
    court_id = "idd"
    styled_headmatter = True
    court_label = "United States District Court, District of Idaho."

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        if not doc.opinions and not doc.summary:
            doc.warnings.append(
                "scanned image-only PDF — no text layer beyond the CM/ECF "
                "header (needs OCR)"
            )
        return doc
