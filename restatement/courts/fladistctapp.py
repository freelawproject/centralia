"""Florida District Court of Appeal.

Intermediate appellate court. The opinion author signs in ALL CAPS — a short
'PER CURIAM.' or a surname + abbreviated title ('PRATT, J.' / 'GANNAM, J.' /
'WOZNIAK, J., concurs in result'). The lower-tribunal judge named in the
'Appeal … from the Circuit Court' block is a mixed-case full name + ', Judge'
('Vincent S. Chiu, Judge.') — NOT an author. The shared appellate parser would
otherwise accept that title-case 'Name, Judge' line as a byline and emit a
spurious opinion, so bylines are gated to all-caps surnames (or PER CURIAM).

A standing notice ('NOT FINAL UNTIL TIME EXPIRES TO FILE MOTION FOR REHEARING /
AND DISPOSITION THEREOF IF TIMELY FILED') is stamped on the opinion; it is
routed to the dropped bucket rather than kept as body.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._statesupreme import _is_byline_name

_NOTICE_CUES = ("not final until time expires", "disposition thereof if timely filed")


def _is_notice(text: str) -> bool:
    low = text.lower()
    return any(cue in low for cue in _NOTICE_CUES)


class FloridaDistrictCourtOfAppeal(StateAppellate):
    court_id = "fladistctapp"
    court_label = "Florida District Court of Appeal."

    # ----------------------------------------------------- byline = all caps
    def _allcaps_author(self, r):
        """Keep a byline only if the author is an all-caps surname or PER
        CURIAM — a mixed-case 'Name, Judge' is the lower-tribunal judge."""
        if r is None:
            return None
        name, title = r[0], r[1]
        if title == "per curiam" or _is_byline_name(name):
            return r
        return None

    def parse_author_line(self, text):
        return self._allcaps_author(super().parse_author_line(text))

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self.parse_author_line(text) is None:
            return None
        return super()._byline_split(line)

    # ------------------------------------------------- 'NOT FINAL' notice
    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        notice = []

        kept_summary = []
        for row in doc.summary:
            if isinstance(row, str) and _is_notice(row):
                notice.append(row.strip())
            else:
                kept_summary.append(row)
        doc.summary = kept_summary

        for op in doc.opinions:
            kept = []
            for b in op.blocks:
                if b.kind in ("p", "heading") and _is_notice(b.text):
                    notice.append(b.text.strip())
                else:
                    kept.append(b)
            op.blocks = kept

        if notice:
            # The notice is a single two-line stamp; collapse repeats.
            doc.dropped = list(doc.dropped) + sorted(set(notice))
        return doc
