"""Supreme Court of Connecticut.

Abbreviated-title byline running inline with the opinion text, not bold:
'BRIGHT, J. The plaintiff ...' / 'ALEXANDER, J. A jury found ...'. The shared
abbreviated-title base handles the 'NAME, J. <body>' form directly. The
Connecticut front matter (the 'officially released' notice and the 'Syllabus')
is handled by the shared ``ConnecticutStyle``.

The refinements below live here rather than in the shared family base because
each is keyed to the *Connecticut Reports* measure — a narrow 174–438 column
centred on the sheet, leaded at ~1.12x the type size and opened to ~1.6x
between paragraphs, with a single 10pt first-line indent:

  * the identified page furniture (the publication notice and the reporter's
    head band) is surfaced in the Removed box **before** the completeness sweep
    runs, so it reads as accounted-for rather than as unplaced content;
  * the reporter's front matter (Syllabus / Procedural History / counsel) is
    returned as styled rows — its own fonts, sizes, alignment, italics and
    vertical rhythm — instead of flattened plain text;
  * paragraphs are grouped by the reporter's leading, not by the indent: a run
    of consecutive one-line paragraphs (a plea-canvass transcript) and a
    centered heading that wraps over four rows both defeat an indent rule;
  * a quotation is never indented here, so the base's gap-band 'blockquote'
    can only be a false positive (body-measure lines sit at exactly two
    x-positions across all 50 files: flush at 174, indented at 184);
  * alignment is measured against the column's own axis, not the page centre,
    which otherwise reads every justified line as centered;
  * the bound reporter overprints each f-ligature on top of a space glyph, so
    the buried space has to be dropped or 'first' extracts as 'fi rst'.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme
from ._connecticut import ConnecticutStyle


class ConnecticutSupreme(ConnecticutStyle, AbbrevTitleSupreme):
    court_id = "conn"
    court_label = "Supreme Court of Connecticut."

    # Nothing but head furniture is ever printed above this on a Connecticut
    # Reports page: the reporter draws two hairline rules at 163.8/180.2 with
    # the volume/date band and the running case name between them, and the
    # measure is rigid — the body never opens above 187.7.
    head_band_max = 185.0

    # ------------------------------------------------------------------ setup
    def extract(self, pdf_path: str):
        self._conn_head = []
        self._conn_reporter = []
        return super().extract(pdf_path)

    # ------------------------------------------------------------- glyph fixes
    def correct_page_geometry(self, page) -> None:
        """Drop the space the bound reporter overprints under each ligature.

        In the bound *Connecticut Reports* every f-ligature is set as a space
        followed by the ligature drawn back over it, so the content stream reads
        ' ' 'fi' 'fi' ' ' 'r' for the 'fi' of 'first' — and the buried space
        comes out as a word break ('fi rst degree with a fi rearm', 'offi
        cially', 'certifi cation'). The base already drops the doubled glyph;
        this drops the buried space.

        Identified purely by geometry, so it cannot touch a real word space: a
        space is an artifact only when its whole box sits INSIDE the box of the
        non-space glyph beside it on the same baseline. A word space always
        sits between two glyph boxes, never within one. The completeness audit
        reads the page through this same hook, so both sides see the repair."""
        super().correct_page_geometry(page)
        chars = page.chars
        buried = []
        for i, c in enumerate(chars):
            if (c.get("text") or "") != " ":
                continue
            for j in (i - 1, i + 1):
                if not 0 <= j < len(chars):
                    continue
                n = chars[j]
                if (
                    (n.get("text") or "").strip()
                    and abs(n["top"] - c["top"]) <= 1.0
                    and n["x0"] <= c["x0"]
                    and c["x1"] <= n["x1"]
                ):
                    buried.append(i)
                    break
        for i in reversed(buried):
            del chars[i]

    # -------------------------------------------------------- page furniture
    def page_lines(self, page):
        """Also strip (and record) the reporter's head band on the *caption*
        page.

        ``ConnecticutStyle`` removes the band on continuation pages only,
        because in the advance-release format page 1 is the publication notice
        and the caption opens on page 2. The bound *Connecticut Reports* print
        the caption on their own first page, head band and all, so there the
        band survived into the caption ('Page 2 CONNECTICUT LAW JOURNAL March
        10, 2026' as the opening headmatter row).

        The band is identified by the reporter's own drawn rules, not by page
        number: a page that strokes a hairline the width of the body measure
        above the head cutoff is a Connecticut Reports page, and everything
        above that cutoff on it is furniture."""
        if not hasattr(self, "_conn_head"):  # page_lines used outside extract()
            self._conn_head = []
        lines = super().page_lines(page)
        band = self._head_band_text(page)
        if band:
            lines = [l for l in lines if l.get("top", 0) >= self.head_band_max]
            for t in band:
                if t not in self._conn_head:
                    self._conn_head.append(t)
        return lines

    def _head_band_text(self, page) -> list:
        """The text lines of the head band, read straight off the page so the
        band is recoverable even where the family base has already filtered it
        out of ``page_lines``. Empty unless the page draws the reporter's head
        rule."""
        if not any(
            abs(l.get("height", 0)) < 2
            and (l["x1"] - l["x0"]) >= 100
            and l["top"] < self.head_band_max
            for l in page.lines
        ):
            return []
        band = page.crop((0, 0, page.width, self.head_band_max - 0.1))
        return [t.strip() for t in (band.extract_text() or "").splitlines() if t.strip()]

    def _sweep_residual(self, doc, source_pages):
        """Surface the identified furniture *before* the completeness sweep.

        ``ConnecticutStyle.extract`` appends the publication notice to
        ``dropped`` after ``super().extract()`` has returned — but the sweep
        runs inside that call, so every one of the notice's 24 lines still read
        as unplaced content (1008 of this court's 1011 unplaced lines). Flush
        the notice and the head band first, then sweep."""
        extra = [t for t in (getattr(self, "_conn_notice", None) or []) if t]
        extra += [t for t in (getattr(self, "_conn_head", None) or []) if t]
        if extra:
            have = set(doc.dropped or [])
            doc.dropped = list(doc.dropped) + [t for t in extra if t not in have]
            self._conn_notice = []
            self._conn_head = []
        super()._sweep_residual(doc, source_pages)

    # ------------------------------------------------------------- body shape
    def classify_segment(self, seg) -> str:
        """A run of consecutive one-line paragraphs is not a block quote.

        Connecticut sets its body on a narrow centered measure: the line pitch
        inside a paragraph is ~12pt and the gap *between* paragraphs ~18pt, so
        a segment of several one-line paragraphs (the plea-canvass transcript
        in ``state_v._roberts``: '"The Defendant: Guilty.' / '"The Court: Do
        you understand?' / '"The Defendant: Yes.') has a median gap in the
        base's single-spaced band and is classified 'blockquote'. It is then
        split by gap rather than by indent, and — every gap being equal — comes
        out as one glommed block.

        The reporter never indents a quotation; across all 50 files every
        body-measure line sits either flush at the margin or at the single 10pt
        first-line indent. So 'blockquote' can only be this false positive
        here: demote it to body and let the indent-aware paragraph splitter
        separate the paragraphs."""
        kind = super().classify_segment(seg)
        return "body" if kind == "blockquote" else kind

    def split_body_paragraphs(self, seg) -> list:
        """Paragraph boundaries here are the reporter's LEADING, not its indent.

        The Connecticut Reports set a fixed rhythm: inside a paragraph the pitch
        is the line pitch (~12.3pt at the 11pt body, ~10.4 at the 8pt small
        measure); between paragraphs it opens to ~18pt (~16.4pt at 8pt). The
        10pt first-line indent the base keys on is the weaker signal here, and
        it fails in both directions:

        * a run of consecutive ONE-LINE paragraphs (the plea-canvass transcript
          in ``state_v._roberts``: '"The Defendant: Guilty.' / '"The Court: Do
          you understand?' / '"The Defendant: Yes.') is entirely first lines, so
          the segment's own left edge *is* the indent and the base joins all
          three into one run-on block;
        * a centered heading that wraps ('Whether "Hours Worked" Includes Time
          Employees' / 'Spend Undergoing Mandatory Security' / 'Screenings on
          Their Employers'' / 'Premises') has a different indent on every row,
          so the base cuts it into four blocks.

        Splitting on the leading gets both right, and agrees with the indent on
        ordinary prose."""
        if not seg:
            return []
        paras = [[seg[0]]]
        for line in seg[1:]:
            prev = paras[-1][-1]
            gap = line["top"] - prev["top"]
            if gap > self._line_pitch_max(prev, line):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def _begins_paragraph_block(self, lines) -> bool:
        """A line at the reporter's 10pt first-line indent opens a paragraph, so
        it is never a page-break continuation of the paragraph above.

        Without this the page-break fold in ``build_opinion`` swallows a new
        paragraph that happens to open a page: page 7 of ``state_v._roberts``
        starts a fresh transcript turn ('"The Defendant: Yes.') at the indent
        and it was being appended to the last paragraph of page 6. A genuine
        continuation always returns flush to the measure at 174."""
        if lines and lines[0]["x0"] >= self.body_baseline_x0 + self.para_indent_min:
            return True
        return super()._begins_paragraph_block(lines)

    def _line_pitch_max(self, *lines) -> float:
        """The widest gap that is still ordinary leading between two wrapped
        lines. The reporter leads at ~1.12x the type size and opens paragraphs
        at ~1.6x, so 1.35x separates them at every size it sets."""
        size = max([self.line_meta(l)[0] for l in lines] + [8.0])
        return 1.35 * size

    def classify_paragraph(self, lines) -> str:
        """A centered heading that wraps past the base's three-line window is
        still a heading. Connecticut's discriminator is its own margin: every
        wrapped line of body prose returns flush to the left measure, so a
        multi-line group in which NO line touches that margin is a centered
        stack, not prose."""
        tag = super().classify_paragraph(lines)
        if tag != "p" or len(lines) < 2:
            return tag
        if any(l["x0"] <= self.body_baseline_x0 + 2 for l in lines):
            return tag
        text = " ".join((l.get("text") or "").strip() for l in lines).strip()
        if not text or text.endswith((".", "?", "!", ";", ":", ",")):
            return tag
        return "heading"

    # ------------------------------------------------- styled reporter matter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Caption as the family base renders it; the reporter's front matter
        (from the italic 'Syllabus' / 'Procedural History' heading down) as
        styled rows that keep their own size, alignment, italics and spacing."""
        lines = []
        for seg in headmatter_segs:
            for line in seg:
                if not (line.get("text") or "").strip():
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                lines.append((pno, round(line["top"], 1), round(line["x0"], 1), line))
        lines.sort(key=lambda r: (r[0], r[1], r[2]))
        cut = self._reporter_matter_start(lines)
        caption = [
            (pno, top, x0, (line.get("text") or "").strip())
            for pno, top, x0, line in lines[:cut]
        ]
        self._conn_reporter = self._conn_styled_rows(lines[cut:])
        return {
            "court": self.court_label or self.court_id,
            "summary": self._paged_layout_rows(caption) + self._conn_reporter,
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [],
        }

    def _reporter_matter_start(self, lines) -> int:
        """Index of the first line of the reporter's front matter.

        The reporter announces each of its own sections with a centered italic
        heading set at the small measure — 'Syllabus', or 'Procedural History'
        where a per curiam disposition carries no syllabus. Everything above
        the first such heading is the court's own caption (party names, docket,
        panel); everything from it down is reporter matter, which the
        publication notice on page 1 says in as many words is copyrighted to
        the Secretary of the State rather than part of the opinion."""
        for i, (_pno, _top, _x0, line) in enumerate(lines):
            _size, font, _bold = self.line_meta(line)
            if ("Italic" in font or "Oblique" in font) and self._measure_align(
                line
            ) == "C":
                return i
        return len(lines)

    def _measure_align(self, line) -> str:
        """Alignment relative to the reporter's own measure, not the page.

        The Connecticut Reports set a narrow column (174–438) in the middle of
        the sheet, so the shared page-centre test reads *every* justified body
        line as centered — rendering the whole syllabus ragged-centre. A line is
        centered here only if it stops short of the right measure, starts in
        from the left measure, and is symmetric about the column's own axis."""
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        left = self.body_baseline_x0
        right = pw - self.body_baseline_x0
        axis = (left + right) / 2
        if (
            line["x0"] > left + 4
            and line["x1"] < right - 4
            and abs((line["x0"] + line["x1"]) / 2 - axis) <= 6
        ):
            return "C"
        return "L"

    def _conn_styled_rows(self, rows) -> list:
        """Reporter matter as styled headmatter rows: one row per source line
        (the reporter's own line breaks), each carrying its relative size, its
        alignment and its inline italics, with a blank row wherever the page
        leaves a real vertical gap."""
        if not rows:
            return []
        metas = [
            (pno, top, line, self.line_meta(line)[0]) for pno, top, _x0, line in rows
        ]
        base = max((m[3] for m in metas), default=0) or 12.0
        out: list = []
        prev = None
        for pno, top, line, size in metas:
            if prev is not None:
                ppno, ptop, psize = prev
                # A gap wider than the line pitch at the *previous* line's size
                # is a paragraph break in the reporter's rhythm (8pt syllabus:
                # ~10.4pt pitch vs ~16.4pt between holdings; 11pt procedural
                # history: ~12.3 vs ~18.2). A page turn breaks it too.
                if pno != ppno or (top - ptop) > 1.35 * max(psize, 8.0):
                    if out and out[-1] != "":
                        out.append("")
            prev = (pno, top, size)
            out.append(
                {
                    "__hm__": True,
                    "html": self.line_inline_text(line),
                    "rel": round(size / base, 3),
                    "align": self._measure_align(line),
                }
            )
        return out

    def _split_syllabus(self, doc) -> None:
        """Move the styled reporter matter built in ``extract_headmatter`` out
        of ``summary`` into ``syllabus``. Overrides the family base's text
        match on a bare 'Syllabus' row, which both loses the styling and misses
        the bound reporter's syllabus-less per curiam front matter."""
        rows = getattr(self, "_conn_reporter", None)
        if not rows:
            return
        doc.syllabus = list(rows)
        doc.summary = list(doc.summary or [])[: -len(rows)]
