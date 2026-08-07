"""Supreme Court of Ohio.

Byline is a bold abbreviated-title line ('DEWINE, J.' / 'BRUNNER, J.,
concurring in judgment only.'). A non-bold authorship summary ('DEWINE, J.,
authored the opinion of the court, which ...') and a sitting-by-designation
line ('HENSAL, J., of the Ninth District Court of Appeals, sat for DETERS, J.')
both start with the bold surname but continue with a comma clause, so the
bold requirement plus the comma-continuation rule exclude them.

Two document styles in the corpus:

  * SLIP OPINIONS (45 files) — 'NOTICE / This slip opinion is subject to formal
    revision …', then 'SLIP OPINION NO. …', the case-name banner, the bracketed
    citation form, the reporter's italic subject line, '(No. … ―Submitted …
    ―Decided ….)', 'APPEAL from …', a rule, the vote/authorship roster, a second
    rule, then the '{¶ N}'-numbered body under an abbreviated-title byline.
  * CLERK ORDERS (5 files: resignations, reinstatement) — the same caption
    anatomy but with NO notice block and, more importantly, NO byline at all.
    The '{¶ 1}' paragraph after the caption's closing rule opens an unsigned
    per-curiam ruling, and the roster ('KENNEDY, C.J., … concur.') follows it.

Page furniture and front matter, tuned here:
  * the top-margin running head is whatever sits above the body block — the
    bracketed cite on page 1 ('[Cite as …]' / '[Until this opinion appears in
    the Ohio Official Reports …]', which may wrap) and 'SUPREME COURT OF OHIO' /
    '<Month> Term, <year>' on continuation pages. It is a margin position, not a
    phrase, so all three forms are caught the same way — and each is RECORDED,
    not silently deleted. The bottom page number is folded out;
  * the 'NOTICE …' block is the only real notice; it goes to ``dropped``;
  * everything else in the front matter stays in the headmatter IN DOCUMENT
    ORDER, styled. It has to: the caption block, its closing rule, the roster
    and the second rule interleave, so routing part of it to another section
    reorders the page (the reporter's headnote used to be lifted into the
    syllabus, which pushed the roster above it).
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

# Ohio numbers every body paragraph with its own printed marker. It is a label
# the document supplies, so it can anchor the start of an unbylined ruling.
_PARA_MARK = "{¶"


class OhioSupreme(AbbrevTitleSupreme):
    court_id = "ohio"
    court_label = "Supreme Court of Ohio."
    require_bold_byline = True
    fold_page_numbers = True
    # Ordinary Ohio Supreme Court prose is double-spaced at ~20.7pt. Quotes
    # are tighter and indented, so the shared 22pt cutoff was tagging the
    # entire opinion as blockquotes.
    gap_single_max = 18
    blockquote_by_indent = True
    # The Ohio Supreme Court's continuation margin is x≈108; x≈144 is the
    # deeper quote edge (the shared default assumes x≈72).
    body_baseline_x0 = 108

    # Set while the styled headmatter is being measured (see ``line_meta``).
    _hm_styling = False

    def line_meta(self, line):
        """While styling the headmatter, report a line's type size as its
        LARGEST glyph rather than its most common one.

        Ohio sets the case-name banner and the justice roster in SMALL CAPS:
        the initial capitals are the line's real 12pt and the small caps are
        9.5pt, and there are more of the latter. Taking the dominant size
        reads those lines as small print — which shrank them mid-paragraph
        against their own continuation lines, and made the ordinary 20.7pt
        line pitch look like a blank row after each one. The cap height is
        the type size."""
        size, font, bold = super().line_meta(line)
        if self._hm_styling:
            chars = [
                c for c in (line.get("chars") or []) if (c.get("text") or "").strip()
            ]
            if chars:
                size = max(round(c.get("size", 0), 1) for c in chars)
        return size, font, bold

    def styled_headmatter_rows(self, rows: list) -> list:
        """Reconcile the caption's wrapped lines before they are frozen.

        Two things a per-line measurement cannot see:

        * The catchline has been lifted out into ``headnotes``, leaving a hole
          several lines deep. Close the caption up over it, or the removal
          prints as a blank row the page never had.
        * Alignment is a property of the BLOCK, not the line. Ohio's whole
          caption is centered, but its full-measure lines reach both margins
          and so measure as left-aligned — the '[Until this opinion appears …]'
          citation form came out left / centered / centered. A run of lines
          that all sit on ONE axis is one centered block; a genuinely left
          block gives itself away because its short last line sits off that
          axis."""
        gap = getattr(self, "_ohio_catchline_gap", None)
        if gap:
            pno0, top0, height = gap
            rows = [
                (pno, top - height if (pno == pno0 and top > top0) else top, x0, p)
                for pno, top, x0, p in rows
            ]
        tops = sorted(t for _p, t, _x, _pl in rows)
        pitch = min((b - a for a, b in zip(tops, tops[1:]) if b > a), default=20.7)
        run: list = []

        def close(run):
            if len(run) < 2:
                return
            centers = [(p["x0"] + p["p"]["x1"]) / 2 for p in run]
            if max(centers) - min(centers) > 6:
                return
            if not any(p["p"]["align"] == "C" for p in run):
                return
            for p in run:
                p["p"]["align"] = "C"

        prev = None
        for pno, top, x0, p in rows:
            if "x1" not in p or (
                prev is not None
                and (pno != prev[0] or (top - prev[1]) > 1.6 * pitch)
            ):
                close(run)
                run = []
            if "x1" in p:
                run.append({"x0": x0, "p": p})
                prev = (pno, top)
            else:
                prev = None
        close(run)
        return rows

    def parse_author_line(self, text):
        # Ohio's disciplinary opinions use title-case ``Per Curiam.`` rather
        # than the all-caps form recognized by the shared parser. Without this
        # opener, the entire multi-page opinion is classified as headmatter.
        if " ".join(text.replace(".", "").split()).lower() == "per curiam":
            return ("PER CURIAM", "per curiam", None)
        return super().parse_author_line(text)

    # ------------------------------------------------------------- furniture
    # The body block starts at top≈110 on continuation pages and at the caption
    # banner (top≈151) on page 1; the running head is whatever sits above that.
    running_head_max_top = 75.0

    def page_lines(self, page):
        """Lift the top-margin running head off the body and RECORD it.

        Every page carries one: the bracketed cite on page 1 ('[Cite as …]' /
        the two-line '[Until this opinion appears …]'), and 'SUPREME COURT OF
        OHIO' / '<Month> Term, <year>' alternating on continuation pages. All
        three sit alone in the top margin, well above the body block, so the
        position identifies them without matching any phrase. Filtering them
        out silently would leave the completeness sweep unable to tell them
        from content, so each one is kept for the Removed box."""
        if not hasattr(self, "_ohio_dropped"):
            self._ohio_dropped = []
        out = []
        for l in super().page_lines(page):
            if l.get("top", 0) < self.running_head_max_top:
                t = self.line_plain_text(l).strip()
                if t:
                    self._ohio_dropped.append(t)
                continue
            out.append(l)
        return out

    # --------------------------------------------------------- front matter
    @staticmethod
    def _seg_first_line(seg):
        for line in seg:
            if (line.get("text") or "").strip():
                return line
        return None

    @staticmethod
    def _line_is_catchline(line) -> bool:
        """True for a line of the reporter's subject catchline.

        The catchline is the one run of front matter set in plain ITALIC:
        'Attorneys—Misconduct—…—Public reprimand.' Everything around it is
        roman (the notice, the docket line, the appeal line, the roster) or
        BOLD italic (the bracketed citation form, whose case name is italic
        inside a bold banner), so the face alone identifies it — no phrase
        matching. Judge on letters: the em-dashes and section numbers between
        topics are routinely left in the roman face."""
        chars = [c for c in (line.get("chars") or []) if (c.get("text") or "").strip()]
        if not chars:
            return False
        if any("Bold" in (c.get("fontname") or "") for c in chars):
            return False
        letters = [c for c in chars if (c.get("text") or "").isalpha()]
        return bool(letters) and all(
            "Italic" in (c.get("fontname") or "") or "Oblique" in (c.get("fontname") or "")
            for c in letters
        )

    def _split_catchline(self, headmatter_segs) -> tuple:
        """(kept segments, catchline lines).

        Takes the FIRST contiguous run of italic front-matter lines — the
        reporter's topical subject line, which belongs in its own section
        rather than in the caption. Also records the vertical span it left
        behind so the caption's rhythm can be closed up over the hole."""
        kept, run, done = [], [], False
        for seg in headmatter_segs:
            keep_seg = []
            for line in seg:
                if not done and self._line_is_catchline(line):
                    run.append(line)
                    continue
                if run and not done:
                    done = True  # the run has ended; later italics are not it
                keep_seg.append(line)
            kept.append(keep_seg)
        if run:
            tops = [l["top"] for l in run]
            pitch = min(
                (b - a for a, b in zip(tops, tops[1:]) if b > a), default=20.7
            )
            chars = run[0].get("chars") or []
            pno = (chars[0].get("page_number") if chars else None) or 1
            self._ohio_catchline_gap = (pno, tops[0], (tops[-1] - tops[0]) + pitch)
        return [s for s in kept if s], run

    def _split_notice(self, headmatter_segs) -> tuple:
        """(kept segments, notice texts).

        The publication advisory opens with the centered one-word 'NOTICE'
        heading; its prose runs on at the notice's own inset margin and — being
        set a whole line-space apart — lands in following segments. The block
        closes at the first BOLD segment, which is the reporter's caption
        ('SLIP OPINION NO. …' / the case-name banner). A clerk order prints no
        notice at all, so nothing is taken from it."""
        keep, notice, in_notice = [], [], False
        for seg in headmatter_segs:
            first = self._seg_first_line(seg)
            if first is None:
                keep.append(seg)
                continue
            text = (first.get("text") or "").strip()
            if in_notice and self.line_meta(first)[2]:  # bold ends the notice
                in_notice = False
            elif text == "NOTICE":
                in_notice = True
            if not in_notice:
                keep.append(seg)
                continue
            notice.append(
                " ".join(
                    (ln.get("text") or "").strip()
                    for ln in seg
                    if (ln.get("text") or "").strip()
                )
            )
        return keep, notice

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Route the publication notice to ``dropped``, lift the reporter's
        italic subject catchline into ``headnotes``, and keep the rest of the
        front matter as styled headmatter in document order."""
        keep, notice = self._split_notice(headmatter_segs)
        keep, catchline = self._split_catchline(keep)
        self._hm_styling = True
        try:
            d = self._styled_headmatter(keep, page1_rules)
        finally:
            self._hm_styling = False
        d["syllabus"] = []
        d["headnotes"] = self._catchline_rows(catchline)
        if notice:
            d["dropped"] = list(d.get("dropped") or []) + notice
        return d

    def _catchline_rows(self, lines) -> list:
        """The catchline is one sentence of em-dash-separated topics that wraps
        over several printed lines — one logical unit, so it is returned as one
        row. A wrap after a topic's trailing dash takes no space; an ordinary
        word wrap does."""
        if not lines:
            return []
        html, prev_text = "", ""
        for line in lines:
            piece = self.line_inline_text(line).strip()
            if not piece:
                continue
            if html and not prev_text.endswith(("—", "–", "-")):
                html += " "
            html += piece
            prev_text = self.line_plain_text(line).strip()
        # One italic sentence, not one italic run per printed line.
        html = html.replace("</em><em>", "").replace("</em> <em>", " ")
        return [{"__hm__": True, "html": html, "rel": 1.0, "align": "L"}] if html else []

    # ------------------------------------------------------------- footnotes
    def detect_footnote_label(self, line):
        """Ohio prints a footnote's label as a full-size 'N.' flush at the
        footnote block's left rail — the same 9.96pt Times as the note's prose,
        on the same baseline (state_v._turner p4: '1' at x0=108.0, size 9.96,
        y1=129.39, exactly the glyph metrics of the 'T' that follows it).

        The base detector proves a label by SUPERSCRIPTING — a first char set
        at least 1.5pt below the line's type size — and there is nothing raised
        here to see. So every note in the zone read as a continuation, and a
        document's whole footnote apparatus fused into one entry labelled '?'
        (31 of the 50 documents in the corpus, four merged notes in
        state_v._turner alone).

        Unlike South Dakota's hanging number-dot, Ohio gives the label NO
        hanging indent: the continuation lines sit at the same x0=108.0 rail.
        What identifies it is that a note's first line OPENS with a bare
        one-or-two digit integer and a period, at the rail — measured over the
        corpus, 68 footnote-zone lines match that description and every one of
        them is a real label (the labels run 1..N in order through each
        document, with no interior line matching). A wrapped citation year is
        four digits and cannot match; a mid-note line at the rail never begins
        with a numbered token."""
        if abs(line.get("x0", 9999) - self.body_baseline_x0) <= 2:
            toks = (line.get("text") or "").split()
            if toks:
                head = toks[0]
                num = head[:-1]
                if head.endswith(".") and num.isdigit() and len(num) <= 2:
                    return num
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the leading 'N.' marker off the note's text — it is the label,
        which the renderer draws in its own column, not the first word of the
        prose."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label.isdigit():
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            if stripped.startswith(label + "."):
                fn.paragraphs[0] = (tag, stripped[len(label) + 1 :].lstrip())
        return fn

    # ------------------------------------------------------------- unbylined
    def find_authors(self, all_segments) -> list:
        """An Ohio clerk order carries no byline: no 'PER CURIAM', no justice
        line — the caption's closing rule is followed straight away by '{¶ 1}'.
        Without an opener the whole order reads as headmatter and no ruling is
        returned, so fall back to the first printed paragraph marker and treat
        the ruling as per curiam. The marker is Ohio's own printed label, and
        it opens the body on every document in the corpus."""
        starts = super().find_authors(all_segments)
        self._ohio_percuriam = False
        if starts:
            return starts
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                if t.startswith(_PARA_MARK):
                    self._ohio_percuriam = True
                    return [i]
                break
        return []

    def split_author_line(self, line):
        """The unbylined order has no byline text to consume — the paragraph the
        opener points at is body, so hand it back as inline body content."""
        if getattr(self, "_ohio_percuriam", False):
            return "PER CURIAM", [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """An unbylined ruling with no publication notice is a CLERK ORDER
        (resignation, reinstatement); an unbylined ruling that DOES carry the
        notice is a per curiam slip decision, which stays an opinion."""
        if getattr(self, "_ohio_percuriam", False):
            _keep, notice = self._split_notice([s for _p, s, _k in all_segments])
            if not notice:
                from ..models import DocType

                return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path: str):
        self._ohio_dropped = []
        self._ohio_percuriam = False
        self._ohio_catchline_gap = None
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the running heads BEFORE the completeness sweep, so they are
        matched against ``doc.dropped`` instead of reported as unplaced."""
        seen, extra = set(), []
        for t in getattr(self, "_ohio_dropped", []):
            if t not in seen:
                seen.add(t)
                extra.append(t)
        if extra:
            doc.dropped = list(doc.dropped) + extra
        from ..models import DocType

        if doc.doc_type == DocType.ORDER and doc.opinions:
            doc.opinions[0].type = "order"
        super()._sweep_residual(doc, source_pages)
