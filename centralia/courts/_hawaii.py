"""Shared format for the Hawaiʻi appellate courts (Supreme Court + Intermediate
Court of Appeals). Both open each writing with an 'OPINION OF THE COURT BY
<NAME>' / 'CONCURRING OPINION BY <NAME>' / 'DISSENTING OPINION BY <NAME>'
heading, or — for a disposition — an 'ORDER ...' header followed by a '(By:
<panel>)' line. No other byline form authors an opinion here, so the author
search is restricted to those: this keeps the appeals court from mistaking a
'<Counsel>, Presiding Judge' / trial-judge line for the author.

Two page-furniture items are dropped: the black 'FOR PUBLICATION IN WEST'S
HAWAIʻI REPORTS ...' banner that repeats at the top of every page, and the red
electronic-filing stamp ('Electronically Filed / Intermediate Court of Appeals /
CAAP-... / 22-MAY-2026 / 08:35 AM / Dkt. 68 OP').
"""

from __future__ import annotations

# (prefix, kind) — longest/most-specific first.
_HAW_BYLINES = (
    ("CONCURRING AND DISSENTING OPINION BY", "concurring and dissenting"),
    ("CONCURRING OPINION BY", "concurring"),
    ("DISSENTING OPINION BY", "dissenting"),
    ("OPINION OF THE COURT BY", None),
    ("CONCURRENCE BY", "concurring"),
    ("DISSENT BY", "dissenting"),
    ("OPINION BY", None),
)


def _is_red(ch) -> bool:
    col = ch.get("non_stroking_color")
    if isinstance(col, (list, tuple)) and len(col) >= 3:
        return col[0] > 0.4 and col[1] < 0.3 and col[2] < 0.3
    return False


class HawaiiStyle:
    def _haw_parse(self, text: str):
        """Return (name, kind) for a Hawaiʻi opinion byline, or None."""
        t = text.strip().rstrip(".")
        up = t.upper()
        for prefix, kind in _HAW_BYLINES:
            if up.startswith(prefix):
                name = t[len(prefix):].strip().split(",")[0].strip()
                if name:
                    return name, kind
        return None

    def parse_author_line(self, text):
        r = self._haw_parse(text)
        if r is not None:
            return r[0], "Justice", r[1]
        return super().parse_author_line(text)

    @staticmethod
    def _is_order_header(text: str) -> bool:
        """A disposition header: 'ORDER DISMISSING MOTION', 'ORDER ACCEPTING
        APPLICATION ...', 'SUMMARY DISPOSITION ORDER', 'MEMORANDUM OPINION'."""
        up = (text or "").strip().upper()
        return len(up) < 70 and (
            up == "ORDER"
            or up.startswith("ORDER ")
            or up.endswith(" ORDER")
            or "DISPOSITION ORDER" in up
            or up == "MEMORANDUM OPINION"
        )

    def _byline_at(self, line) -> bool:
        # Split a segment at an interior opinion heading or order header so it can
        # start its own opinion (the header is otherwise buried in the caption
        # block); a spurious split at a body 'ORDER ...' is harmless — find_authors
        # only treats it as a start when a '(By: <panel>)' line follows.
        t = self.line_plain_text(line)
        return (
            self._haw_parse(t.strip()) is not None
            or self._is_order_header(t)
            or super()._byline_at(line)
        )

    def find_authors(self, all_segments) -> list:
        """Only a Hawaiʻi opinion byline ('OPINION ... BY X') or an 'ORDER ...'
        disposition header starts a writing."""
        self._haw_order = set()
        out, n = [], len(all_segments)
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip()
            if self._haw_parse(t):
                out.append(i)
            elif self._is_order_header(t) and self._by_panel_near(all_segments, i):
                out.append(i)
                self._haw_order.add(i)
        return out

    def _by_panel_near(self, all_segments, i) -> bool:
        """A real order header is followed by a '(By: <panel>)' line within the
        next couple of segments; a stray 'ORDER ...' in the body is not."""
        for j in range(i, min(i + 3, len(all_segments))):
            for ln in all_segments[j][1]:
                if self.line_plain_text(ln).strip().startswith(("(By:", "(By ")):
                    return True
        return False

    def split_author_line(self, line):
        t = self.line_plain_text(line).strip()
        if self._is_order_header(t):
            return "", [line]  # keep the order header as the opening body line
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if op_start in getattr(self, "_haw_order", set()):
            op.author = "PER CURIAM"
            op.type = "majority"
        return op

    def find_footnote_separator(self, page):
        # Full-width caption/section dividers sit in the bottom half (above the
        # 'CERTIORARI ... / ORDER ...' block on a disposition page) and would be
        # mistaken for a footnote rule, dropping the order header beneath. A real
        # footnote has footnote-sized text flush under its rule.
        return self._footnote_sep_small_text_below(page)

    # ----------------------------------------------------------- furniture
    def extract(self, pdf_path):
        self._haw_dropped = []
        doc = super().extract(pdf_path)
        seen, uniq = set(), []
        for t in self._haw_dropped:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        if uniq:
            doc.dropped = list(doc.dropped) + uniq
        return doc

    def page_lines(self, page):
        out = []
        for l in super().page_lines(page):
            t = (l.get("text") or "").strip()
            chars = l.get("chars") or []
            if t.upper().startswith("FOR PUBLICATION IN WEST") or (
                chars and _is_red(chars[0])
            ):
                if t:
                    getattr(self, "_haw_dropped", []).append(t)
                continue
            out.append(l)
        return out
