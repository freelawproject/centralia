"""United States Court of Appeals for the Second Circuit."""

from __future__ import annotations

from collections import Counter

import pdfplumber

from ..base import BaseExtractor
from ._circuit import FederalCircuitBase


class SecondCircuit(FederalCircuitBase):
    court_id = "ca2"
    court_label = "United States Court of Appeals for the Second Circuit."
    circuit_phrase = "second circuit"
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0

    footnote_font_size = 12
    opinion_font_size_= 13
    # pagenum_font_size = 12 or 13
    foonote_divider_width = 144.0
    footnote_divider_style = "rect"
    # footnote_divider_x0 = 108.0,  86.4
    
    # Full opinion, foonotes size 12, 144 width,  108 x0 page number size 12 font PalatinoLinotype-Roman



    # Summary Order #1 
    #      H   top= 698.1 x0=  72.0 x1= 216.0 bot= 698.8 w= 144.0 h=  0.7 (24% pw, top 88%)
    #   x top= 729.1 x0= 302.8 x1= 309.3 sz=13.0 C   PalatinoLinotype-Roman   | 2
#     top= 707.9 x0=  72.0 x1= 449.7 sz=12.0 L   PalatinoLinotype-Roman   | * The Clerk of Court is directed to amend the caption as set forth above.

    # PalatinoLinotype-Roman or TimesNewRomanPSMT

    # Summary order 2 with page lines alvarenga_vides_v._blanche



    # CA2 documents come in distinct STYLES, and each style dictates its own
    # extraction. Two independent axes:
    #   * summary-order vs opinion — a summary order opens with the convening
    #     recital ('At a stated term of the United States Court of Appeals …')
    #     under a centered 'SUMMARY ORDER' heading and a 'PRESENT: <judges>'
    #     panel; an opinion has a normal '<NAME>, Circuit Judge:' byline.
    #   * numbered paper or not — a left-margin line-number gutter.
    # ``document_style`` reports one of: 'opinion', 'opinion_numbered',
    # 'summary_order', 'summary_order_numbered'.
    def document_style(self, page) -> str:
        text = (page.extract_text() or "").lower()
        is_summary = "at a stated term" in text or (
            "summary order" in text and "rulings by summary order" in text
        )
        base = "summary_order" if is_summary else "opinion"
        numbered = self._linenum_gutter_x(page) is not None
        return base + ("_numbered" if numbered else "")

    def extract(self, pdf_path):
        """Detect the document style up front so the style-specific hooks below
        (per-curiam start for summary orders) can branch on it."""
        self._style = "opinion"
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.pages:
                    self._style = self.document_style(pdf.pages[0])
        except Exception:
            pass
        self._measure_body_template(pdf_path)
        return super().extract(pdf_path)

    def _measure_body_template(self, pdf_path):
        """Measure CA2's varying body rail and double-space leading."""
        x0s = Counter()
        page_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    lines = self.page_lines(page)
                    usable = [
                        line
                        for line in lines
                        if 75 < line.get("top", 0) < page.height - 75
                        and line.get("x0", 0) < page.width * 0.42
                        and line.get("x1", 0) > page.width * 0.55
                    ]
                    x0s.update(round(line["x0"]) for line in usable)
                    page_rows.append(usable)
        except Exception:
            return
        if not x0s:
            return
        baseline = float(x0s.most_common(1)[0][0])
        gaps = Counter()
        for lines in page_rows:
            ordered = sorted(lines, key=lambda line: line["top"])
            for above, below in zip(ordered, ordered[1:]):
                gap = below["top"] - above["top"]
                if (
                    abs(above["x0"] - baseline) <= 4
                    and abs(below["x0"] - baseline) <= 4
                    and 14 <= gap <= 42
                ):
                    gaps[round(gap, 1)] += 1
        self.body_baseline_x0 = baseline
        if gaps:
            leading = gaps.most_common(1)[0][0]
            self.gap_single_max = max(self.gap_tight_max + 1, leading - 7)
            self.gap_double_max = leading + 8

    def prepare_document(self, pdf):
        """Enable the continuation-page header filter only when present.

        Many Second Circuit opinions begin body text around y=76 on pages 2+
        and have no running docket header. The circuit base assumes the
        opposite and drops those lines. A repeated ``No.``/``Case No.`` line
        on continuation pages is the positive signal that the reservation is
        actually needed.
        """
        self._drop_page2_header = False
        self._ca2_notice_furniture = []
        headers = []
        for page in pdf.pages[1:]:
            for line in page.extract_text_lines():
                if line.get("top", 0) >= self.page2_header_cutoff:
                    break
                text = " ".join((line.get("text") or "").split()).lower()
                if text.startswith(("no. ", "case no. ", "docket no. ")):
                    headers.append(text)
                    break
        self._drop_page2_header = len(headers) >= 2 and len(set(headers)) == 1

    def _sweep_residual(self, doc, source_pages):
        if getattr(self, "_ca2_notice_furniture", None):
            doc.dropped = list(doc.dropped) + self._ca2_notice_furniture
        super()._sweep_residual(doc, source_pages)

    def filter_margins(self, obj):
        if (
            obj.get("page_number", 1) > 1
            and obj.get("top", 0) < self.page2_header_cutoff
            and not getattr(self, "_drop_page2_header", False)
        ):
            return BaseExtractor.filter_margins(self, obj)
        return super().filter_margins(obj)

    # ------------------------------------------------------------- summary order
    def find_authors(self, all_segments) -> list:
        """A summary order is per curiam with NO byline; force the body-opener
        locator and skip byline detection, which otherwise latches onto a false
        byline ('by the Court, …') and starts the opinion mid-text."""
        if getattr(self, "_style", "").startswith("summary_order"):
            start = self._summary_order_body_start(all_segments)
            if start is not None:
                self._pc_starts = {start}
                return [start]
            return []
        return super().find_authors(all_segments)

    def _percuriam_start(self, all_segments):
        """A summary order is per curiam and has NO byline; its body opens after
        the counsel block (the panel/caption/counsel are all headmatter). The
        base looks for a 'Before … Judges.' roster, but a summary order's panel
        is 'PRESENT: …', so route summary orders to the counsel-block locator."""
        if getattr(self, "_style", "").startswith("summary_order"):
            return self._summary_order_body_start(all_segments)
        return super()._percuriam_start(all_segments)

    # The operative opener of a CA2 summary order's per-curiam body. Everything
    # before it (recital, SUMMARY ORDER heading, PRESENT panel, caption,
    # counsel) is headmatter. Uniform across counseled, pro-se, and consolidated
    # orders — unlike the counsel block, which is absent or unlabeled in some.
    _BODY_OPENERS = (
        "appeal from",
        "appeals from",
        "cross-appeal from",
        "petition for review",
        "petitions for review",
        "on appeal from",
        "on petition for review",
        "following disposition",
        "upon due consideration",
        "on consideration",
    )

    def _summary_order_body_start(self, all_segments):
        """Index of the first body segment of a summary order — the first
        segment opening with the order's operative language ('Appeal from a
        judgment …' / 'UPON DUE CONSIDERATION …')."""
        for j, (_pno, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip().lower()
            if any(t.startswith(o) for o in self._BODY_OPENERS):
                return j
        return None

    def skip_headmatter_segment(self, seg) -> bool:
        """Route CA2's standard summary-order advisory to ``dropped``.

        The advisory is printed as several left-aligned segments, not one
        notice block: the final ``COUNSEL.`` and Rule 25(a)(5) lines otherwise
        fall through the headmatter parser and become apparent unplaced prose.
        """
        text = " ".join(self.line_plain_text(line) for line in seg).strip().lower()
        if getattr(self, "_style", "").startswith("summary_order"):
            if (
                "rulings by summary order" in text
                or text == "counsel."
                or "appellate procedure 25(a)(5)" in text
            ):
                return True
        return super().skip_headmatter_segment(seg)

    # CA2 sets its summary orders (and some opinions) on numbered paper: a left
    # column of sequential line numbers (x0≈44, the body at x0≈86) that, left in
    # place, pdfplumber merges onto each line ('10 PER CURIAM:', '8 DAVID JOHN
    # CAMPBELL,') — breaking byline, caption, and heading detection. There is no
    # margin rule, so the gutter is found by CONTENT: a far-left column of bare
    # integers. Gated on detection, so un-numbered filings are untouched.
    def page_lines(self, page):
        if getattr(self, "_ca2_notice_furniture", None) is not None and page.page_number == 1:
            for line in page.extract_text_lines():
                text = " ".join((line.get("text") or "").split())
                if "Appellate Procedure 25(a)(5)" in text and text not in self._ca2_notice_furniture:
                    self._ca2_notice_furniture.append(text)
        gx = self._linenum_gutter_x(page)
        if gx is not None:
            gutter_start = 0.0
            if page.page_number == 1:
                # Summary-order advisories precede the numbered caption/body
                # on page 1. Filtering the whole page clips their first
                # letters because the advisory itself starts at x≈45, just
                # like the real gutter. Begin filtering at the first line
                # whose text actually carries a gutter number.
                for line in page.extract_text_lines():
                    chars = [c for c in line.get("chars", []) if c.get("text", "").strip()]
                    if chars and chars[0].get("text", "").isdigit() and chars[0].get("x0", 99) < 65:
                        gutter_start = line.get("top", 0)
                        break
            page = page.filter(
                lambda c: c.get("top", 0) < gutter_start
                or c.get("x0", 0) >= gx
            )
        lines = super().page_lines(page)
        # A separate writing can wrap its byline after "and":
        # ``CABRANES, Circuit Judge, concurring in the judgment and`` /
        # ``opinion of the Court:``.  Join those two physical lines so the
        # federal byline grammar sees the complete kind and terminator.
        out, index = [], 0
        while index < len(lines):
            line = lines[index]
            text = self.line_plain_text(line).strip()
            if (
                index + 1 < len(lines)
                and "Circuit Judge," in text
                and text.lower().endswith(" and")
            ):
                nxt = lines[index + 1]
                tail = self.line_plain_text(nxt).strip()
                if tail.lower().startswith("opinion of the court"):
                    merged = dict(line)
                    merged["chars"] = (line.get("chars") or []) + (nxt.get("chars") or [])
                    merged["text"] = f"{text} {tail}"
                    merged["x1"] = max(line.get("x1", 0), nxt.get("x1", 0))
                    merged["bottom"] = max(
                        line.get("bottom", line.get("top", 0)),
                        nxt.get("bottom", nxt.get("top", 0)),
                    )
                    out.append(merged)
                    index += 2
                    continue
            out.append(line)
            index += 1
        return out

    def find_footnote_separator(self, page):
        """CA2 uses two related footnote-rule indents.

        Full-width prose pages anchor the ~144pt rule at x≈108; pages whose
        main text is already inset anchor a ~110pt rule at x≈144.  Require
        footnote-sized text below the rule so an underline/caption shelf cannot
        become a separator.
        """
        candidates = []
        for rect in page.rects:
            width = rect.get("x1", 0) - rect.get("x0", 0)
            if not (
                rect.get("height", 0) < 2
                and 100 <= width <= 155
                and (
                    abs(rect.get("x0", 0) - self.body_baseline_x0) <= 5
                    or abs(
                        rect.get("x0", 0) - (self.body_baseline_x0 + 36)
                    )
                    <= 5
                )
                and rect.get("top", 0) > page.height * 0.30
            ):
                continue
            below = [
                char
                for char in page.chars
                if rect["top"] + 2 <= char.get("top", 0) <= rect["top"] + 55
                and (char.get("text") or "").strip()
            ]
            if below and sum(char.get("size", 99) <= 12.5 for char in below) >= len(below) * 0.7:
                candidates.append(rect)
        return min(candidates, key=lambda rect: rect["top"])["top"] if candidates else None

    @staticmethod
    def _linenum_gutter_x(page):
        """X just right of a left-margin line-number gutter, or None. The gutter
        is a vertical column of >=5 bare digit glyphs clustered at the far-left
        margin (x0 < 75). Cluster around the modal left edge so a stray body
        digit further right doesn't defeat detection (two-digit numbers span
        ~1.5 glyph widths, hence the 12pt window)."""
        digits = [
            c for c in page.chars if c.get("text", "").isdigit() and c.get("x0", 0) < 75
        ]
        if len(digits) >= 5:
            mode = Counter(round(c["x0"]) for c in digits).most_common(1)[0][0]
        else:
            mode = 999
        # Ordinary CA2 body text starts at x≈72. A sentence beginning with a
        # digit can therefore create a convincing-looking cluster of digits at
        # the body margin, but a real numbered-paper gutter is materially
        # farther left (≈44–48pt). Do not clip the first character of normal
        # prose merely because several paragraphs start with citations.
        if mode < 65:
            col = [c for c in digits if abs(c["x0"] - mode) <= 12]
            if len(col) >= 5:
                return max(c["x1"] for c in col) + 2

        # Some later CA2 writings restart line numbering immediately beside
        # an inset body column (numbers at x≈79/84, prose at x≈108), rather
        # than using the far-left x≈44 gutter present on the lead writing.
        # Identify the column by a long consecutive run of number-only words.
        words = [
            w
            for w in page.extract_words()
            if (w.get("text") or "").isdigit()
            and int(w["text"]) <= 40
            and w.get("x0", 999) < 95
            and w.get("x1", 999) < 105
        ]
        if len(words) < 8:
            return None
        words.sort(key=lambda word: word["top"])
        values = [int(word["text"]) for word in words]
        consecutive = sum(1 for a, b in zip(values, values[1:]) if b == a + 1)
        if consecutive < 6:
            return None
        return max(word["x1"] for word in words) + 4
