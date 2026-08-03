"""Shared base for the service Courts of Criminal Appeals ('acca',
'afcca', 'nmcca', 'uscgcoca').

Opinions byline 'STEELE, Judge:' / 'MCCLELLAND, Chief Judge:' (spelled
title, colon-terminated) or 'PER CURIAM:'. Orders carry a ')'-railed
caption with the doc type in the right column and no byline — the body
starts at the first wide paragraph after the caption and the document
stays order-typed. The styled headmatter folds the rail caption into a
two-column block.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class MilitaryCCA(StateSupreme):
    author_titles = (
        "Chief Judge",
        "Senior Judge",
        "Appellate Military Judge",
        "Judge",
    )

    def extract(self, pdf_path):
        self._order_start = None
        self._anonymous_opinion_start = None
        doc = super().extract(pdf_path)
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        if not doc.opinions and not doc.summary:
            doc.warnings.append(
                "scanned image-only PDF — no text layer to extract (needs OCR)"
            )
        return doc

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # Some slips draw the footnote rule as text (dashes/underscores) in
        # the lower half, anchored at the left margin.
        best = None
        for line in page.extract_text_lines():
            t = (line.get("text") or "").strip()
            if (
                len(t) >= 4
                and all(c in "—–-_" for c in t)
                and line["top"] > page.height * 0.5
                and line["x0"] < page.width * 0.4
            ):
                if best is None or line["top"] < best:
                    best = line["top"]
        if best is not None:
            for line in page.extract_text_lines():
                if line.get("top", 0) > best and self.parse_author_line(
                    (line.get("text") or "").strip()
                ):
                    return None
        return best

    def parse_author_line(self, text):
        t = text.strip()
        if t.endswith(":"):
            t = t[:-1].strip()
        # Title-case per curiam ('Per curiam:'), accented surnames
        # ('RAMÍREZ, Judge:'), and name particles ('de GROOT, Judge:').
        if " ".join(t.rstrip(".").split()).lower() == "per curiam":
            return ("Per curiam", "per curiam", None)
        import unicodedata

        ascii_t = unicodedata.normalize("NFD", t)
        ascii_t = "".join(c for c in ascii_t if not unicodedata.combining(c))
        r = super().parse_author_line(ascii_t)
        if r is not None:
            return (t.split(",", 1)[0].strip(), r[1], r[2])
        for particle in ("de ", "van ", "von ", "da ", "del "):
            if ascii_t.startswith(particle):
                r = super().parse_author_line(ascii_t[len(particle) :])
                if r is not None:
                    return (t.split(",", 1)[0].strip(), r[1], r[2])
        return None

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._order_start = None
        if starts:
            return starts
        # An order: the body begins at the first wide paragraph after the
        # ')'-railed caption.
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        last_rail = None
        for i, (pno, seg, _k) in enumerate(all_segments):
            if pno != 1:
                continue
            for l in seg:
                if ")" in self.line_plain_text(l).split():
                    last_rail = i
        if last_rail is None:
            # Some Army memorandum opinions have an image-only title page and
            # no recoverable byline.  Start at the first sustained prose run,
            # keeping the author unknown instead of misclassifying a late
            # occurrence of ')' in a citation as a caption rail/order.
            for i, (_p, seg, _k) in enumerate(all_segments):
                if len(seg) >= 2 and max(l["x1"] - l["x0"] for l in seg) > pw * 0.5:
                    self._anonymous_opinion_start = i
                    return [i]
            return []
        for i in range(last_rail + 1, len(all_segments)):
            seg = all_segments[i][1]
            if seg and max(l["x1"] - l["x0"] for l in seg) > pw * 0.5:
                self._order_start = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            return "", [line]
        if getattr(self, "_anonymous_opinion_start", None) is not None:
            return "", [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        if getattr(self, "_anonymous_opinion_start", None) is not None:
            from ..models import DocType

            return DocType.OPINION
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d
