"""Bankruptcy Appellate Panel of the Ninth Circuit.

Set in Palatino Linotype throughout. Page 1: the clerk's FILED stamp in the
right margin, set in ARIAL ('FILED' at 28pt over the date, 'SUSAN M. SPRAUL,
CLERK / U.S. BKCY. APP. PANEL / OF THE NINTH CIRCUIT'); a bold 16pt
disposition flag ('NOT FOR PUBLICATION' or 'ORDERED PUBLISHED'); the bold
banner 'UNITED STATES BANKRUPTCY APPELLATE PANEL / OF THE NINTH CIRCUIT'; a
two-column caption (parties at x0=77 with their role lines indented to 185,
the BAP / Bk. / Adv. numbers and the bold disposition title 'MEMORANDUM*' or
'OPINION' flush right) fenced by two drawn half-rules; 'Appeal from the United
States Bankruptcy Court / for the District of ... / <name>, Bankruptcy Judge,
Presiding'; and the roster 'Before: NIEMANN, BRAND, and LAFFERTY, Bankruptcy
Judges.'. The disposition then opens straight into a centered bold
'INTRODUCTION' heading with no byline: it is issued by the panel, UNSIGNED.

Body: 14pt at x0=72, 28.3pt leading, paragraphs marked by a 36pt first-line
indent and NOTHING else -- no extra space between them. Quotations are set in
at 108 or 144 and single-spaced at 18.9pt. Footnotes are 12pt under a 144pt
rule at the rail.

Two styles in the corpus, both handled: nine unsigned NOT-FOR-PUBLICATION
MEMORANDUM dispositions and one ORDERED PUBLISHED OPINION. One of the nine
carries a separately signed concurrence ('SPRAKER, Bankruptcy Judge,
concurring.') after the panel's memorandum.
"""

from __future__ import annotations

from typing import Optional

from ._circuit import FederalCircuitBase

#: A blank caption cell that still holds its baseline (a no-break space).
_BLANK_CELL = "\u00a0"


