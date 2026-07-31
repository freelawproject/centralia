"""Kentucky Court of Appeals.

After the 'OPINION' header and the 'BEFORE: <panel>, JUDGES.' roster, the author
signs inline with an ALL-CAPS surname, the title, and a colon: 'MCNEILL, JUDGE:
This case arises ...'. Separate writings carry the kind in the same form
('NAME, JUDGE, CONCURRING:' / 'NAME, JUDGE, DISSENTING:'). The ALL-CAPS surname
distinguishes the byline from the 'BEFORE:' panel line and the trial-court
history; bold centered section labels ('STANDARD OF REVIEW', 'ANALYSIS') are
headings in the body.
"""

from __future__ import annotations

import re

from ._appellate import StateAppellate
from ._statesupreme import is_caps_name

_KY_JUDGE_TITLES = {"judge", "chief judge", "j", "cj", "pj"}


class KentuckyCourtOfAppeals(StateAppellate):
    court_id = "kyctapp"
    court_label = "Kentucky Court of Appeals."

    @staticmethod
    def _ending_matter_start(blocks):
        """Find the counsel/signature section after the ruling closes."""
        concur = None
        for i, block in enumerate(blocks):
            text = re.sub(r"<[^>]+>", "", block.text or "").strip().upper()
            if text.rstrip(":.") in {"ALL CONCUR", "ALL CONCURRED"}:
                concur = i
        start = concur + 1 if concur is not None else 0
        for i in range(start, len(blocks)):
            text = re.sub(r"<[^>]+>", "", blocks[i].text or "").strip().upper()
            if any(
                marker in text
                for marker in ("ON THE BRIEFS", "BRIEFS FOR", "ORAL ARGUMENT FOR", "ENTERED:")
            ):
                return i
        return None

    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        if not doc.opinions:
            return doc
        blocks = doc.opinions[-1].blocks
        cut = self._ending_matter_start(blocks)
        if cut is not None:
            doc.trailer = list(doc.trailer) + blocks[cut:]
            doc.opinions[-1].blocks = blocks[:cut]
        return doc

    def _sweep_residual(self, doc, source_pages):
        """Route the page-one release timestamp into Removed furniture.

        Kentucky's Court of Appeals prints ``RENDERED: ...`` above the
        caption.  It is intentionally outside the headmatter model, but the
        completeness sweep sees it as ordinary source text unless it is
        registered before the sweep runs.
        """
        rendered = []
        for page_no, lines in source_pages:
            if page_no != 1:
                continue
            for line in lines:
                text = line.strip()
                if re.match(r"^RENDERED:\s+.+", text, re.I):
                    rendered.append(text)
        if rendered:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                text for text in dict.fromkeys(rendered) if text not in have
            ]
        super()._sweep_residual(doc, source_pages)

    def _kyctapp_byline(self, text: str):
        """Parse 'NAME, JUDGE[, KIND]:' -> (name, title, kind), or None."""
        t = (text or "").strip()
        if t.upper().startswith("PER CURIAM"):
            return "PER CURIAM", "per curiam", None
        ci = t.find(":")
        if ci == -1:
            return None
        parts = [p.strip() for p in t[:ci].split(",")]
        if len(parts) < 2 or not is_caps_name(parts[0]):
            return None
        if parts[1].lower().replace(".", "") not in _KY_JUDGE_TITLES:
            return None
        kt = " ".join(parts[2:]).upper()
        has_c, has_d = "CONCUR" in kt, "DISSENT" in kt
        kind = (
            "concurring in part and dissenting in part"
            if has_c and has_d
            else "dissenting"
            if has_d
            else "concurring"
            if has_c
            else None
        )
        return parts[0], parts[1].title(), kind

    def parse_author_line(self, text):
        r = self._kyctapp_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._kyctapp_byline(text) is not None:
            ci = text.find(":")
            return text[: ci + 1], text[ci + 1 :].strip()
        return super()._byline_split(line)
