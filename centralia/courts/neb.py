"""Nebraska Supreme Court.

Advance-sheet format: a caption, a numbered syllabus, the panel that heard the
case ('Funke, C.J., Cassel, Stacy, Papik, Freudenberg, and Bergevin, JJ.'),
then the authoring judge on its own line — a title-case surname with an
abbreviated title: 'Papik, J.' / 'Cassel, J.' / 'Funke, C.J.'. The shared
abbreviated-title base handles 'NAME, J.' once title-case surnames are allowed;
the panel line is a comma-continuation (plural 'JJ.') and is not a byline, and
the trial-court history line ('Martin, Judge. Affirmed.') uses the spelled-out
'Judge' and trails a disposition, so it is not matched either.

What is court-local here — all of it measured off the NARROW 396x612 bound
reporter sheet, whose margins (54 / 342) and 12pt indent step none of the
shared 612pt-page constants fit:

  * **The per-curiam byline is title-case** ('Per Curiam.'), not the caps 'PER
    CURIAM' the shared bases match — so without this the whole per-curiam
    opinion read as headmatter (and a per-curiam disposition read as an order
    with no opinion at all).
  * **A byline is always the first line of its paragraph.** The reporter sets
    every paragraph with a first-line indent (x0≈66) over a block margin
    (x0≈54); the 'Appeal from the District Court for Gage County, Ricky A. /
    Schreiner, Judge, on appeal thereto ...' history wraps so that its
    continuation line *opens* with a byline-shaped 'Surname, Judge,' clause.
    Requiring the indent rejects those without looking at their words.
  * **The indent ladder** (54 body / 66 paragraph / 78 quote / 90 quoted
    paragraph / ≥96 disposition, with 61 the hanging indent under a bulleted
    item) drives paragraph grouping, block quotes and dispositions.
  * **Centering is measured on this sheet's axis**, so centered section heads
    and the centered party caption are not mistaken for flush-left prose.
  * **The numbered syllabus is set with a hanging indent** — the point number is
    outdented and the wrapped lines sit deeper — so each point can be grouped
    back into one piece from geometry alone.
"""

from __future__ import annotations

from collections import Counter

from ._abbrevtitle import AbbrevTitleSupreme
from ._nebraska import NebraskaReporterStyle


