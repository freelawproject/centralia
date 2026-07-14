"""Supreme Court of Wisconsin.

Byline opens the first numbered paragraph of each opinion:
  '¶1 REBECCA FRANK DALLET, J. Gerald Lorbiecki was diagnosed ...'   (majority)
  '¶1 PER CURIAM. This matter is before the court ...'               (per curiam)
  'SUSAN M. CRAWFORD, J., dissenting.'                               (separate)
The shared abbreviated-title base handles the 'NAME, J.' grammar once the
leading '¶N' paragraph marker is stripped (kept in the byline text).

Two things are deliberately NOT opinion starts: the centered 'JUSTICE ZIEGLER,
dissenting' line — which is a per-page running header, repeated on every page of
that writing, and rejected because 'dissenting' is not an abbreviated title
after the surname — and the title-page summary 'REBECCA FRANK DALLET, J.,
delivered the majority opinion of the Court, in which ...' (a comma
continuation, not a byline). A 'NAME, J., with whom ... joins, concurring.'
byline whose kind trails a join clause is left as body.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class WisconsinSupreme(AbbrevTitleSupreme):
    court_id = "wis"
    court_label = "Supreme Court of Wisconsin."

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        # The page-1 banner and court-seal images are letterhead furniture, not
        # opinion figures — move them out of the body into ``dropped`` (notice).
        for o in doc.opinions:
            imgs = [b for b in o.blocks if b.kind == "image"]
            if imgs:
                o.blocks = [b for b in o.blocks if b.kind != "image"]
                doc.dropped = list(doc.dropped or []) + [
                    "[court seal / letterhead image]" for _ in imgs
                ]
        return doc

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    strip_para_marker = True

    _ORDER_OPENER = "the court entered the following order"

    def parse_author_line(self, text):
        """A per curiam ORDER opens with 'The Court entered the following order
        on this date:' — an unsigned lead opinion (no 'NAME, J.' byline), which
        the byline grammar otherwise leaves in headmatter."""
        if text.strip().lower().startswith(self._ORDER_OPENER):
            return ("PER CURIAM", "per curiam", "order")
        return super().parse_author_line(text)

    def _maybe_drop_running_header(self, page, lines):
        """Continuation pages carry a two-line running header at the very top —
        the case short-name (small, ~9.5pt) and the writing header ('Order of
        the Court' / 'JUSTICE X, dissenting'), both centered. Drop the
        contiguous centered lines from the top of the page so they stop
        repeating through the body."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number == 1 or not lines:
            return lines
        drop = set()
        for ln in sorted(lines, key=lambda l: l.get("top", 0)):
            if ln.get("top", 0) > 75:
                break
            if self.line_alignment(ln, page.width) == "C":
                drop.add(id(ln))
            else:
                break
        return [l for l in lines if id(l) not in drop]

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if text.startswith("¶"):
            # Majority / per curiam: '¶N NAME, J. ...' / '¶N PER CURIAM. ...'.
            return super()._byline_split(line)
        # Off the paragraph stream, only a self-contained separate-writing
        # byline with an explicit kind counts ('SUSAN M. CRAWFORD, J.,
        # dissenting.'). A bare centered 'Per Curiam' / 'JUSTICE X, dissenting'
        # line is a per-page running header, not an opinion start.
        if text.upper().startswith("PER CURIAM"):
            return None
        r = self._abbrev_parse(text)
        if r is None or r[2] is None:
            return None
        _name, _title, _kind, end = r
        return text[:end], text[end:].lstrip(" —–")
