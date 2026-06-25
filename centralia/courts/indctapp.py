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
    # Body text is anchored at x≈86.4 (not 72); the footnote rule shares that
    # margin, and paragraph starts are flagged by the '[N]' margin markers
    # rather than an indent.
    body_baseline_x0 = 86.0

    def extract(self, pdf_path):
        self._footer_dropped = []
        doc = super().extract(pdf_path)
        extra = list(dict.fromkeys(self._footer_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
        if getattr(self, "_footer_dropped", None) is None:
            self._footer_dropped = []
        kept, markers = [], []
        for ln in lines:
            t = self.line_plain_text(ln).strip()
            # The per-page footer ('Court of Appeals of Indiana | Opinion
            # 25A-CR-2182 | May 20, 2026 Page 1 of 15') sits inside the text
            # margins — furniture, recorded once.
            if ln["top"] > 700 and t.startswith("Court of Appeals of Indiana"):
                self._footer_dropped.append(t)
                continue
            # A hanging '[N]' paragraph marker in the left margin.
            if (
                ln["x1"] < self.body_baseline_x0
                and t.startswith("[")
                and t.endswith("]")
                and t[1:-1].isdigit()
            ):
                markers.append(ln)
                continue
            kept.append(ln)
        # Attach each marker to the body line it labels (nearest top), so
        # '[1]' opens its paragraph instead of floating as its own block.
        for mk in markers:
            best = None
            for ln in kept:
                if ln["x0"] >= self.body_baseline_x0 - 2:
                    d = abs(ln["top"] - mk["top"])
                    if d <= 10 and (best is None or d < abs(best["top"] - mk["top"])):
                        best = ln
            if best is not None:
                # Normalize the marker glyphs to the line's metrics, or the
                # small raised digits read as a footnote reference.
                ref = (best.get("chars") or [{}])[0]
                mchars = []
                for c in mk.get("chars") or []:
                    c = dict(c)
                    c["size"] = ref.get("size", c.get("size"))
                    c["top"] = ref.get("top", c.get("top"))
                    c["bottom"] = ref.get("bottom", c.get("bottom"))
                    mchars.append(c)
                best["chars"] = mchars + list(best.get("chars") or [])
                best["x0"] = min(best["x0"], mk["x0"])
            else:
                kept.append(mk)
        return kept

    def split_body_paragraphs(self, seg) -> list:
        """Indiana paragraphs are flush-left with no indent; the '[N]'
        marker (merged onto the first line) is the paragraph start."""
        if not seg:
            return []
        paras = [[seg[0]]]
        for line in seg[1:]:
            t = self.line_plain_text(line).lstrip()
            if t.startswith("[") and "]" in t[:6] and t[1 : t.find("]")].isdigit():
                paras.append([line])
            elif line["x0"] > self.body_baseline_x0 + self.para_indent_min:
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

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
                if r["top"] < c["top"] < r["top"] + 40 and not c["text"].isspace()
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
