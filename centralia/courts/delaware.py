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
    hm_caption_footnotes = True  # 'TASHA MILLMAN,¹' — caption footnotes
    # The page-number footer sits at y≈726, inside the text margins; fold it
    # out of the body (cross-page merges carry a <pagenumber/> instead).
    fold_page_numbers = True

    def extract(self, pdf_path: str):
        """Reclassify roman-numeral section headings ('I. INTRODUCTION') in the
        body as headings so they render centered; type an ORDER's single
        writing as 'order'."""
        self._order_start = None
        self._order_author = None
        doc = super().extract(pdf_path)
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind == "p" and _is_section_heading(_TAG.sub("", b.text)):
                    b.kind = "heading"
        return doc

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Style-preserving headmatter (centered banner, bold rows, relative
        sizes), with the '§'-railed caption folded into a clean two-column
        block — parties on the left of the rail, docket / court-below on the
        right."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], "§")
        # The court banner spans wider than the generic centering cap; it is
        # the page-centered first row of every Delaware caption.
        for s in d["summary"]:
            if isinstance(s, dict) and s.get("__hm__"):
                if _TAG.sub("", s.get("html", "")).startswith(
                    "IN THE SUPREME COURT"
                ):
                    s["align"] = "C"
                break
        return d

    # ------------------------------------------------------------- orders
    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._order_start = None
        if starts:
            return starts
        # No byline: an ORDER. The body starts at the centered 'ORDER'
        # heading — or, on heading-less single-page orders, at the segment
        # after the 'Submitted:/Decided:' caption block — and the author
        # signs '/s/ Name' over a Justice title after 'BY THE COURT:'.
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self.line_plain_text(seg[0]).strip() == "ORDER":
                start = i
                break
        if start is None:
            for i, (_p, seg, _k) in enumerate(all_segments):
                if any(
                    self.line_plain_text(l).strip().lower().startswith("decided:")
                    for l in seg
                ):
                    if i + 1 < len(all_segments):
                        start = i + 1
                    break
        if start is None:
            return []
        self._order_start = start
        self._order_author = self._signature_author(all_segments)
        if self.hm_caption_footnotes:
            self._hm_super_labels = self._superscript_labels(
                seg for _, seg, _ in all_segments[:start]
            )
        return [start]

    def _signature_author(self, all_segments):
        """The '/s/ Name' signature (some orders type it '/s Name') over its
        'Justice' / 'Chief Justice' title line."""
        lines = [l for _p, seg, _k in all_segments for l in seg]
        for i, line in enumerate(lines):
            t = self.line_plain_text(line).strip()
            if t.lower().startswith(("/s/", "/s ")):
                name = t[3:].strip()
                if i + 1 < len(lines):
                    nxt = self.line_plain_text(lines[i + 1]).strip()
                    if "justice" in nxt.lower() or "judge" in nxt.lower():
                        return f"{name}, {nxt}"
                return name
        return None

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            # The order start is a heading or the first paragraph, not a
            # byline; the author is the signing Justice.
            return (self._order_author or ""), [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

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
