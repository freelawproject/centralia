"""Supreme Court of New Jersey.

Byline leads with the title: 'JUSTICE NORIEGA delivered the opinion of the
Court.' / 'JUSTICE FASCIALE, dissenting.'. Each opinion is preceded by a
syllabus headed 'JUSTICE X, writing for a unanimous Court.' — that heading is
not an opinion verb phrase, so the reversed-justice base treats it as headmatter
and only the 'delivered'/kind byline starts the opinion.

Merits opinions open with a multi-page **clerk's syllabus** (a 'SYLLABUS' title
page: the not-part-of-the-opinion disclaimer, the case caption, the summary
narrative, 'HELD:', numbered holdings, and the panel joinder) and only then the
formal opinion caption ('SUPREME COURT OF NEW JERSEY' + parties + counsel) that
precedes the byline. The base would fold that whole syllabus into the headmatter
line-by-line. Instead ``extract_headmatter`` carves the syllabus off the front
into the ``syllabus`` field — grouped into flowing paragraphs — and leaves the
formal caption as the real headmatter. Not every NJ filing carries a syllabus
(orders, per-curiam denials); the carve fires only when the document opens with
a 'SYLLABUS' page.
"""

from __future__ import annotations

import re

from ._reversedjustice import ReversedJusticeSupreme

# The formal opinion caption that follows the syllabus and opens the headmatter.
_CAPTION_START = "supreme court of new jersey"