class NebraskaSupreme(NebraskaReporterStyle, AbbrevTitleSupreme):
    court_id = "neb"
    court_label = "Nebraska Supreme Court."
    allow_titlecase_name = True

    # ---- the reporter's indent ladder ------------------------------------
    # The advance sheet is a NARROW bound-reporter page (396 x 612, margins 54
    # and 342), single-spaced, with two levels of indent:
    #     54  body margin              78  quoted matter
    #     66  body paragraph 1st line  90  quoted paragraph 1st line
    # so the base's 612pt-page constants (a 72pt margin, a 28pt first-line
    # indent) never fire here — every paragraph on a page merged into one
    # block. These are this sheet's real measurements.
    body_baseline_x0 = 54.0
    para_indent_min = 8.0
    # x0 at or past this is quoted matter, not body prose.
    quote_left = 76.0
    # ...and at or past THIS is the closing disposition, which the reporter
    # pushes out to the right margin so that it ENDS there ('Affirmed.' at 287,
    # 'Final order in No. S-25-145 affirmed.' at 100, 'Reversed and remanded
    # for / further proceedings.' as a two-line block at 193). The widest one
    # observed opens at 100, clear of the quote ladder's deepest rung (90).
    disposition_left = 96.0
    # The body's single leading is ~12.2pt: two centered rows that close are one
    # wrapped heading, rows further apart are two headings.
    heading_lead_max = 14.0

    # The reporter's title-case per-curiam byline, standing alone on its line.
    per_curiam_byline = "Per Curiam."
    # A byline sits at the paragraph's first-line indent (x0≈66); a wrapped
    # continuation line sits at the block margin (x0≈54). Anything left of this
    # is a continuation, never a byline.
    byline_indent_min = 60.0

    # ------------------------------------------------------------------ bylines
    def _is_per_curiam_line(self, text: str) -> bool:
        return " ".join(text.split()) == self.per_curiam_byline

    def _byline_indented(self, line) -> bool:
        """True if ``line`` starts a paragraph (so it may be a byline)."""
        return (line.get("x0") or 0.0) >= self.byline_indent_min

    def parse_author_line(self, text):
        if self._is_per_curiam_line(text or ""):
            return ("PER CURIAM", "per curiam", None)
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._is_per_curiam_line(text):
            return text, ""
        return super()._byline_split(line)

    def _byline_at(self, line) -> bool:
        # Keeps a wrapped history line from splitting its own paragraph.
        return self._byline_indented(line) and super()._byline_at(line)

    def find_authors(self, all_segments) -> list:
        return [
            i
            for i in super().find_authors(all_segments)
            if all_segments[i][1] and self._byline_indented(all_segments[i][1][0])
        ]

    # ------------------------------------------------------------------ layout
    def line_alignment(self, line, page_width) -> str:
        """Centering on a 396pt sheet.

        The base's test needs ``x0 > 100`` and a line narrower than 55% of the
        page — measurements taken from a 612pt page. On this narrower sheet a
        genuinely centered row ('Helzer Farms, LLC, appellant, v. Jason
        Allington' at 71→325, the centered section heads '(a) Justification
        Defenses Under Nebraska Law' at 90→307) is wider than that cap and can
        start left of 100, so it read as flush left. Measure centering the way
        the page sets it instead: symmetric about the measure's axis, opening
        right of the paragraph indent, and stopping short of the right margin
        (a justified body or quote line runs all the way to it)."""
        a = super().line_alignment(line, page_width)
        if a == "C":
            return a
        x0, x1 = line.get("x0"), line.get("x1")
        if x0 is None or x1 is None:
            return a
        right = page_width - self.body_baseline_x0
        if (
            # right of the deepest first-line indent, so a body or quote
            # paragraph's opening line is never a candidate
            x0 > self.body_baseline_x0 + 2 * self.para_indent_min
            and x1 < right - 4
            # the reporter centers on the measure's axis EXACTLY (every real
            # centered row measures 198.0 on this sheet); a ragged last line
            # that merely drifts near the middle is 3pt or more off
            and abs((x0 + x1) / 2 - page_width / 2) <= 2
        ):
            return "C"
        return a

    def _centered_flags(self, seg) -> list:
        """Which lines of ``seg`` are centered *headings*. A short last line of
        a quoted paragraph can land symmetric about the axis by accident; it
        shares its left edge with the justified line above it, and a heading
        never does, so that is the discriminator."""
        pw = getattr(self, "_page1_width", None) or 396.0
        raw = [self.line_alignment(ln, pw) == "C" for ln in seg]
        out = []
        for i, ln in enumerate(seg):
            c = raw[i]
            if (
                c
                and i
                and not raw[i - 1]
                and abs(seg[i - 1]["x0"] - ln["x0"]) <= 3
            ):
                c = False
            out.append(c)
        return out

    def split_body_paragraphs(self, seg) -> list:
        """Group a single-spaced run into paragraphs on the indent ladder.

        Three kinds of line live in the same run, told apart by x0 alone: body
        prose (margin 54, first line 66), quoted matter (margin 78, first line
        90) and centered section headings. A level change starts a new
        paragraph, a first-line indent starts a new paragraph, and everything
        else is a continuation — so a wrapped paragraph stays whole, a quote
        stays whole (its opening line is not orphaned from the lines it wraps
        into), and a heading that wraps to a second row stays one heading."""
        if not seg:
            return []
        centered = self._centered_flags(seg)
        paras: list = []
        prev_kind = prev_x0 = prev_top = None
        for i, line in enumerate(seg):
            x0 = line["x0"]
            if centered[i]:
                # One heading's rows sit a single line apart; a heading and the
                # sub-heading under it are set a line-and-a-half apart, which is
                # what separates '4. County Court Lacked Subject Matter
                # Jurisdiction' from '(a) Law on Title Disputes in Forcible
                # Entry and Detainer Actions'.
                kind = "head"
                first = prev_top is not None and (
                    line["top"] - prev_top
                ) > self.heading_lead_max
            elif x0 >= self.disposition_left:
                # The disposition block is set as a unit at one left edge, so
                # only a *change* of edge starts a new one.
                kind = "disp"
                first = prev_x0 is None or abs(x0 - prev_x0) > 3
            elif x0 >= self.quote_left:
                kind, first = "quote", x0 > self.quote_left + 4
            else:
                kind = "body"
                # A first-line indent (66) opens a paragraph; the shallower 61
                # is the hanging indent under a bulleted item's marker, which
                # is a continuation. The bulleted item itself hangs its marker
                # at the body margin, so the marker is what opens it.
                first = x0 > self.body_baseline_x0 + self.para_indent_min or (
                    self._begins_paragraph_block([line])
                )
            prev_x0, prev_top = x0, line["top"]
            if paras and kind == prev_kind and not first:
                paras[-1].append(line)
            else:
                paras.append([line])
            prev_kind = kind
        return paras

    # The reporter's list marker, hung at the body margin with its wrapped
    # lines indented under it ('• Because reimbursing the Humane Society was a
    # condition of / probation, ...'). Marks a paragraph start in its own
    # right — both for paragraph splitting and for the base's page-break fold.
    list_markers = ("•",)

    def _begins_paragraph_block(self, lines) -> bool:
        if not lines:
            return False
        text = (lines[0].get("text") or "").lstrip()
        return text[:1] in self.list_markers

    def classify_paragraph(self, lines) -> str:
        """A paragraph set wholly at or past the quote margin is quoted matter
        — the reporter indents it on the left and justifies it to the same
        right margin, so the base's both-margins test cannot see it."""
        tag = super().classify_paragraph(lines)
        if tag != "p" or not lines:
            return tag
        # Centered IS the reporter's heading grammar, whatever the punctuation:
        # the base's shared test rejects a heading that ends in '?' ('(b) Did
        # Jeopardy Attach Here?') and one set in plain roman title case.
        pw = getattr(self, "_page1_width", None) or 396.0
        if all(self.line_alignment(ln, pw) == "C" for ln in lines):
            return "heading"
        if not all(ln["x0"] >= self.quote_left for ln in lines):
            return tag
        # ...but the reporter also pushes the closing disposition out to the
        # right margin ('Affirmed in part, and in part dismissed.'), past the
        # quote ladder's 78/90. That is a disposition, not quoted matter.
        if all(ln["x0"] >= self.disposition_left for ln in lines):
            return tag
        return "blockquote"

    # ----------------------------------------------------------------- sections
    @staticmethod
    def _line_page(line) -> int:
        chars = line.get("chars") or []
        pno = chars[0].get("page_number") if chars else line.get("page_number")
        return pno or 1

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Route the small-type numbered syllabus to the syllabus field (grouped
        one row per point); the rest is styled headmatter.

        Same split as the family base, but the syllabus is returned as whole
        points instead of one row per source line."""
        lo, hi = self._headnote_size
        syl, hm = [], []
        for seg in headmatter_segs:
            for ln in seg:
                if not (ln.get("text") or "").strip():
                    continue
                size = self.line_meta(ln)[0]
                (syl if lo <= size <= hi else hm).append(ln)
        styled = self._styled_headmatter([hm], page1_rules)
        styled["syllabus"] = self._syllabus_points(syl, hm)
        return styled

    def _syllabus_points(self, lines, hm_lines=None) -> list:
        """The numbered 'Syllabus by the Court', one styled row per point.

        Each point carries a HANGING indent: the point number is outdented to
        the syllabus margin ('1.' at x0≈58.5, the two-digit '10.' at x0≈54) and
        every wrapped line of that point sits at the deeper text margin
        (x0≈72). So the deepest recurring x0 is the continuation margin, and any
        line left of it opens a new point. Grouping there keeps a point whole —
        its bold topic heading ('3. Divorce: Property Division.') joined to its
        prose rather than split mid-phrase across rows — and preserves inline
        bold/italic and the type's true relative size."""
        if not lines:
            return []
        lines = sorted(lines, key=lambda ln: (self._line_page(ln), ln["top"]))
        cont = Counter(round(ln["x0"], 1) for ln in lines).most_common(1)[0][0]
        points: list = []
        for ln in lines:
            if not points or round(ln["x0"], 1) < cont - 2:
                points.append([ln])
            else:
                points[-1].append(ln)
        # Relative size against the headmatter's own body type, so the syllabus
        # keeps the smaller reporter face it is set in.
        hm_sizes = Counter(
            round(self.line_meta(ln)[0], 1) for ln in (hm_lines or [])
        )
        base = hm_sizes.most_common(1)[0][0] if hm_sizes else 11.0
        out = []
        for point in points:
            size = max(self.line_meta(ln)[0] for ln in point)
            out.append(
                {
                    "__hm__": True,
                    "html": self.paragraph_text(point),
                    "rel": round(size / base, 3) if base else 1.0,
                    "align": "L",
                }
            )
        return out

    # ------------------------------------------------------------------- tables
    def build_opinion(self, op_start, op_end, **kw):
        """Keep a drawn table that owns a WHOLE page.

        The base collects an opinion's pages from its text segments, so a page
        whose only content is a ruled table (Prososki's three-page chart of
        fabricated citations — every line of page 11 sits inside the table's
        bbox, so the page contributes no segment) is absent from that set and
        its table is never emitted as a block. Re-insert, in page order, any
        table drawn on a page inside this opinion's page span."""
        op = super().build_opinion(op_start, op_end, **kw)
        all_segments = kw.get("all_segments") or []
        tables_by_page = kw.get("tables_by_page") or {}
        pages = [p for p, seg, _ in all_segments[op_start:op_end] if seg]
        if not pages or not tables_by_page:
            return op
        placed = {b.page for b in op.blocks if b.kind == "table"}
        from ..models import Block

        for pno in range(min(pages), max(pages) + 1):
            if pno in placed:
                continue
            for tbl in tables_by_page.get(pno, []):
                block = Block(
                    kind="table", page=pno, payload={"rows": tbl.get("rows") or []}
                )
                at = next(
                    (
                        i
                        for i, b in enumerate(op.blocks)
                        if b.page is not None and b.page > pno
                    ),
                    len(op.blocks),
                )
                op.blocks.insert(at, block)
        return op

    # ---------------------------------------------------------------- footnotes
    # The reporter's separator is a STROKED vector line (page.rects is empty on
    # every page of every file), one third of the 288pt measure wide, drawn on
    # the body margin: 96pt at x0=54, 478 of them across the 50 documents.
    # The type drops a full step across that rule — 11pt body above, 9pt
    # footnote below, with the raised label at 5.8pt. Measured on every thin
    # horizontal vector in the corpus, the drop separates the two populations
    # with no exceptions: all 478 96pt rules show it, and none of the 48 144pt
    # reporter/table rules does (44 have same-size text below, 4 have none).
    footnote_sep_size_drop = 1.5

    def find_footnote_separator(self, page):
        """Recover a separator the family base's bottom-half fence rejects.

        ``StateSupreme`` only considers a rule in the bottom half of the page.
        A footnote long enough to fill most of a page pushes its own separator
        up above that line, and then every footnote on the page is read as
        prose: damore p11 draws its rule at y=175 of 612 (footnotes 34-36),
        cyboron p13 at y=261 (22-27), prososki p27 at y=224. Nine such rules
        across eight of the 50 documents.

        Position is not what makes a rule a separator. What makes it one is the
        TYPE DROPPING ACROSS IT — the last line above is body, the first line
        below is footnote — which is measurable on the page itself and needs no
        constant. Reading the body size off the line above also sidesteps the
        page's modal glyph size, which on exactly these footnote-heavy pages
        reports the footnote's 9pt as the body (damore p11: 2,447 glyphs at 9pt
        against 241 at 11pt).

        The family base runs first and always wins, so no page it already
        resolves can move; this only fills in where it returned nothing.
        """
        found = super().find_footnote_separator(page)
        if found is not None:
            return found
        chars = [c for c in page.chars if not (c.get("text") or "").isspace()]
        if not chars:
            return None
        min_w = self.footnote_sep_min_width(page)
        x0_max = self.footnote_sep_x0_max or page.width * 0.25
        cands = []
        for rule in list(page.rects) + list(page.lines):
            if not (
                abs(rule.get("height") or 0.0) < 2
                and (rule["x1"] - rule["x0"]) >= min_w
                and rule["x0"] < x0_max
            ):
                continue
            above = [c for c in chars if c["top"] < rule["top"] - 2]
            below = [c for c in chars if rule["top"] < c["top"] < rule["top"] + 22]
            if not above or not below:
                continue
            # The body's size, read off the line that sits directly on the rule.
            last_top = max(c["top"] for c in above)
            body = max(
                (c.get("size") or 0.0)
                for c in above
                if abs(c["top"] - last_top) < 3
            )
            top_below = min(below, key=lambda c: c["top"])
            if body - (top_below.get("size") or 0.0) >= self.footnote_sep_size_drop:
                cands.append(rule["top"])
        if not cands:
            return None
        sep = min(cands)
        # Same guard the family base applies: a rule with an opinion byline
        # printed under it is an opinion divider, and treating it as a footnote
        # zone would swallow that writing.
        for line in page.extract_text_lines():
            if line.get("top", 0) > sep and self.parse_author_line(
                (line.get("text") or "").strip()
            ):
                return None
        return sep

    # ---------------------------------------------------------------- residuals
    def _sweep_residual(self, doc, source_pages):
        """Surface the recorded running header BEFORE the completeness sweep.

        ``NebraskaReporterStyle`` strips the five-line running band in
        ``page_lines`` and stashes the text on ``self._neb_dropped``, but it only
        copies that onto ``doc.dropped`` after ``extract()`` returns — i.e. after
        the sweep has already run. The sweep therefore saw the running case name
        and the 'Cite as ...' line on every page as unplaced *content*. Hand the
        stash over here (and empty it, so the family base's post-pass has nothing
        left to append twice)."""
        stash = getattr(self, "_neb_dropped", None)
        if stash:
            have = set(doc.dropped or [])
            doc.dropped = list(doc.dropped or []) + [
                t for t in dict.fromkeys(stash) if t not in have
            ]
            self._neb_dropped = []
        super()._sweep_residual(doc, source_pages)
