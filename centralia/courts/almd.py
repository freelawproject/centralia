"""United States District Court, Middle District of Alabama.

Shares the Alabama-district caption style (parties | case numbers separated by a
stacked ')' divider column), rendered as a whitespace-preserved facsimile by the
shared base. Opinion opens at the centered, bold document title ('MEMORANDUM
OPINION AND ORDER' / 'ORDER'); signature-block author; blue bates stamp in the
top margin excluded.
"""

from __future__ import annotations

from ._aldistrict import AlabamaDistrictBase


class MiddleDistrictOfAlabama(AlabamaDistrictBase):
    court_id = "almd"
    court_label = "United States District Court, Middle District of Alabama."

    def _split_segments_at_bylines(self, all_segments):
        """Isolate a full-width title glued to the caption's last row.

        Some ALMD Word templates keep the caption rail and the centered
        ``AMENDED OPINION ...`` title in one gap-classified segment.  The title
        is the ruling boundary, not another caption cell.
        """
        out = []
        for page_no, seg, kind in super()._split_segments_at_bylines(all_segments):
            cuts = []
            for index, line in enumerate(seg[1:], 1):
                text = self.line_plain_text(line).strip()
                upper = text.upper()
                if (
                    text == upper
                    and len(text) < 100
                    and (
                        upper.startswith("AMENDED OPINION")
                        or upper.startswith("AMENDED ORDER")
                    )
                ):
                    cuts.append(index)
            if not cuts:
                out.append((page_no, seg, kind))
                continue
            for start, end in zip([0] + cuts, cuts + [len(seg)]):
                part = seg[start:end]
                if part:
                    out.append((page_no, part, self.classify_segment(part)))
        return out

    def _is_heading(self, line) -> bool:
        text = self.line_plain_text(line).strip()
        upper = text.upper()
        if text == upper and upper.startswith(("AMENDED OPINION", "AMENDED ORDER")):
            return True
        return super()._is_heading(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if (
            len(op.blocks) >= 2
            and op.blocks[0].page == op.blocks[1].page
            and self._untag(op.blocks[0].text).upper().startswith(
                ("AMENDED OPINION", "AMENDED ORDER")
            )
            and op.blocks[1].kind == "p"
        ):
            op.blocks[0].text = f"{op.blocks[0].text} {op.blocks[1].text}".strip()
            op.blocks[0].kind = "heading"
            del op.blocks[1]
        return op

    def correct_page_geometry(self, page) -> None:
        """This judge sets opinions entirely in Courier New Bold. Two quirks:
        a wide-space glyph extracts as the literal '(cid:1)' (map it to a
        space), and because the body is UNIFORMLY bold the weight carries no
        emphasis — strip it from the font names so the output isn't one solid
        block of <strong> (italic runs are kept)."""
        super().correct_page_geometry(page)
        chars = page.chars
        for c in chars:
            if c.get("text") == "(cid:1)":
                c["text"] = " "
        # Strip the weight ONLY when the page is set PREDOMINANTLY in bold
        # (this judge's Courier-Bold opinions) — on ordinary almd filings bold
        # is real emphasis and must be preserved.
        bold = sum(1 for c in chars if "Bold" in (c.get("fontname") or ""))
        if chars and bold / len(chars) > 0.8:
            for c in chars:
                fn = c.get("fontname") or ""
                if "Bold" in fn:
                    c["fontname"] = fn.replace("Bold", "")

    def find_footnote_separator(self, page):
        """Footnotes are set at BODY size (14pt Courier, same as the text) below
        the fixed 2-inch (~144pt) rule at the left margin — the 'smaller text
        below' test fails, so match the rule by width/position directly."""
        cutoff = page.height * 0.5
        cands = [
            r["top"]
            for r in page.rects
            if r["height"] < 3
            and 100 <= (r["x1"] - r["x0"]) <= 200
            and r["x0"] < page.width * 0.25
            and r["top"] > cutoff
        ]
        if cands:
            return min(cands)
        return super().find_footnote_separator(page)

    def detect_footnote_label(self, line):
        """Foot-marks are body-size '*'/'**' or 'N.' (a numbered footnote),
        not raised superscripts, so the base 'smaller char' test misses them."""
        t = (line.get("text") or "").lstrip()
        if t.startswith("*"):
            return t[: len(t) - len(t.lstrip("*"))]
        i = 0
        while i < len(t) and t[i].isdigit():
            i += 1
        # A continuation can begin with a citation such as ``10.) Young's``.
        # That is prose from the current note, not a new note numbered 10.
        if (
            0 < i <= 3
            and i < len(t)
            and t[i] == "."
            and (i + 1 == len(t) or t[i + 1] != ")")
        ):
            return t[:i]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the leading body-size marker ('*' / 'N.') off the footnote
        text — it is the label, not prose."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label != "?":
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            for pre in (label + ".", label):
                if stripped.startswith(pre):
                    fn.paragraphs[0] = (tag, stripped[len(pre) :].lstrip())
                    break
        return fn
