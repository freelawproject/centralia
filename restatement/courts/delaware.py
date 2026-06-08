"""Supreme Court of the State of Delaware.

Byline: '<NAME>, <Title>, for the Majority:' / '<NAME>, Justice, dissenting:'
(ends with a colon, and the panel is listed as 'Before SEITZ, Chief Justice;
... Justices, constituting the Court en Banc.'). The module is named
``delaware`` because ``del`` is a Python keyword; the court id stays ``del``.
"""

from __future__ import annotations

import re

from ._statesupreme import StateSupreme, is_caps_name

_TAG = re.compile(r"<[^>]+>")
_ROMAN = set("IVXLC")


def _is_section_heading(t: str) -> bool:
    """A centered section heading: a roman numeral + all-caps title
    ('I. INTRODUCTION' / 'V. CONCLUSION'), short and standalone."""
    t = t.strip()
    if not t or len(t) > 50 or t.upper() != t or not any(c.isalpha() for c in t):
        return False
    first = t.split(".", 1)[0].split()[0] if t.split() else ""
    return bool(first) and all(c in _ROMAN for c in first)


class DelawareSupreme(StateSupreme):
    court_id = "del"
    court_label = "Supreme Court of the State of Delaware."

    def extract(self, pdf_path: str):
        """Reclassify roman-numeral section headings ('I. INTRODUCTION') in the
        body as headings so they render centered."""
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind == "p" and _is_section_heading(_TAG.sub("", b.text)):
                    b.kind = "heading"
        return doc

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip().rstrip(":")
        parts = [p.strip() for p in t.split(",")]
        if len(parts) < 2:
            return None
        name, title = parts[0], parts[1]
        if not is_caps_name(name):
            return None
        if not any(x in title for x in ("Justice", "Judge")):
            return None
        kind = ", ".join(parts[2:]).strip() or None
        if kind and "majority" in kind.lower():
            kind = None
        return name, title, kind
