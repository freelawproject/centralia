"""Shared byline for the Mississippi appellate courts (miss / missctapp).

Both courts use the same name-first, all-caps, role-closing-with-a-colon byline;
only the title differs (the Supreme Court seats Justices, the Court of Appeals
seats Judges):

    'SULLIVAN, JUSTICE, FOR THE COURT:'                  (miss, majority)
    'COLEMAN, PRESIDING JUSTICE, FOR THE COURT:'
    'KING, JUSTICE, CONCURRING:' / '..., DISSENTING:'    (separate writings)
    'EMFINGER, J., FOR THE COURT:'                       (missctapp)
    'CARLTON, P.J., FOR THE COURT:'
    'LASSITTER, ST. PÉ, J., FOR THE COURT:'              (compound surname)

The byline is parsed field-by-field (comma-delimited): the field that exactly
matches a court title is the title; everything before it is the name (so a
compound surname carrying its own comma, 'LASSITTER, ST. PÉ', is rejoined); the
role after it gives the kind. The closing colon is the role's terminator — a
'BEFORE RANDOLPH, C.J., ...' panel roster and a vote line ('... JJ., CONCUR.
...', no closing colon) are not opinion starts. The opinion text (paragraph-
numbered '¶1. ...') follows on the next line.
"""

from __future__ import annotations

from ._statesupreme import _is_byline_name


class MississippiStyle:
    # {UPPER title field: Full title}. Subclasses set their court's titles.
    _MS_TITLE_MAP: dict = {}

    # Mississippi numbers every body paragraph ('¶2.') and prints NO first-line
    # indent — marker line and continuation alike sit at the body margin, x0=72.
    # ``split_body_paragraphs`` splits on an indented first line, so it found no
    # boundary at all and fused whole sections into one block: ¶2 through ¶18,
    # 7,910 characters, arrived as a single paragraph. The printed marker is the
    # court's own paragraph label, so it is the boundary.
    #
    # Block quotes sit one 36pt step in (x0=108, x1=504 — both margins) and are
    # SINGLE-spaced against the double-spaced body. ``indent_step`` is lowered so
    # the deep-indent threshold (72 + 1.5·24 = 108) lands exactly on that edge;
    # at the 36pt default it sat at 126 and the quote read as ordinary prose.
    blockquote_by_indent = True
    # TWO thresholds have to reach the same 108pt edge, and they are driven by
    # different knobs: ``indent_step`` sets the segmenter's deep-indent
    # boundary (72 + 1.5·24 = 108) and ``para_indent_min`` sets the quote
    # measure used to CLASSIFY a segment (72 + 1.5·24 = 108). At the 28pt
    # default the classifier's edge sat at 114 — six points inside
    # Mississippi's quote — so most quoted matter was never recognised.
    indent_step = 24.0
    para_indent_min = 24.0

    def _is_ms_para_marker(self, line) -> bool:
        """Whether ``line`` opens a numbered paragraph ('¶2. Around noon …')."""
        text = self.line_plain_text(line).lstrip()
        if not text.startswith("¶"):
            return False
        rest = text[1:].lstrip()
        digits = 0
        while digits < len(rest) and rest[digits].isdigit():
            digits += 1
        return digits > 0

    def _begins_paragraph_block(self, lines) -> bool:
        """A marker line never folds into the previous page's paragraph."""
        return bool(lines) and self._is_ms_para_marker(lines[0])

    def _is_quote_like_segment(self, seg) -> bool:
        """Require the segment's LEFT EDGE to be the quote margin.

        The inherited test asks only that a segment fall wholly *inside* the
        quote measure, which a centered heading also does — 'FACTS' sits at
        x0=285 and 'DISCUSSION' at x0=265 on a 612pt sheet, both comfortably
        between 108 and 516, so both were classified as quoted matter. A real
        quote is SET at the quote margin; a heading merely happens to land
        within it."""
        if not super()._is_quote_like_segment(seg):
            return False
        quote_left = self.body_baseline_x0 + 1.5 * self.para_indent_min
        return min(l["x0"] for l in seg) <= quote_left + 8

    def classify_segment(self, seg) -> str:
        """Route a marker-bearing run to the BODY path so it gets split.

        Segmentation owns paragraph boundaries, and it cannot find one here:
        every line sits at x0=72 with the same 30.7pt leading, so an 18-line
        run of numbered paragraphs arrives as ONE segment. A 'single' segment
        becomes one block without ever reaching ``split_body_paragraphs``,
        which is where the printed '¶N.' marker is honoured — hence ¶2 through
        ¶18 fusing into a single 7,910-character paragraph. Naming it 'body'
        sends it down the path that splits."""
        kind = super().classify_segment(seg)
        if kind == "single" and len(seg) > 1 and any(
            self._is_ms_para_marker(l) for l in seg
        ):
            return "body"
        return kind

    def split_body_paragraphs(self, seg) -> list:
        """Break the segment at each printed paragraph marker.

        Falls back to the inherited indent rule for a segment carrying no
        marker at all (a caption block, a signature, quoted matter), so only
        the numbered body prose is affected."""
        if not seg:
            return []
        if not any(self._is_ms_para_marker(l) for l in seg):
            return super().split_body_paragraphs(seg)
        paras: list = []
        for line in seg:
            if not paras or self._is_ms_para_marker(line):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def _ms_parse(self, text: str):
        """Return (name, title, kind) or None."""
        text = text.strip()
        if not text.endswith(":") or "," not in text:
            return None
        fields = [f.strip() for f in text[:-1].split(",")]
        ti = next(
            (i for i, f in enumerate(fields) if f.upper() in self._MS_TITLE_MAP), None
        )
        if not ti:  # None, or 0 (a name must precede the title)
            return None
        name = " ".join(fields[:ti]).strip()
        if not _is_byline_name(name):
            return None
        full = self._MS_TITLE_MAP[fields[ti].upper()]
        role = " ".join(fields[ti + 1 :]).upper().strip()
        if role.startswith("FOR THE COURT"):
            kind = None
        elif "CONCUR" in role and "DISSENT" in role:
            kind = "concurring in part and dissenting in part"
        elif "CONCUR" in role:
            kind = "concurring"
        elif "DISSENT" in role:
            kind = "dissenting"
        else:
            return None
        return name, full, kind

    def parse_author_line(self, text):
        r = self._ms_parse(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._ms_parse(text) is None:
            return super()._byline_split(line)
        return text, ""
