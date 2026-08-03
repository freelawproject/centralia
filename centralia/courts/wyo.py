"""Supreme Court of Wyoming.

Standard bold all-caps byline ('FENN, Justice.' / 'JAROSH, Justice.'); the
trial judge carried in the 'Appeal from ... The Honorable ..., Judge' history
is excluded by the shared base.

A small-print publication notice ('NOTICE: This opinion is subject to formal
revision before publication in Pacific Reporter Third ...') sits at the foot of
page 1 — set in ~10pt, well below the 13-14pt headmatter — and is dropped by
font size. The headmatter is rendered in the style-preserving 'Florida' form.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class WyomingSupreme(StateSupreme):
    court_id = "wyo"
    court_label = "The Supreme Court, State of Wyoming."
    notice_max_size = 11.0

    def _is_non_author_byline(self, text: str) -> bool:
        # A district judge sitting by designation authors some Wyoming Supreme
        # Court opinions.  The actual byline is the bare all-caps form; trial
        # judges in the appeal history retain an ``Honorable``/``Appeal from``
        # prefix and are still rejected by the shared guard.
        parsed = self.parse_author_line(text)
        if parsed and parsed[1] == "District Judge" and text.split(",", 1)[0].isupper():
            return False
        return super()._is_non_author_byline(text)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    def extract(self, pdf_path):
        """The publication notice sits in the page-1 footnote zone (small print
        under a rule), so it is collected as a headmatter footnote; move it to
        ``dropped`` instead — it is page furniture, not a real footnote."""
        doc = super().extract(pdf_path)
        kept = []
        for fn in doc.headmatter_footnotes:
            text = _strip_tags(" ".join(p[1] for p in fn.paragraphs))
            if "subject to formal revision" in text.lower() or text.lower().startswith(
                "notice:"
            ):
                doc.dropped = list(doc.dropped) + [text]
            else:
                kept.append(fn)
        doc.headmatter_footnotes = kept
        return doc


def _strip_tags(s: str) -> str:
    import html as _h

    out, depth = [], 0
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return _h.unescape("".join(out)).strip()
