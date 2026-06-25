"""New Mexico Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME,
Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the
abbreviated-title parser and drops the trial-judge / panel-roster caption
lines.

Slip-print anatomy:
  * pleading-style SIDE LINE NUMBERS (1-28) run down the left margin behind
    a drawn gutter rule at x≈66-68 — the appellate family has no pleading
    handling (that lives in the district base), so the numbers leaked into
    every line ('1 IN THE COURT OF APPEALS …') and broke paragraph
    grouping. ``page_lines`` drops the chars left of the gutter rule;
  * an 11pt SLIP-OPINION NOTICE tops page 1 ('The slip opinion is the first
    version … may contain deviations from the formal authenticated
    opinion.') — small-print headmatter, routed to the Removed box via
    ``notice_max_size`` (body is 14pt);
  * body paragraphs carry bold pinpoint markers ('{2}') on a slightly
    offset baseline — content, kept inline;
  * opinions end with the author's signature and a 'WE CONCUR:' roster of
    the other panel judges — sign-offs, never new opinions (the shared
    roster logic skips them once the line numbers stop corrupting it).
"""

from __future__ import annotations

from ._appellate import StateAppellate


class NewMexicoCourtOfAppeals(StateAppellate):
    court_id = "nmctapp"
    court_label = "New Mexico Court of Appeals."

    # body paragraphs are numbered with a raised brace pinpoint ('{1}', '{2}')
    # — the small digit between the braces is content, not a footnote ref
    bracket_pinpoint = True

    # the slip-opinion notice prints at 11pt (fulton) or 12pt (komis);
    # body is 14pt. The size cap is now gated on being smaller than the
    # document's own dominant size too, so a NM opinion set entirely at 12pt
    # (apache) keeps its caption instead of dropping it all as a notice.
    notice_max_size = 12.5
    # komis's notice starts at top≈12, above the default top margin — keep
    # it in the flow so the size routing can surface it in Removed
    margin_top = 8

    # ------------------------------------------------------------ sign-offs
    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        # 'BUSTAMANTE, Judge, retired, sitting by designation.' — the
        # designation clause is byline furniture, not an opinion kind.
        for op in doc.opinions:
            if op.type.startswith("retired"):
                op.type = "majority"
        # The opinion ends with the author's FULL-NAME sign-off ('KATHERINE
        # A. WRAY, Judge') followed by the 'WE CONCUR:' panel roster; that
        # sign-off parses as a byline and was splitting off as a phantom
        # 3-block opinion. Same surname as the writing it closes + only the
        # roster behind it = a sign-off: fold it back into its opinion.
        merged = []
        for op in doc.opinions:
            prev = merged[-1] if merged else None
            if (
                prev is not None
                and len(op.blocks) <= 6
                and self._signs_off(prev.author, op.author)
            ):
                from ..models import Block

                prev.blocks = (
                    list(prev.blocks)
                    + [Block(kind="p", text=op.author)]
                    + list(op.blocks)
                )
                prev.footnotes = list(prev.footnotes) + list(op.footnotes)
                continue
            merged.append(op)
        # A block quotation is split across segments by the double spacing
        # between its parts (a lead clause, then nested '(1)/(2)/(3)' items),
        # so it arrives as a run of adjacent blockquote blocks. Fold a run of
        # consecutive blockquote blocks into one so the quote reads as a single
        # quotation, not one box per line/part.
        for op in doc.opinions:
            folded = []
            for b in op.blocks:
                if (
                    b.kind == "blockquote"
                    and folded
                    and folded[-1].kind == "blockquote"
                ):
                    folded[-1].text = (
                        str(folded[-1].text).rstrip() + " " + str(b.text).lstrip()
                    )
                else:
                    folded.append(b)
            op.blocks = folded
        return doc

    # ------------------------------------------------------- blockquotes
    def classify_segment(self, seg) -> str:
        """The base classifies a segment by line spacing, but NM bodies are
        single-spaced — so ordinary body and bold section headings get called
        'blockquote' (and the blockquote build path then tags every line a
        quote, ignoring geometry). Confirm a spacing-'blockquote' by GEOMETRY:
        a real quotation is indented at both margins and not bold; otherwise
        it's body, and per-paragraph ``classify_paragraph`` decides."""
        base = super().classify_segment(seg)
        if base != "blockquote":
            return base
        if (
            seg
            and all(self._is_indented(l) for l in seg)
            and not any(self.line_meta(l)[2] for l in seg)
        ):
            return "blockquote"
        return "body"

    def _is_indented(self, line) -> bool:
        """True when a line sits right of the body margin by a full paragraph
        indent — the geometry of a both-margins block quotation (the body is
        at x0≈72; quotations sit at x0≈108, nested items at x0≈144)."""
        return line["x0"] > self.body_baseline_x0 + self.para_indent_min

    def classify_paragraph(self, lines) -> str:
        """An indented, non-bold paragraph is a block quotation (geometry, not
        punctuation). A bold indented run is a numbered section heading
        ('I. Defendant Was Not Deprived …'), not a quotation, so it stays
        prose."""
        if not lines or not all(self._is_indented(l) for l in lines):
            return "p"
        if any(self.line_meta(l)[2] for l in lines):  # bold -> heading
            return "p"
        return "blockquote"

    def split_body_paragraphs(self, seg) -> list:
        """Group lines by indent level: a run of indented quotation lines stays
        together as one paragraph regardless of internal single/double spacing
        and nested item indents, and crossing the indent boundary (in either
        direction) starts a new paragraph — so a quotation that de-indents back
        to the body margin closes cleanly and the body resumes as prose."""
        if not seg:
            return []
        paras = [[seg[0]]]
        for i in range(1, len(seg)):
            if self._is_indented(seg[i]) != self._is_indented(seg[i - 1]):
                paras.append([seg[i]])
            else:
                paras[-1].append(seg[i])
        return paras

    @staticmethod
    def _signs_off(prev_author: str, author: str) -> bool:
        """True when ``author`` is the full-name sign-off of ``prev_author``
        ('WRAY, Judge.' signed as 'KATHERINE A. WRAY, Judge')."""
        if not prev_author or not author:
            return False
        surname = prev_author.split(",")[0].strip().upper()
        name = author.split(",")[0].strip().upper()
        return bool(surname) and (
            name.endswith(" " + surname) or name == surname
        )

    # ------------------------------------------------- pleading line numbers
    def page_lines(self, page):
        gx = self._gutter_x(page)
        if gx is not None:
            page = page.filter(lambda obj: obj.get("x0", 0) >= gx + 1)
        return super().page_lines(page)

    def find_caption_divider(self, page):
        """nmctapp draws no caption divider — the verticals on every page are
        the pleading gutter rails and the right page border. Treating one as
        a divider routes page_lines down the divider branch, which skips the
        interleave merge — leaving the '{N}' pinpoint markers stranded on
        their own offset baseline instead of joined to their paragraph."""
        d = super().find_caption_divider(page)
        if d is None:
            return None
        x, top, bot = d
        if (bot - top) > page.height * 0.8 or x < 100 or x > page.width * 0.85:
            return None
        return d

    @staticmethod
    def _gutter_x(page):
        """x of the pleading margin rule separating the side line numbers
        from the body — a tall thin vertical in the left gutter zone."""
        tall = page.height * 0.6
        xs = [
            r["x1"]
            for r in page.rects
            if (r["x1"] - r["x0"]) < 3
            and (r["bottom"] - r["top"]) > tall
            and 45 < r["x0"] < 130
        ]
        xs += [
            l["x0"]
            for l in page.lines
            if abs(l["x1"] - l["x0"]) < 3
            and abs(l["bottom"] - l["top"]) > tall
            and 45 < l["x0"] < 130
        ]
        return max(xs) if xs else None
