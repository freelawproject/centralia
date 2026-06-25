"""Shared body handling for the Illinois courts (ill / illappct).

Both number their opinion paragraphs with a hanging pilcrow ('¶ 1', '¶ 2' ...).
The marker sits in its own left column (x0≈62.6 at the Supreme Court, flush at
the body margin at the Appellate Court), while the body text and block quotes are
indented further right — and a '¶' inside a citation ('see ¶ 12') lives in that
indented text, never in the marker column. So paragraphs are split on a pilcrow
**at the marker column**, not on every '¶'.

Each page also repeats a running header (the bare docket, 'No. 1-24-2339') and a
'- N -' page-number footer; those fragment the body and are dropped as furniture.
"""

from __future__ import annotations

import re

_DOCKET_HDR = re.compile(r"^No\.\s*[\dA-Za-z\-]+$")
_PAGENO_FOOT = re.compile(r"^-?\s*\d+\s*-?(\s+No\.\s*[\dA-Za-z\-]+)?$")


class IllinoisStyle:
    fold_page_numbers = True

    # Where wrapped body text sits. The marker hangs left of this (ill: marker
    # 62.6 / text 108) or flush with it (illappct: both 72); either way a page's
    # first line at this x0 is a continuation of the prior paragraph, while a
    # line beginning with a '¶ N' marker is a new paragraph (see the overrides
    # of the two base wrap hooks below). None falls back to ``body_baseline_x0``.
    il_body_baseline = None

    def extract(self, pdf_path):
        self._il_dropped = []
        doc = super().extract(pdf_path)
        if self._il_dropped:
            seen, uniq = set(), []
            for t in self._il_dropped:
                if t not in seen:
                    seen.add(t)
                    uniq.append(t)
            doc.dropped = list(doc.dropped) + uniq
        return doc

    # ----------------------------------------------------- running furniture
    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number <= 1:
            return lines
        H = page.height
        kept = []
        for ln in lines:
            t = self.line_plain_text(ln).strip()
            top = ln.get("top", 0)
            if top < 66 and _DOCKET_HDR.match(t):            # repeated docket header
                self._il_dropped.append(t)
                continue
            if top > H * 0.82 and _PAGENO_FOOT.match(t):      # '- N -' page footer
                self._il_dropped.append(t)
                continue
            kept.append(ln)
        return kept

    # ------------------------------------------------- pilcrow paragraphs
    def _il_marker_col(self, seg):
        xs = [ln["x0"] for ln in seg
              if self.line_plain_text(ln).lstrip()[:1] == "¶"]
        return min(xs) if xs else None

    def _il_is_marker(self, line, col) -> bool:
        t = self.line_plain_text(line).lstrip()
        if t[:1] != "¶":
            return False
        if col is not None and abs(line.get("x0", 0) - col) > 3:
            return False  # a '¶' out in the indented body text = a citation
        return t[1:].lstrip()[:1].isdigit()  # '¶ 12' — a paragraph number

    # ------------------------------------------- page-break continuation merge
    def _wrap_continuation_max(self) -> float:
        base = self.il_body_baseline
        if base is None:
            base = self.body_baseline_x0
        return base + 6

    def _begins_paragraph_block(self, lines) -> bool:
        # A '¶ N' marker line opens a new paragraph and must not be folded into
        # the previous one even though it lands at the top of a fresh page.
        if not lines:
            return False
        t = self.line_plain_text(lines[0]).lstrip()
        return t[:1] == "¶" and t[1:].lstrip()[:1].isdigit()

    def _il_split_paras(self, seg):
        if not seg:
            return []
        col = self._il_marker_col(seg)
        paras = [[seg[0]]]
        for ln in seg[1:]:
            if self._il_is_marker(ln, col):
                paras.append([ln])
            else:
                paras[-1].append(ln)
        return paras

    def split_body_paragraphs(self, seg):
        return self._il_split_paras(seg)

    def split_blockquote_paragraphs(self, seg):
        return self._il_split_paras(seg)
