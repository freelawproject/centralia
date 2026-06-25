"""Court of Appeals of Virginia.

The author is announced near the foot of the caption, after the panel ('Present:
Judges ...'), the appeal-from line, the trial judge, and the counsel block:

    [PUBLISHED|UNPUBLISHED] OPINION BY
    JUDGE RANDOLPH A. BEALES

then the opinion body. So the byline is the bold '[CHIEF/SENIOR ]JUDGE <ALL-CAPS
NAME>' announcement line; the opinion starts at the segment after it, and the
whole caption stays in the headmatter. The ALL-CAPS 'JUDGE NAME' distinguishes
the author from the 'Present: Judges ...' panel and the 'NAME, Judge' trial-court
line (both mixed-case). A separate writing is signed in-body ('JUDGE X, with whom
JUDGE Y joins, dissenting.'); a per-curiam order with no announcement falls back
to the default search.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._statesupreme import _is_byline_name

# Longest-first so a compound title wins over the bare 'JUDGE'.
_VAC_TITLES = ("ASSOCIATE JUDGE", "SENIOR JUDGE", "CHIEF JUDGE", "JUDGE")


class CourtOfAppealsOfVirginia(StateAppellate):
    court_id = "vactapp"
    court_label = "Court of Appeals of Virginia."

    def extract(self, pdf_path):
        self._vac_meta = {}
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._vac_meta = {}
        # The announced author: a bold '[CHIEF/SENIOR ]JUDGE <NAME>' line.
        auth_seg, author = None, None
        for i, (_p, seg, _k) in enumerate(all_segments):
            for ln in seg:
                a = self._vac_title_name(self.line_plain_text(ln).strip())
                if a:
                    auth_seg, author = i, a
                    break
            if author:
                break
        if author is None or auth_seg + 1 >= len(all_segments):
            return super().find_authors(all_segments)
        body = auth_seg + 1
        starts = [body]
        self._vac_meta[body] = (author, "majority")
        for i in range(body, len(all_segments)):
            if i in self._vac_meta:
                continue
            sep = self._vac_separate(all_segments[i][1])
            if sep:
                starts.append(i)
                self._vac_meta[i] = sep
        return sorted(starts)

    @staticmethod
    def _vac_title_name(text):
        for title in _VAC_TITLES:
            if text.startswith(title + " "):
                name = text[len(title) + 1 :].split(",")[0].strip()
                if _is_byline_name(name):
                    return f"{title} {name}"
        return None

    def _vac_separate(self, seg):
        author = self._vac_title_name(self.line_plain_text(seg[0]).strip())
        if not author:
            return None
        blob = " ".join(self.line_plain_text(l) for l in seg[:3]).lower()
        if "dissent" in blob and "concur" in blob:
            return author, "concurring in part and dissenting in part"
        if "dissent" in blob:
            return author, "dissent"
        if "concur" in blob:
            return author, "concurrence"
        return None

    def split_author_line(self, line):
        if getattr(self, "_vac_meta", None):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        meta = getattr(self, "_vac_meta", {}).get(op_start)
        if meta:
            op.author, op.type = meta
        return op
