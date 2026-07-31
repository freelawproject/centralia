"""Bankruptcy Appellate Panel of the First Circuit.

Page 1 is a bold Times cover sheet, every row centered on the page: a flush
right 'FOR PUBLICATION' / 'NOT FOR PUBLICATION' flag at 16pt, the banner
'UNITED STATES BANKRUPTCY APPELLATE PANEL / FOR THE FIRST CIRCUIT' also at
16pt, then a stack of 12pt panels fenced off from one another by TYPED
underscore rules -- the BAP docket number, the bankruptcy case number, the
party blocks with their role lines ('STEVEN T. CARRIGAN, SR., / Debtor.'),
'Appeal from the United States Bankruptcy Court / for the District of
Massachusetts / (Hon. Janet E. Bostwick, U.S. Bankruptcy Judge)', the panel
roster ('Before / Godoy, Cary, and Gonzalez, / United States Bankruptcy
Appellate Panel Judges.'), counsel, and the date.

The opinion opens on page 2 with a bold byline at the body rail --
'Godoy, U.S. Bankruptcy Appellate Panel Judge.' / 'Finkle, Chief U.S.
Bankruptcy Appellate Panel Judge.' -- over a DOUBLE-spaced body (27.6pt
leading) at x0=72 with a 36pt first-line indent. Footnotes sit at 11pt under
a 144pt rule at the rail.

The circuit family fits that byline by FORM -- a name, then a run of title
qualifiers, then a singular bench title, then '.' -- and its ``_NON_AUTHOR``
list rejects the roster's 'United States Bankruptcy Appellate Panel Judges.'
line that the generic byline test turned into a phantom opinion. Only this
court's unusually long title needs describing.
"""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class FirstCircuitBAP(FederalCircuitBase):
    court_id = "bap1"
    court_label = "Bankruptcy Appellate Panel of the First Circuit."
    circuit_phrase = "bankruptcy appellate panel"
    body_baseline_x0 = 72.0

    # This panel's judges sign with the longest bench title in the corpus,
    # 'U.S. Bankruptcy Appellate Panel Judge', optionally prefixed 'Chief'.
    author_titles = (
        "Chief U.S. Bankruptcy Appellate Panel Judge",
        "U.S. Bankruptcy Appellate Panel Judge",
        "Bankruptcy Appellate Panel Judge",
        "Bankruptcy Judge",
        "Chief Judge",
        "Judge",
    )
    # The family reaches the title keyword only through a run of recognised
    # qualifier words; 'appellate', 'panel' and the abbreviated 'U.S.' are not
    # among them, so without these three the byline fails the form test and the
    # whole opinion falls into the headmatter (0 opinions on all ten fixtures).
    _TITLE_RUN_WORDS = FederalCircuitBase._TITLE_RUN_WORDS | {
        "appellate",
        "panel",
        "u.s",
    }

    # The body is DOUBLE spaced at 27.6pt and quotations are set single-spaced
    # at 13.8pt, so the two leadings differ by exactly 2x. The base class's
    # 16pt 'tight' cutoff puts a quotation in the notice band -- which the body
    # builder DROPS -- and that alone accounted for all 347 lost lines. Split
    # the two bands so a quotation lands in 'blockquote' (13.8) and the body in
    # 'body' (27.6) on leading alone; no indent test is needed.
    gap_tight_max = 10.0
    gap_single_max = 22.0
    gap_double_max = 32.0

    # The opinion's own byline sits at top=73.8 on page 2. The family default
    # reserves the first 95pt of every continuation page for a centered 'No.
    # <docket>' running header, which this court does not print -- its only
    # running furniture is the centered page number at the foot. Left at 95 the
    # byline, and the first body line of pages 3+, are cut.
    page2_header_cutoff = 0.0

    # The 16pt banner spans 402pt of a 612pt sheet -- wider than the width cap
    # that keeps a justified body line left-aligned -- so it reads 'L' on its
    # midpoint alone and its centring is lost. It is exactly midpoint-centered,
    # and nothing else on the sheet is set at 16pt except the publication flag
    # (pinned right, 158pt off-center), so the size is a safe key.
    banner_center_min_size = 16.0

    # -------------------------------------------------------------- headings
    def _line_all_bold(self, line) -> bool:
        """Every letter and digit on the row is bold -- and nothing more.

        The shared test adds a shortness guard so that a body line whose bold
        case-name citation fills the measure cannot read as a heading. This
        court has no bold prose at all: across the ten fixtures the only bold
        rows below the cover sheet are the byline and the section heads. So the
        guard has nothing to protect against here, and it does real damage --
        two heads run to x1=533 and x1=539, past its 512pt limit, so they read
        as NOT-bold, which cuts the head at that row: '2. Did the Debtor
        Demonstrate There Were Other Reasons to Conclude / the Current Case
        Would Result in a Confirmed Plan that Would Be' was severed from its
        own last row, 'Fully Performed'.
        """
        seen = False
        for char in line.get("chars") or []:
            text = char.get("text") or ""
            if not text.strip() or not text.isalnum():
                continue
            seen = True
            if "Bold" not in (char.get("fontname") or ""):
                return False
        return seen

    def _bold_head_run(self, lines) -> bool:
        """A section head: a short run of rows that are bold throughout.

        The heads are numbered and lettered three levels deep ('I. Relevant
        Legal Standards' at the rail, 'A. Section 362(c)(3)(A): Automatic
        Termination of the Automatic Stay' at x0=108, '2. Did the Debtor
        Demonstrate ...' at x0=144) and a long one wraps to a second or third
        row with a further hanging indent. Four rows covers the longest in the
        corpus and stays far short of a paragraph.
        """
        return bool(lines) and len(lines) <= 4 and all(
            self._line_all_bold(l) for l in lines
        )

    def classify_segment(self, seg) -> str:
        """Route a WRAPPED bold head to the one-unit branch.

        Only the top-level heads are centered ('BACKGROUND', 'DISCUSSION',
        'CONCLUSION'); the numbered and lettered heads sit LEFT, so the shared
        centered-and-bold test never sees them. A head that wraps is set
        single-spaced (13.8pt), which lands it in the block-quote band and made
        it render as a quotation of the opinion's own heading. Returning
        'single' hands the whole run to ``classify_paragraph`` as ONE
        paragraph, which is what a wrapped head is (CLAUDE.md 7).
        """
        kind = super().classify_segment(seg)
        if kind in ("notice", "blockquote") and self._bold_head_run(seg):
            return "single"
        return kind

    def classify_paragraph(self, lines) -> str:
        if self._bold_head_run(lines):
            return "heading"
        return super().classify_paragraph(lines)

    # ------------------------------------------------------------ page folds
    def build_opinion(self, op_start, op_end, **kwargs):
        """Rejoin a block quote that a page break cut mid-sentence.

        The shared cross-page fold in ``add_para`` covers ordinary paragraphs
        only, so a quotation that runs off the foot of one page and resumes at
        the head of the next comes back as two blocks. That is exactly the
        split CLAUDE.md 7 forbids, and it is common here because a footnote
        zone can eat most of a sheet: eight quotations across five of the ten
        fixtures resume at the head of the next page (caroline_ortega_berrios
        p7/p8 and p14/p15, charles_muszynski p3/p4, pcc_rokita p24/p25).

        (bap8 carries the same method for the same reason; the natural home is
        the circuit family base, which is off limits in this pass.)
        """
        op = super().build_opinion(op_start, op_end, **kwargs)
        op.blocks = self._fold_quote_across_pages(op.blocks)
        return op

    def _fold_quote_across_pages(self, blocks) -> list:
        out = []
        for block in blocks:
            if (
                out
                and out[-1].kind == "blockquote"
                and block.kind == "blockquote"
                and block.page == (out[-1].page or 0) + 1
                and not self._ends_sentence(out[-1].text)
            ):
                # The arriving half keeps its own <pagenumber> marker inline,
                # exactly as the shared paragraph fold does.
                out[-1].text = (out[-1].text + " " + block.text).strip()
                continue
            out.append(block)
        return out

    @staticmethod
    def _ends_sentence(text: str) -> bool:
        """Does this block close a sentence? Only a quotation left hanging
        mid-sentence is a page-break casualty; a quotation that ends on its own
        full stop, or on a citation, is complete, and the block that follows it
        at the head of the next page is a NEW quotation, not its tail
        (steven_carrigan p7 ends on '... the debtor is in bankruptcy . . . .[7]'
        and p8 opens a fresh quote of a different speaker). A quote paragraph that ends properly and is
        followed by an ellipsis-led continuation also stays its own block --
        two paragraphs of one quote is what the page shows."""
        trimmed = text.rstrip()
        # A trailing footnote reference, with or without the brackets a court
        # puts round it, is not the sentence's last word.
        if trimmed.endswith("]"):
            trimmed = trimmed[:-1].rstrip()
        if trimmed.endswith("</footnotemark>"):
            trimmed = trimmed[: trimmed.rfind("<footnotemark>")].rstrip()
        if trimmed.endswith("["):
            trimmed = trimmed[:-1].rstrip()
        # Strip the inline style tags so a bold/italic run at the end of the
        # row does not hide the punctuation underneath it.
        plain, depth = [], 0
        for ch in trimmed:
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                plain.append(ch)
        return "".join(plain).rstrip(" \"'”’)").endswith((".", "?", "!"))

    # ------------------------------------------------------------ headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """One styled row per cover-sheet line, keeping its own alignment.

        The cover sheet is a single centered column of one-line rows, EXCEPT
        the publication flag, which is pinned to the right margin. The base
        dump marks a centered row and leaves everything else to render flush
        left, so 'FOR PUBLICATION' loses its position (CLAUDE.md 6: right stays
        right). Emitting the style-preserving row form instead carries each
        line's alignment and its relative size -- which is the other thing the
        base dump flattens, and here it is structural: the banner and the flag
        are set a third larger than the panels below them.

        Line order and content are otherwise untouched, so the typed underscore
        rules stay literal glyph rows (they are text the court typed, not a
        drawn rule, and CLAUDE.md 5 forbids promoting one to the other).
        """
        rows, dropped = [], []
        base_size = 12.0
        prev = None
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                text = " ".join((l.get("text") or "").strip() for l in seg).strip()
                if text:
                    dropped.append(text)
                continue
            for line in seg:
                if not (line.get("text") or "").strip():
                    continue
                size, _, _ = self.line_meta(line)
                page = line.get("page_number") or 1
                # Keep the page's vertical rhythm: the panels are set one blank
                # line apart (27.6pt on a 13.8pt line) while the rows inside a
                # panel are consecutive. Anything under a line and a half of
                # leading is consecutive.
                if prev is not None and (
                    page != prev[0] or line["top"] - prev[1] > 24.0
                ):
                    rows.append("")
                prev = (page, line["top"])
                rows.append(
                    {
                        "__hm__": True,
                        "html": self.line_inline_text(line),
                        "rel": round(size / base_size, 3),
                        "align": self.line_alignment(line, self._page_width_of(line)),
                    }
                )
        return {"court": self.court_label, "summary": rows, "dropped": dropped}

    def _page_width_of(self, line) -> float:
        return getattr(self, "_page1_width", None) or 612.0
