"""Court of Appeals of Indiana.

The author is announced in the headmatter ('Opinion by Judge May', with
'Judges Mathias and Felix concur.' beneath); the opinion then opens with the
judge's signing byline — a left-aligned 'May, Judge.' (a title-case surname, so
the shared all-caps byline grammar misses it, and the trial judge /
announcement were being taken instead). Body paragraphs are bracket-numbered
('[1]', '[2]'). So the opinion start is located at that signing byline.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

from ._appellate import StateAppellate


class CourtOfAppealsOfIndiana(StateAppellate):
    court_id = "indctapp"
    court_label = "Court of Appeals of Indiana."

    def find_footnote_separator(self, page) -> Optional[float]:
        """A real footnote separator has footnote-sized text directly below it.
        Indiana prints full-width horizontal divider rules in the headmatter
        (between caption / appeal-info / byline); the shared finder mistakes the
        topmost one for the footnote separator and drops the byline + body
        beneath it. Requiring small text below excludes those dividers."""
        chars = page.chars
        if not chars:
            return super().find_footnote_separator(page)
        body_size = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        small = body_size - 1.5
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
            if below and min(below, key=lambda c: c["top"]).get("size", 99) <= small:
                cands.append(r["top"])
        return min(cands) if cands else None

    def _is_signing_byline(self, text: str) -> bool:
        t = text.strip()
        low = t.lower()
        if low.startswith(("the honorable", "opinion by", "before")):
            return False
        if not (t.endswith("Judge.") or t.endswith(", J.")):
            return False
        head = t.rsplit(",", 1)[0]
        return 1 <= len(head.split()) <= 2  # a bare surname, not a sentence

    def find_authors(self, all_segments) -> list:
        for i, (_p, seg, _k) in enumerate(all_segments):
            ln = seg[0]
            if ln.get("x0", 999) < 120 and self._is_signing_byline(
                self.line_plain_text(ln)
            ):
                return [i]
        return super().find_authors(all_segments)
