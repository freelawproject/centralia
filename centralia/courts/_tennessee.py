"""Shared base for the Tennessee intermediate appellate courts (Court of
Appeals / Court of Criminal Appeals).

The page-1 layout runs caption → prose byline ('NAME, J., delivered the
opinion of the court, in which ... joined.') → counsel block → a centered
bold 'OPINION' heading where the opinion body begins. The byline and counsel
are headmatter; the byline is still the author, so ``find_authors`` locates
it, then advances the opinion start to the OPINION heading and
``build_opinion`` restores the byline as the author (re-inserting the
heading as the first body block).

A caption footnote (a superscript on a caption line, e.g. 'AT JACKSON¹')
shares page 1 with the opinion, so page ownership would hand it to the
opinion — the superscript reference in the headmatter is what anchors it,
and ``extract`` moves any footnote whose label was referenced above the
opinion start into ``headmatter_footnotes``.

The clerk's e-filing date stamp ('05/15/2026' in the page-1 top-right
corner, sometimes overprinted twice, plus its graphic) is the only
sans-serif text in the document — Arial or Helvetica at 9pt against an
all-Times body — so it is identified by font and dropped, recorded in
``dropped`` for the audit.

Page numbers ('- 4 -' or a bare '4') sit at the bottom center inside the
text margins; ``fold_page_numbers`` drops them and the cross-page paragraph
merge marks the break with a <pagenumber/> instead.

A line of glyphs the PDF maps to no unicode point ('(cid:14)e(cid:8)...' —
an embedded font with no ToUnicode table) carries no recoverable text and
is dropped as identified junk on any page.
"""

from __future__ import annotations

from ..models import Block
from ._appellate import StateAppellate

_STAMP_FONTS = ("ArialMT", "Arial", "Helvetica")

# Words a centered row never ends on unless it wraps — a dangling connective
# marks the next row as the continuation of the same line.
_CONNECTIVES = frozenset(
    ("and", "or", "of", "the", "to", "for", "in", "with", "by", "a", "an")
)


def _strip_inline(s: str) -> str:
    """Remove <...> inline markup (plain scan, no regex)."""
    out, depth = [], 0
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            if depth:
                depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


class TennesseeHeadmatter:
    """Styled, paragraph-grouped headmatter for the Tennessee caption page.

    The page is a single column: centered caption lines (court banner, session
    date, bold style-of-case, dividers, docket), then full-width prose blocks
    (syllabus paragraph, 'delivered the opinion' byline, one counsel entry per
    party). Wrapped prose is single-spaced (line gap ≈ 1.15 × font size) while
    blocks are separated by a blank line (gap ≥ 2 lines), so runs of tight,
    non-centered lines are joined into one flowing paragraph and a spacing gap
    is emitted between blocks. Centered lines keep their own row, alignment,
    relative size, and inline bold/italics; underscore rules stay dividers."""

    def parse_author_line(self, text):
        """Also read a byline whose text layer carries no spaces.

        The separate writings published as their own file set the byline with no
        space glyphs and kerning too tight for the gap-based rebuild in
        ``line_plain_text``. gary_wygant's concurrence prints its byline as
        'DWIGHT E.TARWATER,J.,concurring in part and dissenting in part.', so
        the grammar saw one long token: no author, no opinion start, and the
        whole file became headmatter (42 rows against 0 body). The two
        tenncrimapp files that never parsed at all — burrow and gordon — are the
        same shape ('KYLE A.HIXSON, J., delivered ...').

        The setting implies the spaces: a period or comma followed directly by a
        letter. Restore those and ask the grammar once more. Tried only after
        the normal parse declines, so a byline that already reads correctly is
        untouched.

        This lives on the shared headmatter mixin because both Tennessee bases
        inherit it — TennesseeSupreme does NOT inherit TennesseeAppellate, so a
        method placed on the appellate base fixed tenncrimapp and left the
        Supreme Court's own concurrences broken.
        """
        parsed = super().parse_author_line(text)
        if parsed is not None:
            return parsed
        out = []
        for i, ch in enumerate(text):
            out.append(ch)
            if ch in ".," and i + 1 < len(text) and text[i + 1].isalpha():
                out.append(" ")
        repaired = "".join(out)
        return super().parse_author_line(repaired) if repaired != text else None

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        from collections import Counter

        pw = getattr(self, "_page1_width", 612.0) or 612.0
        rows, lines = [], []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                size, _font, bold = self.line_meta(line)
                top, x0 = round(line["top"], 1), round(line["x0"], 1)
                lines.append(
                    {"text": t, "x0": x0, "top": top, "size": size,
                     "bold": bold, "page": pno}
                )
                if all(c in "_-—–" for c in t):
                    rows.append((pno, top, x0, {"divider": True}))
                    continue
                align = self.line_alignment(line, pw)
                # A wide centered line (the bold style-of-case, the rule-cite
                # disposition) reads as 'L' to the generic alignment check;
                # an indented line whose midpoint sits at page center is
                # centered.
                x1 = round(line.get("x1") or x0, 1)
                left = getattr(self, "body_baseline_x0", 72.0)
                if (
                    align != "C"
                    and x0 > left + 8
                    and abs((x0 + x1) / 2 - pw / 2) <= 8
                ):
                    align = "C"
                rows.append(
                    (pno, top, x0, {
                        "html": self.line_inline_text(line),
                        "size": size,
                        "align": align,
                    })
                )
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        sizes = [p["size"] for _, _, _, p in rows if "size" in p]
        base = Counter(round(s) for s in sizes).most_common(1)[0][0] if sizes else 12

        summary, block = [], []

        def flush():
            if not block:
                return
            if len(block) > 1 and all(p["align"] != "C" for p in block):
                # A single-spaced run of full-width lines is one wrapped
                # paragraph — join it.
                summary.append({
                    "__hm__": True,
                    "html": " ".join(p["html"] for p in block),
                    "rel": round(block[0]["size"] / base, 3),
                    "align": "L",
                })
            else:
                for p in block:
                    summary.append({
                        "__hm__": True,
                        "html": p["html"],
                        "rel": round(p["size"] / base, 3),
                        "align": p["align"],
                    })
            summary.append("")  # block spacing
            del block[:]

        prev = None  # (page, top, size, align)
        for pno, top, x0, p in rows:
            if p.get("divider"):
                flush()
                summary.append("__DIVIDER__")
                prev = None
                continue
            if prev is not None:
                same_block = (
                    pno == prev[0]
                    and (top - prev[1]) <= 1.6 * max(p["size"], prev[2])
                    and (p["align"] == "C") == (prev[3] == "C")
                )
                if not same_block:
                    flush()
            block.append(p)
            prev = (pno, top, p["size"], p["align"])
        flush()
        # A row that wraps is ONE line of the document, wherever the wrap
        # falls — within a block, across blocks, or across a page break. Two
        # tells, either suffices: the continuation opens lowercase ('...
        # Affirmed' / 'and Remanded'), or the previous row dangles
        # mid-sentence on a connective or comma ('... Reversed and' /
        # 'Remanded'; a quote ending '... no just reason for' resuming on the
        # next page). Genuine rows (banner, session, docket, counsel) open
        # upper and end on a full word. Dividers break the chain.
        merged = []
        for s in summary:
            if isinstance(s, dict) and s.get("__hm__"):
                j = len(merged) - 1
                while j >= 0 and merged[j] == "":
                    j -= 1
                prev = merged[j] if j >= 0 else None
                if isinstance(prev, dict) and prev.get("__hm__"):
                    plain = _strip_inline(s["html"]).lstrip()
                    ptext = _strip_inline(prev["html"]).rstrip()
                    ptok = ptext.rsplit(None, 1)[-1].lower() if ptext else ""
                    dangles = ptok in _CONNECTIVES or ptext.endswith((",", ";"))
                    if plain[:1].islower() or dangles:
                        prev["html"] += " " + s["html"]
                        if s["align"] == "C":
                            prev["align"] = "C"
                        del merged[j + 1 :]
                        continue
            merged.append(s)
        summary = merged
        while summary and summary[-1] == "":
            summary.pop()

        return {
            "court": self.court_label or self.court_id,
            "summary": summary,
            "headmatter_lines": lines,
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [],
        }


