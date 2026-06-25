"""Supreme Court of the United States ('scotus').

Slip-opinion structure, section by section:

* Page 1: the Reporter's small-print NOTE (7pt — a notice, dropped and
  recorded), the 'SUPREME COURT OF THE UNITED STATES' banner with the case
  line, 'CERTIORARI TO ...', and 'No. NN–NNN. Argued ... Decided ...' —
  that cover is the document headmatter.
* The Syllabus: runs as long as the running head at the top of each page
  says 'Syllabus'; extracted into ``doc.syllabus`` (its own section, not
  opinion body), paragraph-grouped by the first-line indent.
* Each writing — opinion of the Court, every concurrence and dissent —
  opens on its own fancy first page: a 7pt revision NOTICE (notice,
  dropped+recorded), the banner / docket / caption / 'ON WRIT OF ...' /
  '[date]' cover, then the byline. The writing starts at the TOP of that
  page (the cover belongs to it; nothing is dropped), and the byline
  supplies the author and opinion type — including wrapped 'JUSTICE ALITO,
  with whom THE CHIEF JUSTICE and JUSTICE KAVANAUGH join, dissenting.'

Furniture and geometry:

* Running heads sit at y≈115/139 ('(Slip Opinion) OCTOBER TERM, 2025 1',
  '2 BERK v. CHOY', 'Cite as: 607 U. S. ___ (2026) 5', and the center
  section label). They are dropped by position and recorded; the label
  drives the Syllabus boundary, and the PRINTED page number (slip numbering
  restarts for each writing) replaces the PDF page index on every block.
* 9pt body, lines lead ~13.2pt, indented quotes ~10.8pt; the footnote rule
  is a row of em-dashes drawn as text, not a graphic.
"""

from __future__ import annotations

from ._reversedjustice import _KIND_ENDINGS, ReversedJusticeSupreme

_SECTION_LABELS = ("Syllabus", "Opinion of the Court", "Per Curiam")
_BYLINE_OPENERS = ("JUSTICE", "CHIEF JUSTICE", "THE CHIEF JUSTICE", "PER CURIAM")


