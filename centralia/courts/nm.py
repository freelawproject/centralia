"""Supreme Court of the State of New Mexico.

The court issues opinions in TWO layouts:

  * Times pleading-paper (formal): a line-number column (1–25) runs down the
    left margin (x0 ~40–54) beside the 14pt Times body (x0 72), DOUBLE-spaced
    (32.2pt leading). Those numbers are layout furniture, dropped before line
    clustering.
  * Arial (orders / unpublished): 12pt Arial body (x0 72), SINGLE-spaced
    (13.8pt), with 10pt footnotes under a 144pt rule.

Both open with the bold all-caps byline ('THOMSON, Justice.') and a 'WE
CONCUR:' roster the shared base folds out. The single-spaced Arial body means a
block quote can't be told from body by line gap, and its first-line paragraph
indent (108, 36pt in from the x0=72 body) equals the block-quote indent — so
the quote is found by geometry (both-margins indent), and a first line that
reaches the full right measure is kept as a paragraph opener, not a quote edge.
"""

from __future__ import annotations

from statistics import median

from ._statesupreme import StateSupreme

# Body text starts at x0 72; the line-number gutter ends well left of it.
_GUTTER_X1 = 60.0


class NewMexicoSupreme(StateSupreme):
    court_id = "nm"
    court_label = "Supreme Court of the State of New Mexico."

    # Paragraphs are numbered with a raised, brace-wrapped pinpoint ('{1}',
    # '{2}', …). The digit is small + a label char, so without this it reads as
    # a footnote reference — '{1}' becomes '{<footnotemark>1</footnotemark>}'
    # and the '{2}'…'{5}' markers get consumed as footnotes. Keep a digit
    # between '{' and '}' as inline paragraph-number content.
    bracket_pinpoint = True

    # The slip-opinion publication notice — a body-size boilerplate block at the
    # very top of page 1 ('The slip opinion is the first version … deviations
    # from the formal authenticated opinion.'). Body-size, so it can't be told
    # from prose by font; keyed on the fixed opening/closing strings and dropped
    # into the Removed box.
    _SLIP_START = "the slip opinion is the first version"
    _SLIP_END = "authenticated opinion"

    def filter_margins(self, obj):
        if super().filter_margins(obj) is None:
            return None
        # Drop the left-margin pleading line-number gutter; a char whose right
        # edge sits left of the body baseline is a line number, not content.
        if (
            obj.get("text") is not None
            and obj.get("x1", obj.get("x0", 0)) <= _GUTTER_X1
        ):
            return None
        return True

    def page_lines(self, page):
        lines = self._merge_hanging_markers(super().page_lines(page))
        if page.page_number != 1 or not lines:
            return lines
        texts = [self.line_plain_text(l).strip() for l in lines]
        start = next(
            (i for i, t in enumerate(texts) if t.lower().startswith(self._SLIP_START)),
            None,
        )
        if start is None:
            return lines
        end = next(
            (j for j in range(start, len(lines)) if self._SLIP_END in texts[j].lower()),
            start,
        )
        for j in range(start, end + 1):
            if texts[j]:
                getattr(self, "_nm_dropped", []).append(texts[j])
        return lines[:start] + lines[end + 1 :]

    def _merge_hanging_markers(self, lines):
        """Fold a hanging '{N}' pinpoint that pdfplumber split onto its own line
        (its raised, smaller baseline sits a few pt off the paragraph's) into
        the paragraph text it opens — the same-baseline run just to its right.
        Otherwise the lone marker sorts BETWEEN the paragraph's first and second
        lines and splits the opening line off."""
        markers = [
            l
            for l in lines
            if (l.get("x1", 0) - l.get("x0", 0)) < 25
            and self._is_brace_marker(self.line_plain_text(l))
        ]
        drop = set()
        for m in markers:
            target = min(
                (
                    l
                    for l in lines
                    if l is not m
                    and abs(l.get("top", 0) - m.get("top", 0)) < 6
                    and l.get("x0", 0) > m.get("x0", 0)
                ),
                key=lambda l: l.get("x0", 0),
                default=None,
            )
            if target is None:
                continue
            target["chars"] = sorted(
                (m.get("chars") or []) + (target.get("chars") or []),
                key=lambda c: c["x0"],
            )
            target["x0"] = min(target.get("x0", 0), m.get("x0", 0))
            target["text"] = "".join(c.get("text", "") for c in target["chars"])
            drop.add(id(m))
        return [l for l in lines if id(l) not in drop]

    @staticmethod
    def _is_brace_marker(text: str) -> bool:
        """True if ``text`` opens with a '{N}' paragraph pinpoint."""
        t = text.lstrip()
        if not t.startswith("{"):
            return False
        i = 1
        while i < len(t) and t[i].isdigit():
            i += 1
        return i > 1 and i < len(t) and t[i] == "}"

    def _split_on_brace(self, seg):
        """Split a segment at each '{N}' paragraph marker — the Times layout
        hangs the marker at the margin (text indented), so its paragraphs share
        one left edge and can't be split by first-line indent alone."""
        if not seg:
            return []
        paras = [[seg[0]]]
        for line in seg[1:]:
            if self._is_brace_marker(self.line_plain_text(line)):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def split_body_paragraphs(self, seg):
        return [
            p
            for grp in self._split_on_brace(seg)
            for p in super().split_body_paragraphs(grp)
        ]

    def split_blockquote_paragraphs(self, seg):
        return [
            p
            for grp in self._split_on_brace(seg)
            for p in super().split_blockquote_paragraphs(grp)
        ]

    def _begins_paragraph_block(self, lines):
        """A '{N}' pinpoint opens a paragraph — never fold it into the prior
        one across a page break. Otherwise: a first-line-indented body paragraph
        reaches the FULL right measure while a block quote (both margins in)
        stays short of it — keying on the right edge stops a non-numbered
        indented first line from being read as a quote boundary. Only the
        single-spaced Arial layout needs the right-edge test; the double-spaced
        Times layout finds quotes by gap and is left untouched."""
        if not lines:
            return False
        if self._is_brace_marker(self.line_plain_text(lines[0])):
            return True
        if not getattr(self, "_nm_single", False):
            return False
        l = lines[0]
        right = (getattr(self, "_page1_width", None) or 612.0) - self.body_baseline_x0
        return (
            l.get("x0", 0) > self.body_baseline_x0 + 20
            and l.get("x1", 0) >= right - 20
        )

    @staticmethod
    def _body_line_height(pdf) -> float:
        """Median top-to-top gap of the dominant body-size chars (14pt Times /
        12pt Arial), ignoring the pleading gutter. Distinguishes the double-
        spaced (32pt) from the single-spaced (13.8pt) layout."""
        from collections import Counter

        pg = pdf.pages[min(4, len(pdf.pages) - 1)]
        body_chars = [c for c in pg.chars if c.get("x1", 99) > _GUTTER_X1]
        if not body_chars:
            return 15.0
        bsz = Counter(round(c.get("size", 0)) for c in body_chars).most_common(1)[0][0]
        body = [c for c in body_chars if abs((c.get("size") or 0) - bsz) < 0.5]
        tops = sorted({round(c["top"], 1) for c in body})
        gaps = [b - a for a, b in zip(tops, tops[1:]) if 8 < (b - a) < 40]
        return round(median(gaps), 1) if gaps else 15.0

    def extract(self, pdf_path):
        import pdfplumber

        self._nm_dropped = []
        with pdfplumber.open(pdf_path) as pdf:
            line_h = self._body_line_height(pdf)
        # The single-spaced Arial layout needs indent-based quotes + retuned
        # gap bands (its quotes match the body leading); the double-spaced Times
        # layout finds quotes by gap and must be left EXACTLY as-is. Set the
        # knobs per document (the extractor instance is reused across a corpus).
        self._nm_single = line_h < 20
        if self._nm_single:
            self.blockquote_by_indent = True
            self.indent_step = 18.0  # deep = 72 + 1.5·18 = 99, below the quote
            self.gap_tight_max = round(line_h) + 2
            self.gap_single_max = self.gap_tight_max
        else:
            self.blockquote_by_indent = False
            self.indent_step = type(self).indent_step
            self.gap_tight_max = type(self).gap_tight_max
            self.gap_single_max = type(self).gap_single_max
        doc = super().extract(pdf_path)
        seen = set()
        uniq = [t for t in self._nm_dropped if not (t in seen or seen.add(t))]
        if uniq:
            doc.dropped = list(doc.dropped or []) + uniq
        if not doc.non_digital:
            with pdfplumber.open(pdf_path) as pdf:
                sig = self._nm_facets(pdf, line_h)
            doc.caption_box = dict(doc.caption_box or {})
            doc.caption_box["style_label"] = sig
        return doc

    def _nm_facets(self, pdf, line_h) -> str:
        """Measured facet signature for the review fingerprint — body font/size,
        line height, footnote size + rule, block-quote indent + size — the same
        signals the reporter's grouping app compares. No style LETTER (the app
        owns the A–M grouping); the extractor surfaces the raw facets."""
        from collections import Counter

        pg = pdf.pages[min(4, len(pdf.pages) - 1)]
        body = [c for c in pg.chars if c.get("x1", 99) > _GUTTER_X1]
        bsz = (
            Counter(round(c.get("size", 0)) for c in body).most_common(1)[0][0]
            if body
            else 12
        )
        bfont = (
            Counter(
                (c.get("fontname") or "").split("+")[-1]
                for c in body
                if abs((c.get("size") or 0) - bsz) < 0.5
            ).most_common(1)[0][0]
            if body
            else "?"
        )
        left = round(min((c["x0"] for c in body if abs((c.get("size") or 0) - bsz) < 0.5),
                         default=72))

        fn = "none"
        for p in pdf.pages:
            sep = self.find_footnote_separator(p)
            if not sep:
                continue
            rw = next((round(r["x1"] - r["x0"]) for r in p.rects
                       if abs(r["top"] - sep) < 1 and r["height"] < 2), 144)
            below = [c["size"] for c in p.chars
                     if c["top"] > sep + 1 and 6 < (c.get("size") or 0) < bsz]
            fn = f"fn {round(median(below), 1) if below else 10}pt/{rw}rule"
            break

        right = pg.width - left
        qi, qs = [], []
        for p in pdf.pages:
            for ln in p.extract_text_lines():
                if (
                    left + 20 < ln["x0"] < left + 70
                    and ln["x1"] < right - 15
                    and ln.get("x1", 0) > left + 60
                ):
                    szc = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
                    if szc:
                        qi.append(ln["x0"] - left)
                        qs.append(median(szc))
        bq = f"bq {round(median(qi))}pt/{round(median(qs), 1)}pt" if qs else "no bq"
        return (
            f"NM · {bfont} {bsz}pt · {line_h}pt line · {fn} · {bq}"
        )