class TennesseeFurnitureDrop:
    """Page-furniture removal shared by all three Tennessee courts: the 9pt
    sans-serif e-filing date stamp (text + graphic) on page 1, and lines of
    unmappable '(cid:NN)' glyphs anywhere. Dropped text is recorded on the
    document's ``dropped`` list via ``extract``."""

    @staticmethod
    def _is_stamp_char(c) -> bool:
        fn = c.get("fontname") or ""
        return fn.endswith(_STAMP_FONTS) and abs(c.get("size", 0) - 9.0) < 0.1

    def extract_page_images(self, page):
        imgs = super().extract_page_images(page)
        if page.page_number != 1:
            return imgs
        # The stamp's graphic (seal + date band) sits in the top-right margin
        # above the court banner; opinion images never appear there.
        return [i for i in imgs if not (i["top"] < 100 and i["x0"] > page.width / 2)]

    def extract(self, pdf_path):
        self._stamp_dropped = []
        doc = super().extract(pdf_path)
        extra = list(dict.fromkeys(self._stamp_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
        if getattr(self, "_stamp_dropped", None) is None:
            self._stamp_dropped = []
        kept = []
        for ln in lines:
            chars = ln.get("chars") or []
            # A line of glyphs with no unicode mapping ('(cid:14)e(cid:8)...')
            # carries no recoverable text — identified junk on any page.
            n_cid = sum(1 for c in chars if (c.get("text") or "").startswith("(cid:"))
            if n_cid >= 2:
                txt = self.line_plain_text(ln).strip()
                if txt:
                    self._stamp_dropped.append(txt[:60])
                continue
            if (
                page.page_number == 1
                and chars
                and all(self._is_stamp_char(c) for c in chars)
            ):
                txt = self.line_plain_text(ln).strip()
                if txt:
                    self._stamp_dropped.append(txt)
                continue
            kept.append(ln)
        return kept


class TennesseeBlockquotes:
    """Blockquote detection for the single-spaced Tennessee body.

    Tennessee body text is itself single-spaced, so line spacing cannot
    separate a quote from prose; the structural tell is that a quote pulls
    BOTH margins in — left x0 at least ``_QUOTE_INDENT`` past the body
    baseline AND a right edge at least ``_QUOTE_RIGHT_IN`` short of the body
    right margin. (A body paragraph's indented first line shares the quote's
    left x0 but runs to the full right margin, so it stays prose.)

    Consecutive quote lines group into one blockquote; an enumerated quote
    ('1. The trial court erred ...' with hanging continuations) splits items
    where a line returns left of the run's continuation indent, and a wide
    vertical gap inside a run also splits."""

    _QUOTE_INDENT = 30
    _QUOTE_RIGHT_IN = 20

    def _is_quote_line(self, line, abs_right) -> bool:
        x0 = line["x0"]
        x1 = line.get("x1") or abs_right
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        if not (
            x0 >= self.body_baseline_x0 + self._QUOTE_INDENT
            and x1 <= abs_right - self._QUOTE_RIGHT_IN
        ):
            return False
        # A quote is anchored near the body indent; a line starting in the
        # right half of the page is a signature block or date, not a quote.
        if x0 > pw / 2:
            return False
        t = (line.get("text") or "").strip()
        # An '/s/' electronic signature is a sign-off, not a quote.
        if t.lower().startswith(("s/", "/s/")):
            return False
        # A fully uppercase line is a section heading or signature line
        # ('CONCLUSION', 'MARY L. WAGNER, JUSTICE') — quote text never is.
        alpha = [c for c in t if c.isalpha()]
        if alpha and all(c.isupper() for c in alpha):
            return False
        # A short, midpoint-centered line is a section heading ('III.
        # ANALYSIS', an italic 'The Type of Injury ...'), not quote text — a
        # quote pulls both margins in but still fills its narrowed measure.
        # ±25 matches line_alignment's centering tolerance (these courts set
        # headings up to ~18pt off true center).
        body_w = pw - 2 * self.body_baseline_x0
        if (x1 - x0) < body_w * 0.62 and abs((x0 + x1) / 2 - pw / 2) <= 25:
            return False
        return True

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        # Tennessee body is itself single-spaced, so spacing cannot identify a
        # quote here (a page-bottom gap wobble lands body lines in the
        # 'blockquote' band). Geometry does, via classify_paragraph — treat
        # spacing-detected quote segments as body.
        return "body" if kind == "blockquote" else kind

    def _abs_right(self) -> float:
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        return pw - self.body_baseline_x0

    def split_body_paragraphs(self, seg) -> list:
        if not seg:
            return []
        abs_right = self._abs_right()
        indent_min = self.body_baseline_x0 + self.para_indent_min
        # Group consecutive lines by quote-ness, then paragraph each run. An
        # ISOLATED quote-shaped line sitting at the paragraph indent is a
        # short one-line paragraph ('This timely appeal followed.'), not a
        # quote — real quotes either run deeper or come in runs.
        flags = [self._is_quote_line(l, abs_right) for l in seg]
        for i, line in enumerate(seg):
            if (
                flags[i]
                and line["x0"] <= indent_min + 16
                and not (i > 0 and flags[i - 1])
                and not (i + 1 < len(seg) and flags[i + 1])
            ):
                flags[i] = False
        runs = []
        for q, line in zip(flags, seg):
            if runs and runs[-1][0] == q:
                runs[-1][1].append(line)
            else:
                runs.append((q, [line]))
        paras = []
        for q, lines in runs:
            if not q:
                cur = [lines[0]]
                for l in lines[1:]:
                    if l["x0"] > indent_min:
                        paras.append(cur)
                        cur = [l]
                    else:
                        cur.append(l)
                paras.append(cur)
                continue
            cont = max(l["x0"] for l in lines)
            cur = [lines[0]]
            for prev, l in zip(lines, lines[1:]):
                if l["x0"] < cont - 4 or (l["top"] - prev["top"]) > self.gap_single_max:
                    paras.append(cur)
                    cur = [l]
                else:
                    cur.append(l)
            paras.append(cur)
        return paras

    def classify_paragraph(self, lines) -> str:
        abs_right = self._abs_right()
        if not lines or not all(self._is_quote_line(l, abs_right) for l in lines):
            return "p"
        # A lone line at the paragraph indent is a short paragraph, not a
        # quote (mirrors the isolated-line rule in split_body_paragraphs).
        if (
            len(lines) == 1
            and lines[0]["x0"] <= self.body_baseline_x0 + self.para_indent_min + 16
        ):
            return "p"
        return "blockquote"

    def build_opinion(self, op_start, op_end, **kw):
        op = super().build_opinion(op_start, op_end, **kw)
        # Re-join a quote continuation the segmenter stranded: a blockquote
        # block that opens lowercase directly after another blockquote is the
        # same sentence, split by a zone boundary, not a new quote.
        merged = []
        for b in op.blocks:
            plain = _strip_inline(b.text).lstrip()
            if (
                merged
                and b.kind == "blockquote"
                and merged[-1].kind == "blockquote"
                and b.page == merged[-1].page
                and plain[:1].islower()
            ):
                merged[-1].text += " " + b.text
                continue
            merged.append(b)
        op.blocks = merged
        return op


class TennesseeOpinionHeading:
    """The row the court prints where the front matter ends.

    All three Tennessee courts publish off one template: caption → case name →
    lower court → docket → summary → disposition → the prose byline (author and
    the judges who joined) → the counsel blocks → a bold, centered ``OPINION``
    → the first paragraph.  Everything above that row is headmatter; the body
    starts at it.

    The byline is what the pipeline finds, but it is NOT the boundary — the
    counsel blocks come after it.  Anchoring the opinion at the byline pulls
    the byline's own second line ('and HOLLY KIRBY, SARAH K. CAMPBELL, ... JJ.,
    joined.') and every counsel entry into the opinion body.  So: find the
    byline, keep it as the author, and advance the opinion start to the title
    row, putting the row back as the body's first block.

    The row also stands in for the byline when the grammar cannot read one at
    all.  Headmatter is *defined* as everything before the first opinion, so an
    unreadable byline does not merely cost an author — it turns the whole
    document into front matter (tennctapp/chicago_title: 8 pages, 50 headmatter
    rows, 0 body blocks).  The title row is drawn whether or not the byline
    above it parsed, so it is the anchor of last resort.

    The row is read from its SHAPE, not from the word printed on it — see
    ``_body_title_index``."""

    # The title row's shape, measured off the corpus (see _body_title_index):
    # a bold, centred, all-capital row occupying at most this share of the text
    # measure, standing clear of the row above it.
    _TITLE_WIDTH_MAX = 0.20
    # Where the row falls. Measured: page 1 in 43 files, page 2 in 47, page 3
    # in 1, never later — a rail against a document that prints no such row at
    # all, whose section heads are set the same way further down.
    _TITLE_PAGE_MAX = 3

    def find_authors(self, all_segments) -> list:
        """Anchor the body on the title row; keep the byline as the author.

        The title row is the boundary, so NOTHING above it can start an
        opinion — whatever a byline-shaped row up there says, it is front
        matter by construction. That is what settles the announcement the
        Supreme Court prints under its own byline when a separate writing
        follows ('SARAH K. CAMPBELL, J., filed a separate concurring
        opinion.'): it names a judge and a kind, so the grammar reads it as a
        second opinion, and the second start then cut the search for the title
        row short — heather_smith and ambreia_washington came out as two
        writings, the first of them holding a byline truncated mid-roster
        ('... in which JEFFREY S. BIVINS, ROGER'). The writing being announced
        is not even in the file; the court publishes it separately. A genuine
        second writing sets its byline BELOW the title row and is untouched."""
        starts = [
            i
            for i in super().find_authors(all_segments)
            if not self._is_caption_row(all_segments[i][1][0])
        ]
        self._heading_bylines = {}
        title = self._body_title_index(all_segments)
        if title is None:
            return starts
        above = [i for i in starts if i < title]
        below = [i for i in starts if i > title]
        if not above and below:
            # The title row sits above the first byline the grammar found —
            # not this template. Leave the anchor where the base put it.
            return starts
        if not starts and self._order_fallback(all_segments):
            # No byline anywhere AND the shared fallback recognises the title:
            # this is an unsigned ORDER, which is a different KIND of document,
            # not merely a body needing an anchor. Stand aside and let the
            # pipeline run that fallback, which sets doc_type and the writing's
            # type to 'order' — answering here would hand back a majority
            # opinion instead (tenn/ccd_oldsmith_henry, tenn/michael_dinovo,
            # tenncrimapp/annesha_jackson, tenncrimapp/john_ernest_rediker).
            # Only when it declines is the title row the anchor of last resort.
            return []
        right = self._text_right(all_segments)
        self._heading_bylines[title] = (
            self._byline_text(
                all_segments, self._byline_head(all_segments, above[0], right),
                title, right,
            )
            if above
            else ""
        )
        return [title] + below

    def _text_right(self, all_segments) -> float:
        """The right rail the page actually sets to, measured off the page.

        ``page width - body_baseline_x0`` is a court-wide guess; the rail is a
        fact the document states, in the right edge of every justified row it
        prints. Read it as the furthest right any full-width row reaches —
        rows at the body rail only, so a caption centred past the margin
        cannot move it."""
        left = self.body_baseline_x0
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        edges = [
            l["x1"]
            for _p, seg, _k in all_segments
            for l in seg
            if l.get("x1") and abs(l["x0"] - left) <= 2
        ]
        return max(edges) if edges else pw - left

    def _fills_measure(self, line, right) -> bool:
        """The row ran to the rail, so the row below it is the same line.

        The slack allowed is half the row's own type size — under a word's
        width, over the fraction of a point a justified row wobbles by. It has
        to be that tight. Tennessee justifies its headmatter, so a wrapped row
        lands within 0.3pt of the rail (539.8–540.1 against a 540.1 rail),
        while a roster's closing row can stop only a little short and still be
        finished: 'and JEFFREY S. BIVINS, ... JJ., joined.' ends at 517.8, and
        a percentage-of-the-measure band wide enough to be safe elsewhere (the
        base uses 6%, i.e. 28pt here) reads that as a wrap and swallows the
        counsel block behind it."""
        x1 = line.get("x1") or line["x0"]
        size = (self.line_meta(line)[0] or 12.0) if line.get("chars") else 12.0
        return x1 >= right - 0.5 * size

    def _byline_head(self, all_segments, i, right):
        """The row the byline STARTS on, when it was matched on a later one.

        A byline long enough to wrap is set as two rows, and the grammar reads
        both — but the base keeps only the second, because a byline with no
        opinion body before the next byline is taken for a sign-off, and the
        first row has only the second row beneath it. So the author comes out
        as the tail of its own roster: tennctapp/nicole_marie_beach reported
        'JR., C.J. and THOMAS R. FRIERSON, II, J., joined.' and
        tennctapp/michael_tomlin 'CLEMENT, JR., C.J. and ANDY D. BENNETT, J.,
        joined.', losing the judge who actually wrote each one.

        Walk back over the rows the byline wrapped onto: same page, same left
        rail, the row above filling the measure (so it is a wrap, not a
        finished line), and reading as a byline itself. Counsel entries sit at
        the same rail directly below and are the thing to not swallow; none of
        them answers the byline grammar, so the last test holds the line."""
        while i > 0:
            _prev_pg, prev, _pk = all_segments[i - 1]
            cur_pg, cur, _ck = all_segments[i]
            if not prev or not cur or _prev_pg != cur_pg:
                break
            if abs(prev[0]["x0"] - cur[0]["x0"]) > 2:
                break
            if not self._fills_measure(prev[-1], right):
                break
            if not self.parse_author_line(self.line_plain_text(prev[0]).strip()):
                break
            i -= 1
        return i

    def _is_caption_row(self, line) -> bool:
        """A caption row, not a byline — told apart by how each is set.

        The case history names the judge below ('No. 22-1103-IV Mary L.
        Wagner, Judge', 'Carlyn L. Addison, Judge'), and once the word breaks
        in it are recovered it answers the byline grammar as well as any
        author line does. Nothing in the WORDS separates them, but the page
        sets them differently and always has: every caption row here is bold
        and centered, and every byline is roman and flush to the body rail.
        So read the setting."""
        _size, _font, bold = self.line_meta(line)
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        return bool(bold) and self.line_alignment(line, pw) == "C"

    def _byline_text(self, all_segments, first, stop, right):
        """The byline paragraph — the author, and the roster that finishes it.

        Read ROW BY ROW, not segment by segment. The byline is one paragraph
        among several set the same way at the same rail, and the segmenter
        does not always cut between them: on tennctapp/chicago_title the
        byline, the two counsel entries and the amicus entry arrive as a
        single segment, so taking whole segments put 1,013 characters of
        appearances into ``author`` on 33 of the 110 files. The Supreme Court,
        meanwhile, sets the SAME byline as two segments ('... in which JEFFREY
        S. BIVINS, C.J.,' / 'and HOLLY KIRBY, ... JJ., joined.'), so stopping
        at the segment edge is equally wrong. Segment boundaries simply do not
        line up with this paragraph; rows do.

        Where the paragraph ends is a question the page answers. A row that
        filled the measure had nowhere to put the next word, so the row below
        continues it; a row that stopped short ended its paragraph, and what
        follows is the next one — the first counsel entry. Punctuation is kept
        as a second tell for a row that stops short but breaks off unfinished,
        on a comma or a connective ('... in which JEFFREY S. BIVINS, C.J.,')."""
        lines = [l for k in range(first, stop) for l in all_segments[k][1]]
        parts, prev = [], None
        for line in lines:
            text = self.line_plain_text(line).strip()
            if not text:
                continue
            if parts:
                tail = parts[-1].rsplit(None, 1)[-1].lower() if parts[-1] else ""
                dangles = parts[-1].endswith((",", ";")) or tail in _CONNECTIVES
                if not (dangles or self._fills_measure(prev, right)):
                    break
            parts.append(text)
            prev = line
        return " ".join(parts).strip()

    def _body_title_index(self, all_segments):
        """The title row, read from its SHAPE — no list of titles anywhere.

        The court announces the body with a row set unlike anything around it:
        bold, centred, in capitals, a fifth of the measure or less, standing
        clear of the row above. That is what it IS; ``OPINION`` is only what it
        happens to say, and a word list would have to grow the day a file says
        ``OPINION ON REHEARING`` or ``ORDER AND OPINION``.

        Measured over the 104 born-digital Tennessee files. 93 print such a
        row; the shape above finds 91 of them, picks a wrong row in none, and
        fires on none of the 11 files that print no title row at all. Every
        test earns its place against a specific rival population:

        * WIDTH — the anchor runs 46.8-70.4pt against a 468pt measure (10-15%);
          the ceiling is set at 20% so a longer title still clears it, and the
          rival it holds off is the caption itself ('IN RE JADEN H.' at 24%).
        * GAP — a caption that WRAPS leaves its tail alone on a row that is
          bold, centred, capital and short ('CENTER', 'FUND', 'LLC ET AL.').
          Every one of them sits 16.1pt under its own first line, single
          spacing on this page; every anchor sits 26.9pt or more clear. So the
          court's own line spacing separates them, read from the document's
          measured ``gap_single_max`` rather than a number chosen here.
        * BOLD — the section heads below ('ANALYSIS', 'II.') answer every
          other test, and the FIRST-match rule is what keeps them out. That
          holds only while nothing above the real anchor answers too, and
          berkeley_research_group sets 'I.' in roman directly under its
          OPINION row. Bold is the difference. Its price is the two files that
          set the anchor itself in roman — tenncrimapp/j.p._burrow_jr. and
          .../victor_gordon — which find no anchor and fall back to the byline.
        * PAGE — the row is on page 1, 2 or 3 and never later, so a document
          that prints none cannot match a section head deep in its body.

        Only the segment's first line is read: the heading shares its segment
        with the section head below it on some files ('OPINION' / 'I. FACTUAL
        AND PROCEDURAL HISTORY' are consecutive centred rows)."""
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        measure = pw - 2 * self.body_baseline_x0
        prev = None
        for i, (page_no, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            line = seg[0]
            gap = line["top"] - prev[1]["top"] if prev and prev[0] == page_no else None
            prev = (page_no, seg[-1])
            if page_no > self._TITLE_PAGE_MAX:
                continue
            text = self.line_plain_text(line).strip()
            letters = [c for c in text if c.isalpha()]
            if not letters or not all(c.isupper() for c in letters):
                continue
            width = (line.get("x1") or line["x0"]) - line["x0"]
            if width > self._TITLE_WIDTH_MAX * measure:
                continue
            if gap is not None and gap <= self.gap_single_max:
                continue
            _size, _font, bold = self.line_meta(line)
            if bold and self.line_alignment(line, pw) == "C":
                return i
        return None

    def build_opinion(self, op_start, op_end, *, all_segments, **kw):
        op = super().build_opinion(op_start, op_end, all_segments=all_segments, **kw)
        byline = getattr(self, "_heading_bylines", {}).get(op_start)
        if byline is not None:
            # super() consumed the heading segment as the author line; the
            # real author is the prose byline left behind in the headmatter,
            # and the heading goes back as the opinion's first block.
            heading = op.author.strip() or "OPINION"
            op.author = byline
            op.blocks.insert(
                0,
                Block(
                    kind="p",
                    text=f"<strong>{heading}</strong>",
                    page=all_segments[op_start][0],
                ),
            )
        return op


class TennesseeCriteria:
    """The headmatter, read into ``doc.criteria``.

    All three courts publish off one template and print it in one fixed order,
    so the headmatter is read POSITIONALLY, the way scotus reads its bench
    opinions, rather than by recognising each row's shape one at a time:

        IN THE SUPREME COURT OF TENNESSEE            the court
        AT NASHVILLE                                 where it sat
        February 12, 2025 Session                    when it heard the case
        STATE OF TENNESSEE V. SHANESSA L. SOKOLOSKY  the style of case, in caps
        Appeal by Permission from the Court of ...   how the case got here
        Criminal Court for Smith County              the court below
        No. 2017-CR-11 Brody Kane, Judge             its docket, and its judge
        No. M2022-00873-SC-R11-CD                    THIS court's docket
        <one paragraph>                              the summary
        Tenn. R. App. P. 11 Appeal by Permission;    the disposition
            Judgment ... Reversed; Case Remanded
        MARY L. WAGNER, J., delivered ... joined.    the byline
        Comer L. Donnell, District Public ...        counsel, one per party
        Jonathan Skrmetti, Attorney General ...

    Two landmarks carry the whole reading, and both are facts about the page
    rather than guesses about the words:

    * THE DOCKET ROWS divide it. Every one of the 104 born-digital Tennessee
      files prints exactly two rows opening 'No.'/'Nos.' — the court below's
      and this court's, in that order — and nothing below the second one is
      caption. So the second docket row is the caption's floor, which is what
      makes the reading survive the files where the style of case is set wide
      enough to read as flush-left rather than centred (pharma_conference,
      robert_l._trentham) and the boundary cannot be taken from alignment.

    * ALIGNMENT divides what is left. Below the docket the court centres the
      disposition and sets the summary, the byline and the appearances full
      width, so the centred run between two full-width ones IS the
      disposition — no vocabulary of dispositions is needed, and Tennessee's
      ('Tenn. R. App. P. 11 Appeal by Permission; ...', 'Tenn. Code Ann.
      § 16-3-201(d); ...', 'Tenn. Sup. Ct. R. 10B Interlocutory Appeal; ...')
      would need a wide one.

    Within the caption the style of case is told from everything around it by
    CASE: the court sets it in capitals and sets nothing else there that way.

    What the reader cannot place, it does not publish. An unsigned order
    (tenncrimapp/annesha_jackson) prints no summary, no disposition, no byline
    and no appearances, and comes back with the four fields it does print."""

    # A judicial title closes the row that names a judge — the court below's
    # judge sits on the docket row ('No. 21C184 Thomas W. Brothers, Judge') or
    # on one of its own ('Carlyn L. Addison, Judge'). Measured over the corpus,
    # the closing word is one of these five and never anything else.
    _JUDICIAL_TITLES = frozenset(
        ("judge", "judges", "chancellor", "chancellors", "commissioner")
    )
    _DOCKET_OPENERS = ("no.", "nos.")
    # Name suffixes travel with the name they follow; every other all-caps
    # fragment in a byline is either a judge or an abbreviated title.
    _NAME_SUFFIXES = frozenset(("jr", "sr", "ii", "iii", "iv", "v"))

    parse_criteria_enabled = False

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        if self.parse_criteria_enabled:
            self._read_criteria(doc)
        return doc

    # ------------------------------------------------------------- row text
    def _crit_text(self, row) -> str:
        """A headmatter row as TEXT — markup out, footnote references out.

        A footnote reference is a pointer, not part of what the row says: the
        session row 'Assigned on Briefs June 25, 2025<footnotemark>1</...>'
        otherwise yields the date 'June 25, 20251'."""
        if not isinstance(row, dict) or not row.get("__hm__"):
            return ""
        html, out, i = row.get("html") or "", [], 0
        while i < len(html):
            if html.startswith(self._MARK_OPEN, i):
                end = html.find(self._MARK_CLOSE, i)
                if end != -1:
                    i = end + len(self._MARK_CLOSE)
                    continue
            out.append(html[i])
            i += 1
        return " ".join(_strip_inline("".join(out)).split()).strip()

    @staticmethod
    def _is_caps(text) -> bool:
        """The style of case is set in capitals; nothing else in the caption is.

        Not 'every letter', because the versus and the party tags the court
        leaves in lower case ('v.', 'a/k/a', 'd/b/a', 'et al.') ride along
        inside it. A four-fifths majority separates 'CLAYTON D. RICHARDS v.
        VANDERBILT UNIVERSITY MEDICAL' (97% capitals) from every session,
        origin and appearance row in the corpus (under 20%)."""
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return False
        return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.8

    def _is_docket_row(self, text) -> bool:
        head = text.split(None, 1)[0].lower() if text.split() else ""
        return head in self._DOCKET_OPENERS

    def _ends_with_title(self, text) -> bool:
        words = text.rstrip(".").split()
        return bool(words) and words[-1].strip(",;.").lower() in self._JUDICIAL_TITLES

    def _split_docket(self, text):
        """A docket row into (docket, judge).

        The two are set on one row separated by nothing but space, so the
        split is by what the tokens ARE: a docket number carries digits and a
        judge's name does not, so the docket is the leading run of digit-
        bearing tokens and the judge is the remainder. Claimed only when a
        judicial title closes the row — otherwise the whole row is the docket
        ('Nos. 94-02797, 94-02798, ... , P-25948', whose judge is printed on a
        row of its own)."""
        parts = text.split(None, 1)
        rest = parts[1] if len(parts) > 1 else ""
        if not self._ends_with_title(text):
            return rest.strip(), ""
        tokens = rest.split()
        n = 0
        while n < len(tokens) and any(c.isdigit() for c in tokens[n]):
            n += 1
        if not n or n == len(tokens):
            return rest.strip(), ""
        return " ".join(tokens[:n]).strip(" ,"), " ".join(tokens[n:]).strip()

    # ------------------------------------------------------------- the read
    def _read_criteria(self, doc) -> None:
        rows = [
            (self._crit_text(r), (r or {}).get("align") if isinstance(r, dict) else None)
            for r in (doc.summary or [])
        ]
        rows = [(t, a) for t, a in rows if t]
        dockets = [i for i, (t, _a) in enumerate(rows) if self._is_docket_row(t)]
        if not dockets:
            # No docket rows: not the template this reader knows. Publishing a
            # partial read of an unknown layout is worse than publishing none.
            return
        cut = dockets[-1]
        crit = self._read_caption(rows[: cut + 1], cut)
        crit.update(self._read_body(rows[cut + 1:]))
        if crit.get("cases") or crit.get("summary"):
            self._publish_tn_criteria(doc, crit)

    def _read_caption(self, caption, cut) -> dict:
        crit, case = {}, {}
        names, history, judges, lower_dockets = [], [], [], []
        seen_name = False
        for i, (text, _align) in enumerate(caption):
            if i == 0 and text.lower().startswith("in the"):
                crit["court"] = text
                continue
            if not seen_name and text.upper().startswith("AT "):
                crit["sitting"] = text
                continue
            if self._is_docket_row(text):
                docket, judge = self._split_docket(text)
                if i == cut:
                    case["docket"] = f"No. {docket}" if docket else None
                elif docket:
                    lower_dockets.append(docket)
                if judge:
                    judges.append(judge)
                continue
            if self._ends_with_title(text):
                judges.append(text)
                continue
            if self._is_caps(text):
                names.append(text)
                seen_name = True
                continue
            if not seen_name:
                crit.update(self._session_date(text))
                continue
            history.append(text)
        if names:
            case["case_name"] = " ".join(names)
        if history:
            # Each row is a complete statement of its own (how the appeal
            # arrives, then the court it arrives from), so they are listed,
            # not run together into one sentence.
            case["prior_history"] = "; ".join(history)
            case["lower_court"] = self._lower_court(history[0])
        if lower_dockets:
            case["lower_docket"] = "; ".join(lower_dockets)
        if judges:
            case["lower_judge"] = "; ".join(judges)
        case = {k: v for k, v in case.items() if v}
        if case:
            crit["cases"] = [case]
        return crit

    @staticmethod
    def _session_date(text) -> dict:
        """When the case was heard, from how the court says it was heard.

        'February 12, 2025 Session' is an oral argument and 'Assigned on
        Briefs June 16, 2026' is a submission on the papers — two different
        facts, and the court's own two forms are what tell them apart. A row
        that is neither is not published."""
        if " Session" in text:
            return {"date_argued": text.split(" Session")[0].strip()}
        opener = "Assigned on Briefs"
        if text.startswith(opener):
            return {"date_submitted": text[len(opener):].strip()}
        return {}

    @staticmethod
    def _lower_court(text):
        """The tribunal the origin row names — what follows 'from the'.

        'Appeal by Permission from the Court of Appeals' → 'Court of Appeals';
        'Appeal from the Chancery Court for Washington County' → that court.
        A row that names the court outright and says nothing about the appeal
        ('Circuit Court for Coffee County') is already the answer."""
        low = text.lower()
        for lead in (" from the ", " from "):
            if lead in low:
                return text[low.index(lead) + len(lead):].strip()
        return text if "court" in low or "commission" in low else None

    def _read_body(self, prose) -> dict:
        """The rows below the docket: summary, disposition, byline, counsel.

        Phase by phase, in the order the court prints them. The centred run
        that opens after the summary is the disposition and the row the byline
        grammar answers is the byline; everything full width after it is an
        appearance."""
        crit = {}
        summary, disposition, counsel = [], [], []
        phase = "summary"
        for text, align in prose:
            if align == "C":
                if phase == "summary" and summary:
                    phase = "disposition"
                if phase == "disposition":
                    disposition.append(text)
                continue
            if "panel_line" not in crit and self.parse_author_line(text):
                crit["panel_line"] = text
                phase = "counsel"
                continue
            if phase == "summary":
                summary.append(text)
                continue
            counsel.append(text)
        if summary and (disposition or crit.get("panel_line")):
            # The summary is only published when something BELOW it closed it:
            # the disposition the court centres, or the byline. Tennessee also
            # publishes a single separate writing as its own file, with a thin
            # headmatter and no summary at all (tenn/gary_wygant, the
            # concurrence to the file before it), and with no floor under the
            # zone every paragraph of such a document reads as summary. An
            # absent section is absent; it is not something to fill.
            crit["summary"] = "\n".join(summary)
        if disposition:
            crit["disposition"] = " ".join(disposition)
        if crit.get("panel_line"):
            names = self._byline_names(crit["panel_line"])
            if names:
                crit["panel"] = names
        if counsel:
            crit["counsel"] = "\n\n".join(counsel)
        return crit

    def _byline_names(self, byline) -> list:
        """The judges the byline names — read off the page's own casing.

        Tennessee sets every judge in the byline in capitals and every word of
        the sentence carrying them in lower case ('MARY L. WAGNER, J.,
        delivered the opinion of the Court, in which HOLLY KIRBY, C.J., and
        JEFFREY S. BIVINS, ... JJ., joined.'), so the capitalised runs ARE the
        roster and the prose between them needs no reading at all. Inside a
        run the court's own commas separate one judge from the next; a
        fragment that is nothing but abbreviations is a title ('J.', 'C.J.',
        'JJ.', 'P.J., W.S.'), and a fragment that is a name suffix belongs to
        the judge above it ('JOHN W. CAMPBELL, SR.')."""
        runs, current = [], []
        for token in byline.split():
            letters = [c for c in token if c.isalpha()]
            if letters and all(c.isupper() for c in letters):
                current.append(token)
            else:
                if current:
                    runs.append(" ".join(current))
                current = []
        if current:
            runs.append(" ".join(current))
        names = []
        for run in runs:
            for fragment in run.split(","):
                # The full stops stay on for the tests below — they are what
                # marks an abbreviation as one ('J.' against a surname).
                name = fragment.strip().strip(",;").strip()
                if not name or not any(c.isalpha() for c in name):
                    continue
                if name.lower().replace(".", "") in self._NAME_SUFFIXES:
                    if names:
                        names[-1] = f"{names[-1]}, {name}"
                    continue
                if all(self._is_abbreviation(w) for w in name.split()):
                    continue
                names.append(name.rstrip("."))
        return list(dict.fromkeys(names))

    @staticmethod
    def _is_abbreviation(word) -> bool:
        """'J.' / 'C.J.' / 'JJ.' / 'W.S.' — letters in ones and twos, cut by
        full stops. A judge's name never is."""
        if not word.endswith("."):
            return False
        return all(
            len(part) <= 2 and part.isalpha()
            for part in word.rstrip(".").split(".")
            if part
        )

    def _publish_tn_criteria(self, doc, crit) -> None:
        """Attach the criteria and mirror them into the flat fields.

        The same plumbing the circuits' ``_publish_criteria`` provides, but
        that method lives on the federal-circuit base and Tennessee is not a
        circuit; scotus writes its own for the same reason."""
        doc.criteria = crit
        case = (crit.get("cases") or [{}])[0]
        if case.get("docket"):
            doc.docket_number = case["docket"]
        if case.get("lower_docket"):
            doc.other_docket = case["lower_docket"]
        if case.get("prior_history"):
            doc.history = case["prior_history"]
        if case.get("lower_court"):
            doc.lower_court = case["lower_court"]
        if case.get("case_name"):
            doc.parties = [case["case_name"]]
        if crit.get("disposition"):
            doc.disposition = crit["disposition"]
        if crit.get("panel_line"):
            doc.judges = crit["panel_line"]
        if crit.get("panel"):
            doc.panel = crit["panel"]
        if crit.get("counsel"):
            doc.attorneys = crit["counsel"]
        submitted = crit.get("date_submitted") or crit.get("date_argued")
        if submitted and not doc.submitted:
            doc.submitted = submitted


class TennesseeAppellate(
    TennesseeOpinionHeading,
    TennesseeCriteria,
    TennesseeHeadmatter,
    TennesseeBlockquotes,
    TennesseeFurnitureDrop,
    StateAppellate,
):
    # Headmatter criteria: one template across the three courts, read off the
    # docket rows and the alignment of what follows them.
    parse_criteria_enabled = True
    accept_delivered = (
        True  # Tennessee prose byline: NAME, J., delivered the opinion ...
    )
    # The Court of Appeals sits in sections; the byline carries the section
    # after the title ('STAFFORD, P.J., W.S., delivered ...').
    title_suffixes = ("W.S.", "M.S.", "E.S.")
    abbrev_titles = (
        ("PJ.", "Presiding Judge"),
        ("CJ.", "Chief Judge"),
    ) + StateAppellate.abbrev_titles
    fold_page_numbers = True

    def extract(self, pdf_path):
        self._heading_bylines = {}
        self._hm_super_labels = set()
        doc = super().extract(pdf_path)
        # A footnote whose superscript reference sits in the headmatter (a
        # caption footnote) belongs to the headmatter, not the opinion that
        # owns the rest of page 1.
        if self._hm_super_labels and doc.opinions:
            op = doc.opinions[0]
            moved = [f for f in op.footnotes if f.label in self._hm_super_labels]
            if moved:
                op.footnotes = [
                    f for f in op.footnotes if f.label not in self._hm_super_labels
                ]
                doc.headmatter_footnotes = list(doc.headmatter_footnotes) + moved
        return doc

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        cut = starts[0] if starts else len(all_segments)
        self._hm_super_labels = self._superscript_labels(
            seg for _, seg, _ in all_segments[:cut]
        )
        return starts

    def _superscript_labels(self, segs) -> set:
        """Labels of superscript digit references in the given segments — a
        digit run set well below the line's dominant font size."""
        labels = set()
        for seg in segs:
            for line in seg:
                chars = line.get("chars") or []
                sizes = [
                    round(c.get("size", 0), 1)
                    for c in chars
                    if (c.get("text") or "").strip()
                ]
                if not sizes:
                    continue
                dom = max(set(sizes), key=sizes.count)
                run = ""
                for c in chars:
                    t = c.get("text") or ""
                    if t.isdigit() and c.get("size", 0) < dom * 0.8:
                        run += t
                    elif run:
                        labels.add(run)
                        run = ""
                if run:
                    labels.add(run)
        return labels

