"""Shared layout for the Kansas appellate courts (kan / kanctapp).

Both print the same front matter, pivoting on a centered, all-caps title that
follows the case caption (whose final party-status line — 'Appellant,' /
'Appellees.' / 'Respondent.' — is set in italics). Everything before that title
is headmatter (the court banner, docket, and caption).

Two shapes:

  * an authored ruling — the title is 'SYLLABUS BY THE COURT', and the official
    syllabus (body-size) runs beneath it; the opinion itself opens later at an
    indented (x0≈108) byline, 'STEGALL, J.: ...' / 'ROSEN, C.J.: ...' /
    'PER CURIAM: ...', the line after 'The opinion of the court was delivered
    by'. The abbreviated-title base recognizes that byline; this mixin lifts the
    syllabus block out of the headmatter into the ``syllabus`` field (it stops
    where the type drops to the smaller procedural-history / counsel block).

  * an order — there is no byline, so the body opens at that centered, all-caps
    title ('ORDER' / 'ORIGINAL PROCEEDING IN DISCIPLINE'), which is kept as the
    first line of the order, authored PER CURIAM (doc_type = order).

All of this is structural — alignment, all-caps, italics, font size — with no
matching of the title text itself.
"""

from __future__ import annotations

from ..models import DocType


class KansasStyle:
    def _kan_page_width(self) -> float:
        return getattr(self, "_page1_width", 612.0) or 612.0

    def _kan_centered(self, line) -> bool:
        pw = self._kan_page_width()
        x0, x1 = line["x0"], line["x1"]
        cx = (x0 + x1) / 2
        return x0 > 100 and abs(cx - pw / 2) < 30 and (x1 - x0) < pw * 0.6

    @staticmethod
    def _kan_allcaps(text: str) -> bool:
        t = text.strip()
        return bool(t) and t == t.upper() and any(c.isalpha() for c in t)

    def _kan_caption_end(self, lines: list) -> int:
        """Index of the last italic, centered caption line (the party-status
        line that closes the case caption), or -1."""
        last = -1
        for i, ln in enumerate(lines):
            _s, font, _b = self.line_meta(ln)
            if "Italic" in font and self._kan_centered(ln):
                last = i
        return last

    def _kan_title_index(self, lines: list):
        """Index of the centered, all-caps title that follows the case caption
        (the first such line after the last italic caption line), or None. The
        court banner is excluded because it precedes the caption."""
        cap = self._kan_caption_end(lines)
        if cap < 0:
            return None
        for i in range(cap + 1, len(lines)):
            if self._kan_centered(lines[i]) and self._kan_allcaps(
                self.line_plain_text(lines[i]).strip()
            ):
                return i
        return None

    def _kan_syllabus_index(self, lines: list):
        """Index of the centered 'SYLLABUS BY THE COURT' heading, or None."""
        cap = self._kan_caption_end(lines)
        for i in range(cap + 1, len(lines)):
            t = self.line_plain_text(lines[i]).strip()
            if self._kan_centered(lines[i]) and t.upper().startswith("SYLLABUS"):
                return i
        return None

    # ------------------------------------------------------------- orders
    def extract(self, pdf_path):
        self._kan_order = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._kan_order = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # No byline -> order: the body opens at the centered all-caps title. The
        # italic caption line and the title may sit mid-segment, so scan every
        # line (tracking its segment) rather than only each segment's first line.
        flat, owner = [], []
        for si, (_p, seg, _k) in enumerate(all_segments):
            for ln in seg:
                if (ln.get("text") or "").strip():
                    flat.append(ln)
                    owner.append(si)
        idx = self._kan_title_index(flat)
        if idx is not None:
            self._kan_order = owner[idx]
            return [owner[idx]]
        return []

    def split_author_line(self, line):
        if getattr(self, "_kan_order", None) is not None:
            return "", [line]  # the centered title opens the order body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_kan_order", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op

    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        if getattr(self, "_kan_order", None) is not None:
            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # --------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        lines = [
            ln
            for seg in headmatter_segs
            for ln in seg
            if (ln.get("text") or "").strip()
        ]
        syl_hdr = self._kan_syllabus_index(lines)
        hm, syllabus = lines, []
        if syl_hdr is not None:
            # Syllabus = the centered title + the body-size lines beneath it,
            # stopping where the type drops to the smaller procedural / counsel
            # block. The rest stays headmatter.
            base = self.line_meta(lines[syl_hdr])[0]
            end = syl_hdr + 1
            while end < len(lines) and self.line_meta(lines[end])[0] >= base - 1.0:
                end += 1
            syllabus = [self.line_plain_text(ln).strip() for ln in lines[syl_hdr:end]]
            hm = lines[:syl_hdr] + lines[end:]

        # Style-preserving headmatter (the 'Florida' look): the centered caption
        # renders centered via CSS, not crude leading whitespace, and italics are
        # kept. Far cleaner than the raw monospace block for these centered
        # captions.
        styled = self._styled_headmatter([hm], page1_rules)
        styled["syllabus"] = [s for s in syllabus if s]
        return styled
