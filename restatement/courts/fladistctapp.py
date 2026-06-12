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
_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)


def _is_notice(text: str) -> bool:
    low = text.lower()
    return any(cue in low for cue in _NOTICE_CUES)


def _is_centered_date(text: str) -> bool:
    """'May 22, 2026' — a month name, a day, and a 4-digit year."""
    t = text.strip().rstrip(".")
    parts = t.replace(",", " ").split()
    return (
        len(parts) == 3
        and parts[0] in _MONTHS
        and parts[1].isdigit()
        and len(parts[2]) == 4
        and parts[2].isdigit()
    )


class FloridaDistrictCourtOfAppeal(StateAppellate):
    def find_authors(self, all_segments) -> list:
        # The decision DATE is centered on its own line and is the last
        # headmatter element — every Florida DCA disposition (signed
        # opinion or per curiam order) begins right after it. Use it as the
        # headmatter boundary; a real byline (PER CURIAM / NAME, J.) always
        # sits below the date, so when the base finds one there, trust it
        # (it also catches later concurrences/dissents).
        date_i = self._centered_date_index(all_segments)
        base = super().find_authors(all_segments)
        if date_i is None:
            return base
        if base and base[0] > date_i:
            return base
        return [date_i + 1] if date_i + 1 < len(all_segments) else base

    def _centered_date_index(self, all_segments):
        last = None
        for i, (pno, seg, _k) in enumerate(all_segments):
            if pno != 1 or not seg:
                continue
            line = seg[0]
            t = self.line_plain_text(line).strip()
            if _is_centered_date(t) and self.line_alignment(line, 612) == "C":
                last = i
        return last

    def split_author_line(self, line):
        if self._byline_split(line) is None and self.parse_author_line(
            self.line_plain_text(line).strip()
        ) is None:
            return "", [line]
        return super().split_author_line(line)

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