class NinthCircuitBAP(FederalCircuitBase):
    court_id = "bap9"
    court_label = "Bankruptcy Appellate Panel of the Ninth Circuit."
    circuit_phrase = "bankruptcy appellate panel"
    body_baseline_x0 = 72.0

    # Body 28.3pt, quotations 18.9pt, footnotes 16.2pt. Paragraph breaks carry
    # NO extra leading here, so the body's own 28.3 must stay inside the 'body'
    # band -- the base's 40pt boundary would be reached by nothing at all and
    # its 22pt single cutoff would call every body segment a block quote.
    gap_tight_max = 12.0
    gap_single_max = 22.0
    gap_double_max = 34.0

    # Nothing on the page is set tighter than a quotation, so the notice band
    # is empty; keep it anyway rather than let an unforeseen tight run vanish.
    drop_notice_in_body = False

    # No running header: every continuation page opens with body text at
    # top~76 and carries its folio in the bottom margin.
    page2_header_cutoff = 0.0

    # NOT set: the shared ``banner_center_min_size`` escape hatch centres any
    # row of a given size whose midpoint is near the page centre, and this
    # court's banner is set at the BODY size (14pt) -- so the hook cannot be
    # aimed at the banner without also catching body lines, which then read as
    # centered and, being short and unpunctuated, as section headings
    # (olivier_rigon's opening body line became a heading that way). Page 1's
    # centring is decided in ``extract_headmatter`` instead, where it can be.
    banner_center_min_size = None

    def matches_expected_layout(self, pdf) -> bool:
        """The banner reads 'UNITED STATES BANKRUPTCY APPELLATE PANEL / OF THE
        NINTH CIRCUIT' -- never 'United States Court of Appeals', and split over
        two lines, so the family's same-line phrase check cannot see it."""
        if not pdf.pages:
            return False
        text = " ".join(
            (line.get("text") or "") for line in pdf.pages[0].extract_text_lines()
        ).lower()
        return "bankruptcy appellate panel" in text and "ninth circuit" in text

    # -------------------------------------------------------------- furniture
    def extract(self, pdf_path):
        self._stamp_rows = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Flush the stamp onto the document BEFORE the completeness sweep --
        appending after ``extract`` returns would put it there after the sweep
        had already read the sections, so every stamp row would be reported
        unplaced while sitting in the Removed box."""
        extra = list(dict.fromkeys(self._stamp_rows))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def _is_stamp_char(self, char) -> bool:
        """The clerk's FILED stamp, identified by TYPEFACE.

        The opinion is set entirely in Palatino Linotype; the stamp is the only
        Arial on the sheet. Position cannot do this job -- the stamp starts at
        x0~466 but page 1's own footnotes run past x=536, so an x-threshold
        shreds them. The only other Arial in the corpus is a scattering of
        single space glyphs, which carry no text.
        """
        return "Arial" in (char.get("fontname") or "")

    def correct_page_geometry(self, page) -> None:
        """Measure the caption's shelves, and take the stamp off page 1.

        The court draws exactly two horizontal rules across the caption, both
        running from the body rail to x1~340 -- a little over half the measure.
        They are the shelves closing the debtor block and the parties block,
        and their right end is ALSO the caption's column boundary: everything
        left of it is the party column, everything right of it the BAP / Bk. /
        Adv. numbers and the disposition title. Recording them here gives
        ``extract_headmatter`` the column split measured off the page instead of
        guessed. (Each rule is drawn with a 0.5pt end cap beyond x1, which the
        width window excludes.)

        The stamp is taken off at CHAR level.

        The stamp's rows share baselines with the banner and the disposition
        flag, so pdfplumber returns them merged: clifton_sanders' page 1 yields
        one line reading 'NOT FOR PUBLICATION SUSAN M. SPRAUL, CLERK'. A
        whole-line test cannot classify that; splitting by char can. Doing it
        here -- where the completeness audit reads the same corrected page the
        extractor does -- keeps a half-furniture line from matching neither
        haystack and reading as lost when it is merely split between the
        headmatter and the Removed box.
        """
        super().correct_page_geometry(page)
        if page.page_number != 1:
            return
        self._cap_shelves = sorted(
            (r["top"], r["x1"])
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2
            and abs(r["x0"] - self.body_baseline_x0) <= 2.0
            and 250.0 <= (r["x1"] - r["x0"]) <= 290.0
        )
        junk = [c for c in page.chars if self._is_stamp_char(c)]
        if not junk:
            return
        if getattr(self, "_stamp_rows", None) is None:
            self._stamp_rows = []
        # Capture the text HERE, from the page's complete char set: by the time
        # the line builder has split runs on x-gaps the stamp survives only as
        # fragments that no per-line pass can put back together.
        rows: dict = {}
        for char in junk:
            rows.setdefault(round(char.get("top", 0)), []).append(char)
        for top in sorted(rows):
            row = sorted(rows[top], key=lambda c: c.get("x0", 0))
            text = self.line_plain_text({"chars": row}).strip()
            if text:
                self._stamp_rows.append(text)
        for char in junk:
            char["upright"] = False

    def page_lines(self, page):
        """Drop the stamp's chars out of any line that still carries them."""
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        kept = []
        for line in lines:
            chars = line.get("chars") or []
            rest = [c for c in chars if not self._is_stamp_char(c)]
            if len(rest) == len(chars):
                kept.append(line)
            elif rest:
                kept.append(self._rebuild_line(line, rest))
        return kept

    # -------------------------------------------------------------- headings
    def _line_all_bold(self, line) -> bool:
        """Every letter and digit on the row is bold -- and nothing more.

        The shared test adds a shortness guard so a body line whose bold
        case-name citation fills the measure cannot read as a heading. Nothing
        in this court is set bold except the cover sheet, the byline and the
        section heads -- case names are ITALIC here -- so the guard has nothing
        to protect against, and it does real damage: a lettered head routinely
        runs past its 512pt limit ('B. The bankruptcy court did not abuse its
        discretion in granting the' reaches 522), which reads as NOT-bold and
        severs the head from its own second row ('Dental Group's motion.').
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
        """A section head: a short run of rows that are bold throughout. The
        top-level heads are centered ('INTRODUCTION', 'FACTS', 'DISCUSSION');
        the lettered and roman-numbered heads under them sit LEFT at the rail or
        at x0=99-108, and a long one wraps to a second row."""
        return bool(lines) and len(lines) <= 3 and all(
            self._line_all_bold(l) for l in lines
        )

    def classify_segment(self, seg) -> str:
        """Route a WRAPPED bold head to the one-unit branch: it is set
        single-spaced (19pt), which lands it in the block-quote band and made it
        render as a quotation of the opinion's own heading. 'single' hands the
        whole run to ``classify_paragraph`` as ONE paragraph (CLAUDE.md 7)."""
        kind = super().classify_segment(seg)
        if kind in ("notice", "blockquote") and self._bold_head_run(seg):
            return "single"
        return kind

    def classify_paragraph(self, lines) -> str:
        if self._bold_head_run(lines):
            return "heading"
        return super().classify_paragraph(lines)

    # ------------------------------------------------------------ headmatter
    #: A gutter this wide between two runs on one baseline separates the
    #: caption's columns; ordinary word spacing at 14pt is under 5pt.
    _GUTTER_MIN = 10.0

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Rebuild the cover as styled rows plus ONE two-column caption block.

        pdfplumber returns each caption baseline as a single line with both
        columns run together -- 'In re: BAP No. ID-25-1068-NBL', 'v.
        MEMORANDUM*', and worst of all 'Appellant, v. MEMORANDUM* MARC HOWELL,'
        once three baselines merge -- so left verbatim the caption reads as
        nonsense. Split each baseline at the shelves' right end (measured in
        ``correct_page_geometry``) and hand the two halves to the two-column
        caption block, with the drawn shelves as the left column's own rules and
        the role lines ('Debtor.', 'Appellant,', 'Appellee.') kept at their
        indent under the party they belong to.

        The columns are held apart by whitespace, not by a drawn vertical or a
        glyph rail, so ``rail`` is None: the renderer draws no divider, because
        the page draws none (CLAUDE.md 5).

        Everything outside the caption -- the disposition flag, the banner, the
        'Appeal from ...' history with its trial-judge line, and the panel
        roster -- stays a styled row in document order, each keeping its own
        alignment and its size relative to the 14pt body.
        """
        lines, dropped = [], []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                text = " ".join((l.get("text") or "").strip() for l in seg).strip()
                if text:
                    dropped.append(text)
                continue
            lines.extend(l for l in seg if (l.get("text") or "").strip())

        shelves = list(getattr(self, "_cap_shelves", []) or [])
        zone = self._caption_zone(lines, shelves)
        width = getattr(self, "_page1_width", None) or 612.0
        rows = []
        prev_top = None
        for line in lines:
            if zone and zone[0] <= line["top"] <= zone[1]:
                if not any(isinstance(r, dict) and r.get("__caption__") for r in rows):
                    rows.append(self._caption_block(lines, zone, shelves))
                prev_top = line["top"]
                continue
            # Outside the caption the cover has exactly two kinds of row: a
            # display row centred on the page (the flag, the banner, the
            # 'Appeal from ...' history, 'APPEARANCES'), and prose flush at the
            # body rail (the counsel block and the panel roster). A row that
            # starts at the rail is prose -- which is what tells the counsel
            # line apart from the centred history above it, since both happen
            # to be about as wide and about as centred.
            centered = (
                line["x0"] > self.body_baseline_x0 + 3
                and abs((line["x0"] + line["x1"]) / 2.0 - width / 2.0) <= 8.0
            )
            tight = prev_top is not None and line["top"] - prev_top <= 24.0
            # The counsel block is the one row here that wraps ('Miles L.
            # Prince argued for appellant; Andrew S. Bisom of Bisom Law' /
            # 'Group argued for appellee.'); fold it back together rather than
            # orphan the tail (CLAUDE.md 7).
            if (
                tight
                and not centered
                and rows
                and isinstance(rows[-1], dict)
                and rows[-1].get("__hm__")
                and rows[-1].get("align") == "L"
            ):
                rows[-1]["html"] = (
                    rows[-1]["html"] + " " + self.line_inline_text(line)
                ).strip()
                prev_top = line["top"]
                continue
            if prev_top is not None and not tight:
                rows.append("")
            prev_top = line["top"]
            size, _, _ = self.line_meta(line)
            rows.append(
                {
                    "__hm__": True,
                    "html": self.line_inline_text(line),
                    "rel": round(size / 14.0, 3),
                    "align": "C" if centered else "L",
                }
            )
        return {"court": self.court_label, "summary": rows, "dropped": dropped}

    def _caption_zone(self, lines, shelves):
        """(first_top, last_top) of the caption block, or None.

        The zone ENDS at the lower shelf -- the rule the court draws to close
        the parties block. It BEGINS at the first baseline that carries a
        genuine second column: a run starting right of the shelves' end with a
        gutter in front of it. That test is what separates the caption from the
        banner above it, which also crosses the column boundary but does so as
        one unbroken run of text.
        """
        if not shelves:
            return None
        split_x = max(x1 for _t, x1 in shelves)
        last = max(t for t, _x in shelves)
        first = None
        for line in lines:
            if line["top"] >= last:
                continue
            if self._caption_row_parts(line, split_x)[1]:
                first = line["top"]
                break
        return None if first is None else (first, last)

    def _caption_row_parts(self, line, split_x):
        """(left_chars, right_chars) for one caption line.

        The shared line builder already splits the FIRST caption block's
        baselines on their x-gap and tags the halves ``_caption_col`` L / R --
        but it gives up below the first shelf, leaving the parties block's
        baselines merged. Honour its verdict where it reached one, and fall back
        to the gutter test where it did not, so both blocks come out in the same
        two columns.
        """
        col = line.get("_caption_col")
        chars = sorted(line.get("chars") or [], key=lambda c: c.get("x0", 0))
        if col == "R":
            return [], chars
        if col == "L":
            return chars, []
        return self._split_at_gutter(line, split_x)

    def _split_at_gutter(self, line, split_x):
        """Split a baseline into (left_chars, right_chars) at the caption
        gutter. The right column only exists when a run actually STARTS beyond
        ``split_x``; a single run straddling it (the banner) stays whole."""
        chars = sorted(line.get("chars") or [], key=lambda c: c.get("x0", 0))
        cut = None
        prev_x1 = None
        for i, char in enumerate(chars):
            if not (char.get("text") or "").strip():
                continue
            if (
                char["x0"] >= split_x
                and prev_x1 is not None
                and char["x0"] - prev_x1 >= self._GUTTER_MIN
            ):
                cut = i
                break
            prev_x1 = char["x1"]
        if cut is None:
            return chars, []
        return chars[:cut], chars[cut:]

    def _caption_block(self, lines, zone, shelves) -> dict:
        split_x = max(x1 for _t, x1 in shelves)
        # Group by baseline: the two halves of an already-split row are two
        # separate line objects sharing one top, and they are ONE caption row.
        groups: dict = {}
        for line in lines:
            if zone[0] <= line["top"] <= zone[1]:
                groups.setdefault(round(line["top"], 1), []).append(line)
        cells = []
        for top in sorted(groups):
            left, right = [], []
            for line in groups[top]:
                lchars, rchars = self._caption_row_parts(line, split_x)
                left.extend(lchars)
                right.extend(rchars)
            left.sort(key=lambda c: c.get("x0", 0))
            right.sort(key=lambda c: c.get("x0", 0))
            cells.append((top, left, right))
        col_left = min(
            (c[0]["x0"] for _t, c, _r in cells if c), default=self.body_baseline_x0
        )

        left_col, right_col = [], []

        def emit(l_entry, r_entry):
            left_col.append(l_entry)
            right_col.append(r_entry)

        pending = list(shelves)
        prev_top = None
        for top, lchars, rchars in cells:
            # A shelf drawn above this baseline closes the block above it.
            while pending and pending[0][0] < top:
                emit({"__shelf__": True}, "")
                pending.pop(0)
            # A gap not explained by a shelf is real vertical space.
            if prev_top is not None and top - prev_top > 24.0:
                emit("", "")
            prev_top = top
            ltext = self.line_inline_text({"chars": lchars}).strip() if lchars else ""
            rtext = self.line_inline_text({"chars": rchars}).strip() if rchars else ""
            # A side with nothing on this baseline still occupies the baseline:
            # give it a full-height blank cell, not the short inter-block
            # spacer, or the two columns lose step and 'Bk. No. ...' rides up
            # off the party row it is printed beside.
            emit(
                {"h": ltext, "ind": round(lchars[0]["x0"] - col_left)}
                if ltext
                else {"h": _BLANK_CELL},
                {"h": rtext} if rtext else {"h": _BLANK_CELL},
            )
        for _t, _x in pending:  # the closing shelf, below the last baseline
            emit({"__shelf__": True}, "")

        return {
            "__caption__": True,
            "left": left_col,
            "right": right_col,
            "rail": None,
            "rail_rows": 0,
        }

    # ----------------------------------------------------------------- author
    def find_authors(self, all_segments) -> list:
        """The panel's disposition is UNSIGNED; a concurrence is signed.

        The family takes a signed byline as proof that there is no unsigned per
        curiam opinion and returns only the signed writings. Here that is
        exactly backwards: the memorandum is always the panel's, unsigned, and
        von_neitsch's 'SPRAKER, Bankruptcy Judge, concurring.' on page 16 sits
        AFTER fifteen pages of it -- so keying off the concurrence alone
        swallows the whole majority into the headmatter. Take both: the panel's
        opinion opening after the roster, then any signed writing below it.

        The trial-judge line ('Noah G. Hillen, Chief Bankruptcy Judge,
        Presiding') is not a byline and the family's form test already declines
        it -- 'Presiding' is not a concur/dissent clause -- which is what the
        generic parser was mistaking for the author on all ten fixtures.
        """
        signed = [
            i
            for i, (_p, seg, _k) in enumerate(all_segments)
            if seg and self._byline_split(seg[0]) is not None
        ]
        signed = [
            i
            for n, i in enumerate(signed)
            if self._opinion_has_body(
                all_segments,
                i,
                signed[n + 1] if n + 1 < len(signed) else len(all_segments),
            )
        ]
        self._pc_starts = set()
        start = self._percuriam_start(all_segments)
        if start is not None and (not signed or start < signed[0]):
            self._pc_starts.add(start)
            return [start] + signed
        return signed

    def build_opinion(self, op_start, op_end, **kwargs):
        """Keep the panel opinion's opening heading a heading.

        An unsigned opinion has no byline line, so the family hands its first
        line to the body builder as prose -- but that first line is the
        centered bold 'INTRODUCTION' (or 'FACTS', on the one file that opens
        straight into them). Re-tag it from the same geometry the shared
        classifier uses, so the disposition does not open with its own section
        head set as a paragraph.
        """
        op = super().build_opinion(op_start, op_end, **kwargs)
        seg = kwargs["all_segments"][op_start][1]
        if (
            op.blocks
            and op_start in getattr(self, "_pc_starts", set())
            and self.classify_paragraph(seg) == "heading"
        ):
            op.blocks[0].kind = "heading"
        return op

    # ------------------------------------------------------------- footnotes
    def find_footnote_separator(self, page) -> Optional[float]:
        """A 144pt hairline at the body rail.

        The court also draws two half-rules of 268pt across the caption on page
        1, so width alone must be tight; and the rule is a vector LINE on some
        sheets and a RECT on others, so both collections must be read.
        """
        cands = [
            r
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2
            and abs((r["x1"] - r["x0"]) - 144.0) <= 2.0
            and abs(r["x0"] - self.body_baseline_x0) <= 4.0
        ]
        return min(c["top"] for c in cands) if cands else None