class NewJerseySupreme(ReversedJusticeSupreme):
    court_id = "nj"
    court_label = "Supreme Court of New Jersey."
    # The page number sits centered at the bottom of each page, so it drops into
    # the body as its own line — recognize it as furniture (drop it, and fold a
    # paragraph that a page break split back together with a <pagenumber> mark).
    fold_page_numbers = True

    @staticmethod
    def _repair_split_letter_hyphens(text: str) -> str:
        """Repair an NJ embedded-font artifact: ``-Po-s-t`` / ``-Id-``.

        These are not source hyphenations; the same PDF exposes the normal
        words through its plain text layer. Require at least two hyphens so
        ordinary compounds such as ``work-around`` remain untouched.
        """
        def join(match):
            token = match.group(0)
            return token.replace("-", "") if token.count("-") >= 2 else token

        return re.sub(
            r"(?<![A-Za-z])-?[A-Za-z]+(?:-[A-Za-z]+)+-?(?![A-Za-z])",
            join,
            text,
        )

    def line_inline_text(self, line) -> str:
        return self._repair_split_letter_hyphens(super().line_inline_text(line))

    def line_plain_text(self, line) -> str:
        return self._repair_split_letter_hyphens(super().line_plain_text(line))

    _ROMAN_OUTLINE = {
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
    }

    def _is_outline_label(self, line) -> bool:
        """A centered standalone hierarchy label: ``II.``, ``A.``, ``1.``."""
        text = (line.get("text") or "").strip()
        if not text.endswith(".") or " " in text:
            return False
        core = text[:-1]
        label = (
            core in self._ROMAN_OUTLINE
            or (len(core) == 1 and core.isalpha() and core.isupper())
            or (core.isdigit() and len(core) <= 2)
        )
        if not label:
            return False
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        center = (line["x0"] + line["x1"]) / 2
        return abs(center - pw / 2) <= 20 and line["x1"] - line["x0"] <= 40

    def split_body_paragraphs(self, seg) -> list:
        # NJ stacks outline levels on separate centered rows with ordinary
        # body leading. The generic splitter otherwise folds the whole stack
        # and following prose into one paragraph ("II. A. 1."). Split those
        # structural rows before applying normal indentation logic.
        out = []
        current = []
        for line in seg:
            if self._is_outline_label(line):
                if current:
                    out.extend(super().split_body_paragraphs(current))
                    current = []
                out.append([line])
            else:
                current.append(line)
        if current:
            out.extend(super().split_body_paragraphs(current))
        return out

    def classify_paragraph(self, lines) -> str:
        if len(lines) == 1 and self._is_outline_label(lines[0]):
            return "heading"
        return super().classify_paragraph(lines)

    def find_footnote_separator(self, page):
        """NJ draws a FULL-WIDTH rule between the counsel block and the opinion
        byline. The width-based finder mistakes that divider for a footnote
        separator and shunts the byline — and with it the whole opinion — below
        the 'footnote' line, so no opinion is found. NJ's real separator is a
        short 2-inch rule with footnote-SIZE text beneath it, so discriminate by
        the size of the text below the rule (the repo's robust discriminator),
        not its width: the byline under the divider is body-size and rejected."""
        return self._footnote_sep_small_text_below(page)

    @staticmethod
    def _line_page(line) -> int:
        chars = line.get("chars") or []
        return (
            chars[0].get("page_number") if chars else line.get("page_number")
        ) or 1

    def find_authors(self, all_segments) -> list:
        """On a syllabus opinion the clerk's syllabus is itself headed by an
        author line — 'JUSTICE X, writing for a unanimous Court.' (rejected by
        the reversed-justice parser) or a bare 'PER CURIAM' (indistinguishable
        from the real byline by text alone). Both sit on the syllabus page,
        ahead of the formal 'SUPREME COURT OF NEW JERSEY' caption; the true
        byline always follows it. So drop any candidate before that caption."""
        authors = super().find_authors(all_segments)
        self._nj_order_start = None
        first = ""
        for _pno, seg, _kind in all_segments:
            if seg and self.line_plain_text(seg[0]).strip():
                first = self.line_plain_text(seg[0]).strip().upper()
                break
        if first != "SYLLABUS":
            if authors:
                return authors
            # Appellate Division motion orders have no justice byline. Their
            # ruling begins with a standalone ``ORDER`` after the caption;
            # without this fallback the ruling is all classified as headmatter.
            for i, (_pno, seg, _kind) in enumerate(all_segments):
                if (
                    seg
                    and "".join(self.line_plain_text(seg[0]).split()).upper()
                    == "ORDER"
                    and i > 0
                ):
                    self._nj_order_start = i
                    return [i]
            return authors
        cap_idx = next(
            (
                i
                for i, (_p, seg, _k) in enumerate(all_segments)
                if seg
                and self.line_plain_text(seg[0])
                .strip()
                .upper()
                .rstrip(".")
                .startswith(_CAPTION_START.upper())
            ),
            None,
        )
        if cap_idx is None:
            return authors
        gated = [i for i in authors if i >= cap_idx]
        return gated or authors

    def split_author_line(self, line):
        if getattr(self, "_nj_order_start", None) is not None:
            return "PER CURIAM", [line]
        return super().split_author_line(line)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        lines = [
            line
            for seg in headmatter_segs
            for line in seg
            if (line.get("text") or "").strip()
        ]
        first = (lines[0].get("text") or "").strip().upper() if lines else ""
        if first != "SYLLABUS":
            return super().extract_headmatter(headmatter_segs, page1_rules)
        # The syllabus and the opinion's formal caption sit on different pages.
        # Headmatter begins on the FIRST page that carries the caption banner
        # ('SUPREME COURT OF NEW JERSEY'); every earlier page is the syllabus.
        # Splitting by page (not by the caption line) keeps the whole caption
        # page in the headmatter and the whole syllabus tail in the syllabus.
        cap_page = next(
            (
                self._line_page(line)
                for line in lines
                if (line.get("text") or "")
                .strip()
                .upper()
                .rstrip(".")
                .startswith(_CAPTION_START.upper())
            ),
            None,
        )
        if cap_page is None:  # no formal caption found — leave headmatter intact
            return super().extract_headmatter(headmatter_segs, page1_rules)
        boundary = next(
            i for i, line in enumerate(lines) if self._line_page(line) >= cap_page
        )
        syl_lines = lines[:boundary]
        cap_lines = lines[boundary:]
        # The formal caption sits on a later page, so the page-1 (syllabus-page)
        # drawn rules are not its dividers — drop them from the caption build.
        hm = super().extract_headmatter([cap_lines], None)
        hm["syllabus"] = self._group_syllabus(syl_lines)
        return hm

    def _group_syllabus(self, syl_lines) -> list:
        """Reflow the clerk's syllabus lines into paragraphs. A paragraph starts
        at a first-line indent (x0 shifted right of the body margin) or after a
        blank-line gap; lines that return to the body margin, and continuations
        across a page break, fold into the running paragraph. Page numbers and
        the mis-read page-1 dividers are furniture and are dropped. A centered
        single-line row (the 'SYLLABUS' banner, the case caption) keeps its
        centered styling; everything else renders as flowing prose."""
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        rows: list = []
        cur: list = []  # (html, align) for the paragraph being built

        def flush():
            if not cur:
                return
            if len(cur) == 1 and cur[0][1] == "C":
                rows.append(
                    {"__hm__": True, "html": cur[0][0], "rel": 1.0, "align": "C"}
                )
            else:
                rows.append(" ".join(h for h, _ in cur))
            rows.append("")
            cur.clear()

        prev_top = prev_page = prev_size = None
        for line in syl_lines:
            t = (line.get("text") or "").strip()
            if t.isdigit() and len(t) <= 4:  # page number
                continue
            size, _fn, _bold = self.line_meta(line)
            x0, top = line["x0"], line["top"]
            page = self._line_page(line)
            indented = x0 > 95  # a first-line indent (~108) vs the body margin (72)
            page_break = prev_page is not None and page != prev_page
            gap = None if prev_top is None or page_break else (top - prev_top)
            new_para = (
                prev_top is None
                or indented
                or (gap is not None and gap > 1.7 * max(prev_size or size, 9))
            )
            if new_para:
                flush()
            cur.append((self.line_inline_text(line), self.line_alignment(line, pw)))
            prev_top, prev_page, prev_size = top, page, size
        flush()
        while rows and rows[-1] == "":
            rows.pop()
        return rows
