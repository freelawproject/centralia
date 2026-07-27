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

    # ------------------------------------------- case-information end page
    def extract(self, pdf_path):
        self._ill_endmatter = []
        doc = super().extract(pdf_path)
        if self._ill_endmatter:
            doc.trailer = list(doc.trailer) + self._ill_endmatter
        return doc

    def _case_info_table(self, page):
        """Every Illinois Official Reports opinion closes with a
        case-information page — a drawn two-column table (label column left,
        content right) carrying the case title + citation, 'Decision Under
        Review', and counsel for each side. Left in place it reads as more
        opinion body, so it is lifted into the document's ending matter.

        Detected from the drawing, never the wording: each row rule is laid
        down as TWO segments meeting at a shared column seam, so several rules
        sharing one seam x is the table's signature. Returns (seam_x, rule
        tops) or None."""
        bands: dict = {}
        for r in page.rects:
            if r["height"] < 2.5 and (r["x1"] - r["x0"]) > 40:
                bands.setdefault(round(r["top"], 1), []).append(r)
        seams: dict = {}
        for top, rs in bands.items():
            rs.sort(key=lambda r: r["x0"])
            for a, b in zip(rs, rs[1:]):
                if 0 <= b["x0"] - a["x1"] < 4:  # two segments, one seam
                    seams.setdefault(round((a["x1"] + b["x0"]) / 2), set()).add(top)
        if not seams:
            return None
        seam_x, tops = max(seams.items(), key=lambda kv: len(kv[1]))
        # A single seam could be any two abutting rules; a table has several.
        if len(tops) < 2:
            return None
        return seam_x, sorted(bands)

    @staticmethod
    def _seam_split(line, seam_x):
        """Split one source line into (label, content) at the column seam.

        A row whose text runs straight through the seam (the case title) is one
        cell, not two — splitting it would scramble its reading order — so it is
        returned whole. Spaces are real chars here (``keep_blank_chars``), so
        the gutter is measured between non-blank glyphs."""
        chars = list(line.get("chars", ()))
        glyphs = [c for c in chars if not c["text"].isspace()]
        if not glyphs:
            return "", ""

        def join(cs):
            return " ".join(
                "".join(c["text"] for c in sorted(cs, key=lambda c: c["x0"])).split()
            )

        # Sides are measured on the ink, but rebuilt from every char so the
        # real space glyphs survive and words keep their breaks.
        ink_l = [c for c in glyphs if c["x0"] < seam_x]
        ink_r = [c for c in glyphs if c["x0"] >= seam_x]
        if not ink_l or not ink_r:
            return (join(chars), "") if ink_l else ("", join(chars))
        gutter = min(c["x0"] for c in ink_r) - max(c["x1"] for c in ink_l)
        if gutter < 12:  # continuous text crossing the seam — a spanning row
            return join(chars), ""
        return (
            join([c for c in chars if c["x0"] < seam_x]),
            join([c for c in chars if c["x0"] >= seam_x]),
        )

    def _fold_case_info(self, rows, seam_x, rule_tops) -> list:
        """One entry per table row, with each column's wrapped lines rejoined:
        the label column stacks 'Attorneys' / 'for' / 'Appellant:' down three
        baselines that pdfplumber merges into the counsel names beside them, so
        the two columns are gathered separately and then set side by side."""
        out = []
        for lo, hi in zip(rule_tops, rule_tops[1:] + [float("inf")]):
            band = sorted(
                (ln for ln in rows if lo <= ln.get("top", 0) < hi),
                key=lambda ln: ln.get("top", 0),
            )
            label, content = [], []
            for ln in band:
                l, r = self._seam_split(ln, seam_x)
                if l:
                    label.append(l)
                if r:
                    content.append(r)
            row = " ".join(label + content).strip()
            if row:
                out.append(row)
        return out

    def page_lines(self, page) -> list:
        lines = super().page_lines(page)
        table = self._case_info_table(page)
        if not table:
            return lines
        seam_x, rule_tops = table
        top0 = rule_tops[0]
        body = [ln for ln in lines if ln.get("top", 0) < top0]
        rows = [ln for ln in lines if ln.get("top", 0) >= top0]
        if not rows:
            return lines
        self._ill_endmatter = self._fold_case_info(rows, seam_x, rule_tops)
        return body

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Fold the ')'-railed caption (The Banded Bracket) into a two-column
        block: parties left of the rail, court-below / docket / trial judge
        right — like idahoctapp/delch/wash. Without this the rail stays inline
        in the text ('PARTY ) Appeal from the') and the two columns lose their
        alignment, with the rail-only rows orphaned as lone ')' lines."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d

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
