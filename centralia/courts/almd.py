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
        if i > 0 and i < len(t) and t[i] == ".":
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
