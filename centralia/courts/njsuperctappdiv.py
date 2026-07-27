"""New Jersey Superior Court, Appellate Division.

The opinion is introduced by 'The opinion of the court was delivered by' and the
author follows as 'FIRKO, J.A.D.' / 'SUMNERS, JR., C.J.A.D.' — a surname (with
an optional 'JR.') and an Appellate-Division title. A 'PER CURIAM' opinion is
handled by the base.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Longest first so 'C.J.A.D.'/'P.J.A.D.' win over the bare 'J.A.D.'.
_TITLES = (", C.J.A.D.", ", P.J.A.D.", ", J.A.D.")
# The byline is introduced by this fixed phrase on the line ABOVE the name
# ('The opinion of the court was delivered by' / 'FIRKO, J.A.D.'). It is part
# of the opinion, not the headmatter, so the two lines are joined (page_lines,
# or across a page break in extract) and the phrase is stripped before the name
# is parsed. Matched by its 'The opinion ... delivered by' shape so a dropped
# 'of' in the source ('The opinion the court was delivered by') still matches.


def _is_intro(text: str) -> bool:
    low = text.strip().lower()
    return low.startswith("the opinion") and low.endswith("delivered by")


class NewJerseySuperiorCourtAppellateDivision(StateSupreme):
    court_id = "njsuperctappdiv"
    court_label = "New Jersey Superior Court, Appellate Division."

    def page_lines(self, page):
        """Join the wrapped byline: 'The opinion of the court was delivered by'
        on one line, 'NAME, J.A.D.' on the next — so the introduction stays with
        the opinion (as its byline) instead of orphaning into the headmatter."""
        lines = super().page_lines(page)
        out, i = [], 0
        while i < len(lines):
            l = lines[i]
            if (
                i + 1 < len(lines)
                and _is_intro(self.line_plain_text(l))
                and self.parse_author_line(self.line_plain_text(lines[i + 1]).strip())
            ):
                merged = dict(l)
                merged["chars"] = (l.get("chars") or []) + (
                    lines[i + 1].get("chars") or []
                )
                merged["text"] = (
                    self.line_plain_text(l).strip()
                    + " "
                    + self.line_plain_text(lines[i + 1]).strip()
                )
                out.append(merged)
                i += 2
                continue
            out.append(l)
            i += 1
        return out

    def find_footnote_separator(self, page):
        """This court's separator is the 2-inch (144pt) rule at the left body
        margin — 108 of them across the corpus, against a scatter of other
        widths (103, 112, 118, 324, 468 ...) that are underlines and shelves.

        Keyed on that width alone. The inherited finder takes any thin rule
        >=100pt in the bottom half that is neither a caption PAIR nor an
        underline, which on page 1 matches the 216pt shelf closing the caption
        box — sweeping the argued/decided line and the panel roster beneath it
        into the footnote zone. Width is what separates the two here: the shelf
        is 216pt, the separator always 144pt. Keying on the court's own rule
        also drops the bottom-half fence, so a long footnote that pushes its
        separator high up the page is still found."""
        return self.footnote_sep_fixed_left_rule(page, width=144.0)

    def extract(self, pdf_path):
        """Bridge the page-break case the per-page join can't: the introduction
        is the last line of one page and the byline the first line of the next,
        so it lands as the final headmatter row while the byline starts the
        opinion. Move it onto the opinion's author line."""
        doc = super().extract(pdf_path)
        if not doc.opinions:
            return doc
        op = doc.opinions[0]
        if _is_intro(op.author or ""):
            return doc
        summary = doc.summary or []
        for i in range(len(summary) - 1, -1, -1):
            row = summary[i]
            txt = row.get("html", "") if isinstance(row, dict) else str(row)
            if not str(txt).strip():
                continue
            if _is_intro(txt):
                op.author = str(txt).strip() + " " + (op.author or "")
                doc.summary = summary[:i] + summary[i + 1 :]
            break
        return doc

    def parse_author_line(self, text):
        t = text.strip()
        # Peel the 'delivered by' introduction (present on the joined byline).
        if _is_intro(t):
            return None
        low = t.lower()
        if low.startswith("the opinion") and "delivered by" in low:
            t = t[low.index("delivered by") + len("delivered by"):].strip()
        for ti in _TITLES:
            idx = t.find(ti)
            if idx != -1 and idx > 0:
                name = t[:idx].strip()
                # Allow a hyphenated surname ('BISHOP-THOMPSON') and an
                # apostrophe ("O'CONNOR"); an 'SR.'/'JR.' suffix keeps a period.
                core = (
                    name.replace(",", "")
                    .replace(".", "")
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("’", "")
                    .replace("'", "")
                )
                if core and core.isalpha():
                    return name, "Judge", None
        return super().parse_author_line(text)
