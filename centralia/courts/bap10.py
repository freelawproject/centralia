"""Bankruptcy Appellate Panel of the Tenth Circuit.

A federal slip opinion in all but the banner. Page 1 carries the CM/ECF
docket strip, the clerk's FILED stamp in the right margin, a centered
'UNITED STATES BANKRUPTCY APPELLATE PANEL / OF THE TENTH CIRCUIT' banner
over typed underscore rules, a two-column caption (parties left, BAP and
bankruptcy-court numbers right), 'Appeal from the United States Bankruptcy
Court for the District of …', and the panel roster ('Before ROMERO, Chief
Judge, HALL, and LOYD, Bankruptcy Judges.'). The opinion opens on page 2
with a plain, non-bold byline — 'HALL, Bankruptcy Judge.' — over a
double-spaced body at x0=72 with a 36pt first-line indent.

The circuit family fits the byline by FORM (a name, a bench title reached
through title qualifiers — 'bankruptcy' is already one — then a period), so
only this court's furniture and its footnote rule need describing.
"""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class TenthCircuitBAP(FederalCircuitBase):
    court_id = "bap10"
    court_label = "Bankruptcy Appellate Panel of the Tenth Circuit."
    circuit_phrase = "bankruptcy appellate panel"
    body_baseline_x0 = 72.0
    # Double-spaced at ~30pt; quotations are set single-spaced at ~15pt.
    gap_tight_max = 17.0
    gap_single_max = 24.0
    gap_double_max = 46.0
    # The body opens at top≈75 on page 2 (the byline itself). The family
    # default reserves the first 95pt of continuation pages for a docket
    # header, which here would swallow the byline whole. The one thing that
    # does sit up there is the CM/ECF strip, dropped by font below.
    page2_header_cutoff = 0.0
    # This court prints no notices in the body. Because the body is DOUBLE
    # spaced, every single-spaced run lands in the 'notice' band — quotations,
    # and the bold lettered sub-headings ('A. The Bankruptcy Court complied
    # with …', wrapping to a second line at the body rail). Dropping that band
    # discards real text, so keep it: what is a quotation is promoted by
    # classify_segment below, and the rest returns as ordinary body.
    drop_notice_in_body = False

    # ------------------------------------------------------------- furniture
    def extract(self, pdf_path):
        self._bap_furniture = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Flush the furniture onto the document BEFORE the completeness sweep.
        Appending it after ``extract`` returns would land it there after the
        sweep had already read the sections, so every stamp line would be
        reported unplaced while sitting in the Removed box."""
        extra = list(dict.fromkeys(self._bap_furniture))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def matches_expected_layout(self, pdf) -> bool:
        """The banner reads 'UNITED STATES BANKRUPTCY APPELLATE PANEL / OF THE
        TENTH CIRCUIT' — never 'United States Court of Appeals', and split over
        two lines, so the family's same-line phrase check cannot see it."""
        if not pdf.pages:
            return False
        text = " ".join(
            (line.get("text") or "") for line in pdf.pages[0].extract_text_lines()
        ).lower()
        return "bankruptcy appellate panel" in text and "tenth circuit" in text

    def correct_page_geometry(self, page) -> None:
        """Take the strip and the stamp off the page for EVERY reader.

        Both collide with real text — pdfplumber groups the stamp's rows onto
        the banner's baselines ('UNITED STATES BANKRUPTCY APPELLATE PANEL' +
        'of the Tenth Circuit'), and returns the strip and the stamp's first
        row as one interleaved line on some sheets. Marking them here, where
        the completeness audit reads the same corrected page the extractor
        does, keeps a half-furniture line from matching neither haystack and
        reading as lost when it is merely split between the body and the
        Removed box."""
        super().correct_page_geometry(page)
        junk = [c for c in page.chars if self._is_furniture_char(page, c)]
        if not junk:
            return
        # Capture the text HERE, from the page's complete char set, before the
        # line builder splits runs on x-gaps: by the time page_lines has run,
        # the stamp survives only as fragments ('F', 'u', 'e', 'ILED') that no
        # per-line pass can put back together.
        if getattr(self, "_bap_furniture", None) is None:
            self._bap_furniture = []
        self._bap_furniture.extend(self._furniture_rows(page, junk))
        for char in junk:
            char["upright"] = False

    def page_lines(self, page):
        """Route this court's two pieces of page furniture to ``dropped``.

        1. The CM/ECF docket strip across the top of EVERY page ('BAP Appeal
           No. 25-2 Docket No. 52 Filed: 02/03/2026 Page: 1 of 13'). It is the
           only Helvetica on the sheet — the opinion itself is set entirely in
           Times — so the typeface identifies it outright, on page 1 as well as
           on continuation pages, without reserving a band of the page.
        2. The clerk's FILED stamp in page 1's right margin.

        Left in, both are body: the docket strip lands mid-sentence at every
        page turn, and the stamp's lines interleave with the banner rows.

        Done at CHAR level, because the two collide: the strip and the stamp's
        first row share a baseline on some sheets, so pdfplumber returns them
        as ONE line whose text interleaves both ('… Page:U 1.S .o Bfa n1k5rup').
        A whole-line test cannot classify that; splitting by char can.
        """
        lines = super().page_lines(page)
        kept = []
        for line in lines:
            chars = line.get("chars") or []
            junk = [c for c in chars if self._is_furniture_char(page, c)]
            if not junk:
                kept.append(line)
                continue
            rest = [c for c in chars if not self._is_furniture_char(page, c)]
            if rest:
                kept.append(self._rebuild_line(line, rest))
        return kept

    def _furniture_rows(self, page, chars) -> list:
        """Reassemble furniture chars into readable rows for the Removed box.

        The two blocks overlap, so one pdfplumber line can hold chars of both
        — and taken in x order they interleave into rubbish ('Fue ILED U.S').
        Separate the strip from the stamp first, then rebuild each by its own
        baseline, so the box shows what was removed instead of shredded text.
        """
        out = []
        for group in (
            [c for c in chars if "Helvetica" in (c.get("fontname") or "")],
            [c for c in chars if "Helvetica" not in (c.get("fontname") or "")],
        ):
            rows = {}
            for char in group:
                rows.setdefault(round(char.get("top", 0)), []).append(char)
            for top in sorted(rows):
                row = sorted(rows[top], key=lambda c: c.get("x0", 0))
                text = self.line_plain_text({"chars": row}).strip()
                if text:
                    out.append(text)
        return out

    def _is_furniture_char(self, page, char) -> bool:
        font = (char.get("fontname") or "").split("+")[-1]
        if "Helvetica" in font:  # the CM/ECF docket strip
            return True
        if page.page_number != 1:
            return False
        # The clerk's FILED stamp, by FONT + SIZE. Position alone cannot do it:
        # the stamp starts at x0≈467 but the banner's own last glyphs reach
        # x1≈469, and page 1's footnotes run out past x=520 — an x-threshold
        # shreds both. The stamp is the only bold Times on the sheet set at
        # 8pt or 12pt (the banner and the section heads are bold Times 13, the
        # body roman 13), so the face identifies it exactly.
        return "Bold" in font and round(char.get("size", 0), 1) in (8.0, 12.0)

    def classify_paragraph(self, lines):
        """A section head is a fully-bold run at the paragraph indent.

        This court numbers its heads ('I. Background and Procedural History',
        'II. Jurisdiction') and letters its sub-heads ('b. The Bankruptcy Court
        did not err in denying the Motion.'), setting all of them LEFT at the
        indent rather than centered — so the family's centered-and-bold test
        never sees them and they render as ordinary paragraphs. A sub-head that
        wraps is still one heading, so accept a second line (CLAUDE.md 7)."""
        if 1 <= len(lines) <= 2 and all(self._line_all_bold(l) for l in lines):
            return "heading"
        return super().classify_paragraph(lines)

    # ----------------------------------------------------------- blockquotes
    def classify_segment(self, seg) -> str:
        """Promote an indented single-spaced run to a block quote.

        The body is DOUBLE-spaced at ~30pt, so a quotation's ordinary single
        spacing (~15pt) lands under ``gap_tight_max`` and classifies as a
        notice — which the circuit family drops from the body outright. That
        is how the quoted issue lists and record passages were disappearing.

        The family's both-margins test can't be turned on to catch them: most
        of this court's quotes are indented on both sides (x0=108, x1=504), but
        some are indented on the LEFT only and run to the full body measure
        (douglas_gould's Pioneer factors at x0=144, x1=540). Since the body is
        double-spaced here, the left indent plus the tight leading is already
        conclusive — the right margin carries no signal and isn't consulted.
        """
        kind = super().classify_segment(seg)
        if kind != "notice" or len(seg) < 2:
            return kind
        width = getattr(self, "_page1_width", None) or 612.0
        x0s = [line["x0"] for line in seg]
        edge = min(x0s)
        # Indented past the paragraph's own first-line indent, but not out in
        # the right-hand column (a signature block is not a quotation).
        if not self.body_baseline_x0 + 30 <= edge <= width * 0.4:
            return kind
        # A consistent flush-left edge: ≥2 lines share it. Rejects centered or
        # short heading runs, which are also indented but ragged on the left.
        if sum(1 for x in x0s if abs(x - edge) <= 3) < 2:
            return kind
        return "blockquote"

    # ------------------------------------------------------------- footnotes
    def find_footnote_separator(self, page):
        """BAP10 sets its footnotes at BODY size (13pt), so the shared
        discriminator — footnote-sized text directly below the rule — can never
        fire, and every footnote in the volume was lost: 1,649 lines across all
        ten fixtures, the largest single loss in the corpus.

        Identify the rule by its own geometry instead. The court draws exactly
        one 144pt rule per footnoted page, at the body rail (x0=72) or at the
        indent (x0=108); nothing else that width is drawn below the fold. The
        only other 144pt-ish rule in the corpus is the underline beneath page
        1's 'NOT FOR PUBLICATION', which sits at the very top of the sheet.

        A half-page cutoff is no good: a heavily footnoted sheet pushes the
        rule well up the page (desiree_myrum p.5 draws it at 385 on a 792pt
        sheet), and losing it there costs the whole zone. Bound it by the head
        band instead — the rule is distinctive enough on its own that only
        page 1's 'NOT FOR PUBLICATION' underline needs excluding, and that one
        sits at the very top and starts at x0≈231, out past the indent.
        """
        x0_max = self.body_baseline_x0 + 40
        tops = [
            r["top"]
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2
            and abs((r["x1"] - r["x0"]) - 144.0) <= 2.0
            and r["x0"] <= x0_max
            and r["top"] > 150
        ]
        return min(tops) if tops else None
