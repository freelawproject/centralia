"""Court of Appeals of Georgia.

Two document families:

* Opinions: author byline at the opinion start ('MARKLE, Judge.' /
  'BARNES, Presiding Judge.'); the shared appellate base handles them.

* Orders: a script 'Court of Appeals / of the State of Georgia' letterhead,
  an 'ATLANTA, <date>' line typed over an underscore fill-in rule (the
  underscores interleave with the date glyphs and are dropped), the formula
  'The Court of Appeals hereby passes the following order:', an ALL-CAPS
  docket caption ('A26A2022. PARTY v. PARTY.'), then the unsigned order
  body, often ending in the clerk's certificate block. The body starts at
  the first segment after the docket caption; there is no author.
"""

from __future__ import annotations

from ._appellate import StateAppellate

_ORDER_FORMULA = "hereby passes the following order"


class CourtOfAppealsOfGeorgia(StateAppellate):
    court_id = "gactapp"
    court_label = "Court of Appeals of Georgia."
    # The reconsideration-deadline boilerplate box on opinions is 10pt small
    # print against a 14pt page — a notice, routed to ``dropped``.
    notice_max_size = 10.5

    def extract(self, pdf_path):
        self._order_start = None
        doc = super().extract(pdf_path)
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
        # The 'ATLANTA, <date>' line is typed over an underscore fill-in
        # rule, interleaving '_' glyphs with the date ('__M_a_y_ 2_2_').
        # Strip the underscores only when they INTERLEAVE with the text
        # (many _↔text transitions along the line); a blank-reporter cite
        # ('___ Ga. ___') has two contiguous runs and stays intact.
        for ln in lines:
            chars = ln.get("chars") or []
            flips = 0
            prev = None
            for c in sorted(chars, key=lambda c: c["x0"]):
                cur = c.get("text") == "_"
                if prev is not None and cur != prev:
                    flips += 1
                prev = cur
            if flips > 4:
                ln["chars"] = [c for c in chars if c.get("text") != "_"]
        return lines

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._order_start = None
        if starts:
            return starts
        # An order: the body begins at the segment after the ALL-CAPS docket
        # caption that follows the 'hereby passes the following order'
        # formula.
        formula_at = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            for l in seg:
                if _ORDER_FORMULA in self.line_plain_text(l).lower():
                    formula_at = i
                    break
            if formula_at is not None:
                break
        if formula_at is None:
            return []
        for i in range(formula_at + 1, len(all_segments)):
            seg = all_segments[i][1]
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            # the docket caption row ('A26A2022. EDIE-JANE CLARKE v. ...')
            first = t.split()[0] if t.split() else ""
            if first.endswith(".") and first[:-1].isalnum() and any(
                c.isdigit() for c in first
            ):
                if i + 1 < len(all_segments):
                    self._order_start = i + 1
                    return [i + 1]
        return []

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            return "", [line]  # unsigned order; first segment is body
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)
