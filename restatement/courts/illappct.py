"""Illinois Appellate Court.

The author is announced ('JUSTICE LAMPKIN delivered the judgment of the court
...', with 'Justices Rochford and Reyes concurred ...' beneath). The opinion
proper opens at the bold 'OPINION' divider, after which the body is
paragraph-numbered ('¶ 1', '¶ 2'). So the author is read off the announcement
and the opinion starts at '¶ 1' (the announcement / panel block stays in the
headmatter).
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

from ._illinois import IllinoisStyle
from ._reversedjustice import ReversedJusticeSupreme


class IllinoisAppellateCourt(IllinoisStyle, ReversedJusticeSupreme):
    court_id = "illappct"
    court_label = "Illinois Appellate Court."

    def find_footnote_separator(self, page) -> Optional[float]:
        """A footnote separator has footnote-sized text directly below it. The
        two-column caption is closed by full-width divider rules; the shared
        finder mistakes the top one for the footnote separator and drops the
        announcement byline + ¶1 body beneath it. (Recurring base bug — see
        arkctapp / indctapp; a general fix belongs in StateSupreme but needs a
        verified sweep across all 43 state courts.)"""
        chars = page.chars
        if not chars:
            return super().find_footnote_separator(page)
        body_size = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        h, cands = page.height, []
        for r in page.rects:
            if not (
                r["height"] < 2.5 and (r["x1"] - r["x0"]) >= 80 and r["top"] > h * 0.4
            ):
                continue
            below = [
                c
                for c in chars
                if r["top"] < c["top"] < r["top"] + 22 and not c["text"].isspace()
            ]
            if (
                below
                and min(below, key=lambda c: c["top"]).get("size", 99)
                <= body_size - 1.0
            ):
                cands.append(r["top"])
        return min(cands) if cands else None

    def find_authors(self, all_segments) -> list:
        # Author announced via the reversed-title verb byline ('JUSTICE LAMPKIN
        # delivered ...'); read it off wherever it sits.
        self._ill_author = None
        for _p, seg, _k in all_segments:
            for ln in seg:
                r = self._rev_parse(self.line_plain_text(ln).strip())
                if r:
                    name, title, _kind = r
                    self._ill_author = f"{title} {name}".strip()
                    break
            if self._ill_author:
                break
        # The opinion body opens at the first numbered paragraph.
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip()
            if t.startswith("¶ 1") or t.startswith("¶1"):
                return [i]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        if self.line_plain_text(line).strip().startswith("¶"):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if self._ill_author:
            op.author = self._ill_author
        return op
