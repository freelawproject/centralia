"""United States Court of Appeals for the First Circuit."""

from __future__ import annotations
from typing import Optional

from ._circuit import FederalCircuitBase


class FirstCircuit(FederalCircuitBase):
    court_id = "ca1"
    court_label = "United States Court of Appeals for the First Circuit."
    circuit_phrase = "first circuit"
    page2_header_cutoff = 30.0  # no centered running header; body at top~72
    margin_top = 0.0  # banner starts at top~26; no margin content on any page
    # CA1 footers are a centered '- N -' page number. Drop them from the body
    # and fold the cross-page paragraph back together with a <pagenumber>
    # marker — otherwise the footer is kept inline ('- 5 - <pagenumber.../>
    # disciplinary action…') or left as a stray '- 13 -' body block.
    fold_page_numbers = True

    def _drop_pageno_lines(self, lines):
        """Drop any line that is just a '- N -' page footer. CA1 prints the
        footer at the very bottom of the page, where it can be clustered into a
        blockquote that spans the page break, or fall inside the footnote zone —
        in both places it would otherwise be joined inline ('…obtained . . .. -
        8 -' / '…a federally - 4 -'). Filtering whole page-number LINES (not the
        joined text) leaves a hyphenated URL fragment like 'sept-29- 2021'
        untouched, since that is never a standalone footer line."""
        return [
            l
            for l in lines
            if not self._is_page_number_text(self.line_plain_text(l))
        ]

    def split_blockquote_paragraphs(self, seg):
        return super().split_blockquote_paragraphs(self._drop_pageno_lines(seg))

    def split_body_paragraphs(self, seg):
        return super().split_body_paragraphs(self._drop_pageno_lines(seg))

    def build_footnotes(self, pages, footnote_lines_by_page, seen_labels=None):
        cleaned = {
            pno: self._drop_pageno_lines(lines)
            for pno, lines in footnote_lines_by_page.items()
        }
        return super().build_footnotes(pages, cleaned, seen_labels=seen_labels)

    def find_footnote_separator(self, page) -> Optional[float]:
        """CA1 draws its footnote separator as a 2-inch (≈144pt) hairline at
        the left margin (x0≈72, x1≈216). The page-1 caption also carries
        left-margin hairlines — counsel-name underlines — but those are a hair
        narrower (≈142pt) or variable; the centered caption dividers are 144pt
        but sit at x0≈234. The generic ">=100pt, left-margin" rule mistakes a
        counsel underline for a footnote separator and sweeps the counsel-block
        tail + decision date into a phantom footnote (and ends the headmatter
        early). Match CA1's separator by its exact ≈144pt width instead, so a
        real page-1 footnote rule (e.g. buckley's '*' note) still registers
        while a counsel underline does not."""
        cutoff = page.height * 0.55
        text_lines = page.extract_text_lines()

        def is_underline(r):
            # A counsel-name underline sits at the baseline of the text it
            # underlines (same width/margin as the separator); a real footnote
            # separator sits in whitespace with no text line at its level.
            for tl in text_lines:
                if (
                    tl["bottom"] - 3 <= r["top"] <= tl["bottom"] + 3
                    and r["x0"] < tl["x1"]
                    and r["x1"] > tl["x0"]
                ):
                    return True
            return False

        cands = [
            r
            for r in page.rects
            if r["height"] < 2
            and abs(r["x0"] - 72.0) <= 1.5
            and abs((r["x1"] - r["x0"]) - 144.0) <= 1.0
            and r["top"] > cutoff
            and not is_underline(r)
        ]
        if not cands:
            return None
        return min(cands, key=lambda r: r["top"])["top"]

    def _byline_split(self, line):
        """CA1 sets every opinion byline in BOLD, and the byline IS the leading
        bold run of the line — the regular-weight inline body follows it:

            **BARRON, Chief Judge.** This appeal…                  (majority)
            **BARRON, Chief Judge, concurring in part and          (a partial
            dissenting in part.** The majority…                     dissent)

        Detecting by the bold run (font) rather than by a '.'/':' terminator
        (form alone) does two things the base grammar can't: it rejects the
        regular-weight panel roster after 'Before' ('Gelpí, Circuit Judge.',
        which otherwise looks like a byline and cuts the headmatter short), and
        it accepts a concurrence/dissent byline whose kind suffix sits between
        the bench title and the terminator. 'PER CURIAM' / 'BY THE COURT' are
        court-authored and not necessarily bold, so defer those to the base."""
        text = (line.get("text") or "").strip()
        if not text:
            return None
        up = text.upper()
        if up.startswith("PER CURIAM") or up.startswith("BY THE COURT"):
            return super()._byline_split(line)
        chars = line.get("chars") or []
        if not chars:
            return None
        # Leading bold run. Spaces AND punctuation are weight-neutral — CA1
        # sets the comma between name and title in regular weight
        # ('KAYATTA<,> Circuit Judge.'), so only a non-bold *word* char (the
        # first body word, 'This') ends the byline run.
        n, saw_bold = 0, False
        for c in chars:
            t = c.get("text", "")
            if not any(ch.isalnum() for ch in t):  # space / punctuation
                n += 1
                continue
            if "bold" in (c.get("fontname", "") or "").lower():
                saw_bold = True
                n += 1
            else:
                break
        if not saw_bold:
            return None
        byline = "".join(c.get("text", "") for c in chars[:n]).strip()
        body = "".join(c.get("text", "") for c in chars[n:]).strip()
        # The bold run must have byline FORM — a name, then a bench title
        # preceded only by title qualifiers — so a bold section head
        # ('I. BACKGROUND') or disposition word is never taken for an author.
        if not self._has_byline_form(byline):  # inherited from FederalCircuitBase
            return None
        return byline, body
