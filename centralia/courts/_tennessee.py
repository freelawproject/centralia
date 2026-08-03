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

    def extract(self, pdf_path):
        self._stamp_dropped = []
        doc = super().extract(pdf_path)
        extra = list(dict.fromkeys(self._stamp_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

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


class TennesseeAppellate(
    TennesseeHeadmatter, TennesseeBlockquotes, TennesseeFurnitureDrop, StateAppellate
):
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

    # --------------------------------------------------- OPINION-heading start
    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._heading_bylines = {}
        if starts:
            first = starts[0]
            nxt = starts[1] if len(starts) > 1 else len(all_segments)
            for j in range(first + 1, nxt):
                seg = all_segments[j][1]
                if not seg:
                    continue
                # The heading may share a segment with the next section head
                # ('OPINION' / 'FACTS' are consecutive centered bold lines), so
                # only the segment's first line is checked.
                if self.line_plain_text(seg[0]).strip() == "OPINION":
                    self._heading_bylines[j] = " ".join(
                        self.line_plain_text(l).strip()
                        for l in all_segments[first][1]
                    ).strip()
                    starts = [j] + starts[1:]
                    break
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

    def build_opinion(self, op_start, op_end, *, all_segments, **kw):
        op = super().build_opinion(op_start, op_end, all_segments=all_segments, **kw)
        byline = getattr(self, "_heading_bylines", {}).get(op_start)
        if byline:
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