class SupremeCourtUS(ReversedJusticeSupreme):
    court_id = "scotus"
    court_label = "Supreme Court of the United States."

    _HEAD_BAND = 150.0  # running heads at y≈115/139; content starts y≈158
    # 9pt body: lines lead ~13.2pt, block quotes ~10.8pt.
    gap_tight_max = 9.5
    gap_single_max = 12.4
    gap_double_max = 28
    # Body baseline x≈156.2 with an ~11pt paragraph indent.
    body_baseline_x0 = 156.0
    para_indent_min = 8

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path):
        self._head_dropped = []
        self._notice_dropped = []
        self._page_label = {}
        self._page_printed = {}
        self._authors = {}
        self._covers = {}  # op_start (top) → byline segment index for i>0 writings
        self._syllabus_rows = []
        doc = super().extract(pdf_path)
        if self._syllabus_rows:
            doc.syllabus = self._syllabus_rows
        extra = list(dict.fromkeys(self._notice_dropped + self._head_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        self._remap_printed_pages(doc)
        return doc

    def _remap_printed_pages(self, doc):
        """Blocks carry the slip's PRINTED page number (which restarts for
        each writing), not the PDF page index."""
        mapping = self._page_printed
        if not mapping:
            return
        marker = '<pagenumber value="'
        for op in doc.opinions:
            for b in op.blocks:
                if b.page in mapping:
                    b.page = mapping[b.page]
                if marker in (b.text or ""):
                    parts = b.text.split(marker)
                    out = [parts[0]]
                    for rest in parts[1:]:
                        i = rest.find('"')
                        if i > 0 and rest[:i].isdigit():
                            n = int(rest[:i])
                            out.append(marker + str(mapping.get(n, n)) + rest[i:])
                        else:
                            out.append(marker + rest)
                    b.text = "".join(out)

    # ---------------------------------------------------- page furniture
    def page_lines(self, page):
        lines = super().page_lines(page)
        for attr in ("_head_dropped", "_notice_dropped"):
            if getattr(self, attr, None) is None:
                setattr(self, attr, [])
        kept, head_texts = [], []
        for ln in lines:
            if ln["top"] < self._HEAD_BAND:
                txt = self.line_plain_text(ln).strip()
                if txt:
                    head_texts.append(txt)
                    self._head_dropped.append(txt)
                continue
            txt0 = self.line_plain_text(ln).strip()
            if len(txt0) >= 4 and all(c in "—–-" for c in txt0):
                continue  # the footnote rule, drawn as text
            size, _f, _b = self.line_meta(ln)
            if size <= 7.5 and ln["top"] < 230 and any(c.isalpha() for c in txt0):
                # The Reporter's NOTE / the revision NOTICE — small-print
                # notices, always in the cover region. (Small-caps body text
                # can read as 7pt-dominant — 'JUSTICE SOTOMAYOR' — so the
                # drop is position-bound; underscore rules stay separators.)
                if txt0:
                    self._notice_dropped.append(txt0)
                continue
            kept.append(ln)
        self._record_head(page.page_number, head_texts)
        return kept

    def _record_head(self, pno: int, head_texts: list) -> None:
        """The running head carries the section label (center line) and the
        printed page number (edge of the first line)."""
        label = None
        for t in head_texts:
            if t in _SECTION_LABELS or "dissent" in t.lower() or "concurr" in t.lower():
                label = t
                break
        if label is not None:
            self._page_label[pno] = label
        for t in head_texts:
            toks = t.split()
            digits = [w for w in toks if w.isdigit() and len(w) <= 3]
            if digits:
                self._page_printed[pno] = int(digits[-1])
                break

    def detect_footnote_label(self, line):
        label = super().detect_footnote_label(line)
        if label is not None:
            return label
        # An unnumbered asterisk footnote ('*JUSTICE JACKSON says ...').
        chars = line.get("chars") or []
        if chars and (chars[0].get("text") or "") == "*":
            return "*"
        return None

    def find_footnote_separator(self, page):
        """The slip footnote rule is a short em-dash run drawn as TEXT."""
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        best = None
        for line in page.extract_text_lines():
            t = (line.get("text") or "").strip()
            if (
                len(t) >= 4
                and all(c in "—–-" for c in t)
                and line["top"] > page.height * 0.4
                and line["x0"] < page.width * 0.4
            ):
                if best is None or line["top"] < best:
                    best = line["top"]
        return best

    # ------------------------------------------------------------ writings
    def find_authors(self, all_segments) -> list:
        byline_idx = super().find_authors(all_segments)
        self._authors = {}
        claimed = {all_segments[b][0]: b for b in byline_idx}
        # Supplement: a wrapped byline whose continuation line carries no
        # JUSTICE prefix — 'JUSTICE JACKSON, with whom JUSTICE SOTOMAYOR
        # joins,' / 'dissenting.', hyphenated 'con-' / 'curring in the
        # judgment.' — is invisible to the line parser. Detect it from the
        # page's opening lines (a consolidated-case cover stacks two
        # captions, so the byline can sit ~21 lines down) and accept only if
        # the assembled clause actually parses as a byline.
        pages: dict = {}
        for j, (pno, seg, _k) in enumerate(all_segments):
            pages.setdefault(pno, []).append(j)
        for pno, idxs in pages.items():
            if pno in claimed:
                continue
            lines = [
                (j, self.line_plain_text(l).strip())
                for j in idxs
                for l in all_segments[j][1]
            ][:24]
            for k, (j, t) in enumerate(lines):
                if not t.upper().startswith(_BYLINE_OPENERS):
                    continue
                texts = [x for _j, x in lines[k:]]
                clause, used = self._assemble_byline(texts)
                if clause and self.parse_author_line(clause) is not None:
                    claimed[pno] = lines[k + used][0]
                break
        starts = []
        for i, pno in enumerate(sorted(claimed)):
            b = claimed[pno]
            top = b
            while top > 0 and all_segments[top - 1][0] == pno:
                top -= 1
            if i == 0:
                # The FIRST writing starts at its byline — its cover page
                # (banner / docket / caption / [date]) is the document
                # headmatter. Later writings start at the top of their own
                # fancy first page so those segments are claimed; the cover
                # content is dropped in build_opinion.
                starts.append(b)
                self._authors[b] = self._page_byline(all_segments, top, b)
            else:
                starts.append(top)
                self._authors[top] = self._page_byline(all_segments, top, b)
                self._covers[top] = b  # cover runs from top to b-1; body starts at b
        return starts

    @staticmethod
    def _assemble_byline(texts) -> tuple:
        """Join up to 5 lines starting at the byline opener into one clause:
        hyphenated wraps rejoin ('con-' + 'curring'), and a kind-ending only
        closes the clause when the NEXT line doesn't continue it lowercase
        ('... concurring in part and' / 'dissenting in part.'). Returns
        (clause, lines_used) or (None, 0) if the clause never closes."""
        out = ""
        for i, t in enumerate(texts[:5]):
            if out.endswith("-"):
                out = out[:-1] + t
            else:
                out = f"{out} {t}".strip()
            if t.rstrip().lower().endswith(_KIND_ENDINGS):
                nxt = texts[i + 1].lstrip() if i + 1 < len(texts) else ""
                if nxt[:1].islower():
                    continue
                return out, i
        return None, 0

    def _page_byline(self, all_segments, top, b) -> str:
        """The full byline text: from the first JUSTICE/PER CURIAM line on
        the page through the line that closes the byline clause."""
        texts = []
        for j in range(top, b + 1):
            for l in all_segments[j][1]:
                texts.append(self.line_plain_text(l).strip())
        start = next(
            (k for k, t in enumerate(texts) if t.upper().startswith(_BYLINE_OPENERS)),
            None,
        )
        if start is None:
            return texts[-1] if texts else ""
        clause, _used = self._assemble_byline(texts[start:] + [""])
        return clause or " ".join(texts[start:]).strip()

    def split_author_line(self, line):
        # The start line is the cover banner; it stays in the body, the
        # author comes from the page's byline.
        return "", [line]

    def build_opinion(self, op_start, op_end, **kw):
        # For i>0 writings the opinion is claimed from the top of its cover
        # page, but the cover content (banner/docket/caption/date) is the
        # same boilerplate as the first-opinion headmatter — drop it and
        # start the body at the byline segment.
        byline_seg = getattr(self, "_covers", {}).get(op_start)
        if byline_seg is not None:
            all_segs = kw.get("all_segments", [])
            for j in range(op_start, byline_seg):
                for ln in all_segs[j][1]:
                    txt = self.line_plain_text(ln).strip()
                    if txt:
                        self._notice_dropped.append(txt)
            body_start = byline_seg
        else:
            body_start = op_start
        op = super().build_opinion(body_start, op_end, **kw)
        author = getattr(self, "_authors", {}).get(op_start)
        if author:
            op.author = author
            r = self.parse_author_line(author)
            op.type = self.normalize_opinion_type(r[2] if r else None)
        return op

    # ------------------------------------------------------ paragraph types
    def classify_paragraph(self, lines) -> str:
        """A paragraph where every line sits well inside the body column (all
        x0 > indent_min and at least two lines) is an indented block-quote."""
        if len(lines) < 2:
            return "p"
        seg_left = min(l["x0"] for l in lines)
        indent_min = self.body_baseline_x0 + self.para_indent_min
        return "blockquote" if seg_left > indent_min else "p"

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """The headmatter is the FIRST OPINION PAGE's cover (banner / docket
        / caption / 'ON WRIT OF ...' / '[date]'). Everything on the
        Syllabus-labeled pages — the slip cover and the syllabus itself —
        is the syllabus section."""
        hm_segs, syl_lines = [], []
        for seg in headmatter_segs:
            if not seg:
                continue
            chars = seg[0].get("chars") or []
            pno = (chars[0].get("page_number") if chars else None) or 1
            if self._page_label.get(pno) == "Syllabus":
                syl_lines.extend(seg)
            else:
                hm_segs.append(seg)
        self._syllabus_rows = self._syllabus_paragraphs(syl_lines)
        return self._styled_headmatter(hm_segs, page1_rules)

    def _syllabus_paragraphs(self, lines) -> list:
        """Styled syllabus rows.

        The cover section (SUPREME COURT banner through the docket/date line
        "No. NNN–NNN. Argued … Decided …") renders each line as its own
        centered row.  Everything after groups into paragraphs: a line whose
        x0 is off the continuation margin (> 4pt) starts a new paragraph,
        matching the same logic used for the opinion body."""
        from collections import Counter

        body = [l for l in lines if self.line_plain_text(l).strip()]
        if not body:
            return []

        # Continuation margin = most common x0 across all lines; body lines
        # dominate because there are far more of them than cover headings.
        margin = Counter(round(l["x0"], 1) for l in body).most_common(1)[0][0]

        rows, para = [], []
        cover_done = False  # True once we have passed the docket/date line

        def gap():
            if rows and rows[-1] != "":
                rows.append("")

        def flush():
            if para:
                text = " ".join(
                    self.line_inline_text(l).strip() for l in para
                ).strip()
                if text:
                    gap()
                    rows.append(
                        {"__hm__": True, "html": text, "rel": 1.0, "align": "L"}
                    )
                del para[:]

        for l in body:
            txt = self.line_plain_text(l).strip()

            if not cover_done:
                # Render each cover line as its own centered heading row.
                gap()
                rows.append(
                    {
                        "__hm__": True,
                        "html": self.line_inline_text(l),
                        "rel": 1.0,
                        "align": "C",
                    }
                )
                # Docket/date line closes the cover: "No. 17–646. Argued …"
                if txt.startswith("No.") and any(c.isdigit() for c in txt[:20]):
                    cover_done = True
                continue

            # Body text: off-margin x0 opens a new paragraph.
            if para and abs(l["x0"] - margin) > 4:
                flush()
            para.append(l)

        flush()
        return rows
