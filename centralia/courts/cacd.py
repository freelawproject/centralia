"""United States District Court, Central District of California.

The CACD docket in this reporter is a mix of two very different things, and the
distinction is what a reader most needs:

  * a court RULING — a 'CIVIL MINUTES - GENERAL' minute order (author on the
    'Present: The Honorable NAME, UNITED STATES DISTRICT JUDGE' line, ruling from
    'Proceedings:'), or a memorandum/order the judge signed (a signature block
    ending 'UNITED STATES DISTRICT JUDGE'); and
  * an attorney FILING — a motion, a position paper, or a [PROPOSED] order on
    California pleading paper (numbered lines, an attorney caption block). It
    carries no judicial author; it becomes a ruling only once the judge signs
    it (a signed [PROPOSED] order is then a real order).

The district base always finds *some* author (falling back to the caption's
assigned-judge line), so a bare filing would otherwise read as a judge-authored
opinion. Classify the document by the two ruling signals — a minute-order
header or a judge signature at the foot — and mark everything else FILING,
dropping the fabricated author so it is not presented as the court's opinion.
"""

from __future__ import annotations

import re

import pdfplumber

from ..models import DocType
from ._district import DistrictBase

# A judge's conformed-signature title line at the foot of a signed ruling.
_JUDGE_SIG = re.compile(
    r"UNITED STATES (DISTRICT|MAGISTRATE|CIRCUIT|BANKRUPTCY|CHIEF) JUDGE", re.I
)


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

    def _is_ruling(self, pdf_path) -> bool:
        """True when the document is a court ruling, not an attorney filing: a
        'CIVIL MINUTES' minute order, or a judge's signature-block title line at
        the foot of a page (a signed order — including a signed [PROPOSED] order
        whose signature sits a page or two before a trailing signature/service
        exhibit). Scan each page's foot, not just the last page: the caption's
        'Present:'/assigned-judge lines sit at the TOP of page 1, so a
        foot-of-page title is a conformed signature, not a caption reference —
        and empirically an unsigned proposed order carries no such foot title."""
        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages
            if not pages:
                return False
            for page in pages:
                lines = (page.extract_text() or "").splitlines()
                if "CIVIL MINUTES" in "\n".join(lines):
                    return True
                if _JUDGE_SIG.search("\n".join(lines[-22:])):
                    return True
        return False

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        if doc.non_digital:
            return doc
        if not self._is_ruling(pdf_path):
            doc.doc_type = DocType.FILING
            # No judicial author on an attorney filing — the base fell back to
            # the caption's assigned judge, which is not the document's author.
            for op in doc.opinions:
                op.author = ""
        return doc
