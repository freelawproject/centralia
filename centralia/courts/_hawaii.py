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

    # The Intermediate Court of Appeals sets its footnotes right down to
    # y≈751 on a 792pt page, past the inherited 740 cutoff — so the last
    # footnote of a page was filtered off before anything could place it.
    # Nothing sits below this but the folio, which is folded out by value.
    margin_bottom = 756.0

    def find_footnote_separator(self, page):
        # Full-width caption/section dividers sit in the bottom half (above the
        # 'CERTIORARI ... / ORDER ...' block on a disposition page) and would be
        # mistaken for a footnote rule, dropping the order header beneath. A real
        # footnote has footnote-sized text flush under its rule.
        # FIRST the court's own rule: a 2-inch (144pt) rule at the left body
        # margin — 48 of them in hawapp, 58 in haw, against a scatter of other
        # widths that are underlines. Keyed on that signature the bottom-half
        # position fence drops away, which matters because a long footnote
        # pushes its own separator UP the page: yang_1 p8 is one footnote
        # containing a table, its rule at y=234 on a 792pt page, so the fence
        # rejected it and footnote 7 was swallowed into footnote 6.
        sep = self.footnote_sep_fixed_left_rule(page, width=144.0)
        if sep is not None:
            return sep
        sep = self._footnote_sep_small_text_below(page)
        if sep is not None:
            return sep
        return self._haw_sep_by_size(page)

    def _haw_body_size(self, page):
        """The document's dominant type size, measured once and cached.

        Taken over the whole file so a page a long footnote has taken over
        cannot redefine what 'body' means."""
        cached = getattr(self, "_haw_body", None)
        if cached is not None:
            return cached or None
        from collections import Counter

        pdf = getattr(page, "pdf", None)
        pages = getattr(pdf, "pages", None) or [page]
        sizes: Counter = Counter()
        for pg in pages:
            try:
                for ln in pg.extract_text_lines():
                    if not (ln.get("text") or "").strip():
                        continue
                    printable = [
                        c for c in ln["chars"] if (c.get("text") or "").strip()
                    ]
                    if printable:
                        sizes[round(max(c.get("size") or 0 for c in printable))] += 1
            except Exception:
                continue
        self._haw_body = sizes.most_common(1)[0][0] if sizes else 0
        return self._haw_body or None

    def _haw_sep_by_size(self, page):
        """Footnote zone on a page that draws NO separator rule.

        The ICA prints footnotes with no divider at all — just a size drop,
        10pt under a 12pt Courier body. Every rule-based finder therefore
        returns None and the footnotes are left in the body, or (past the
        margin) dropped outright: 'choi_v._aloha_pacific' returned zero
        footnotes with '1 The Honorable Michelle N. Comeau presided.' unplaced.

        The zone is the trailing run of sub-body-size lines at the foot of the
        page. The page folio is skipped rather than ending the run — it is set
        at body size or smaller and sits BELOW the footnotes, so treating it as
        a boundary would hide the block behind it."""
        from collections import Counter

        lines = [l for l in page.extract_text_lines() if (l.get("text") or "").strip()]
        if len(lines) < 3:
            return None

        def size_of(ln):
            return max(
                (c.get("size") or 0)
                for c in ln["chars"]
                if (c.get("text") or "").strip()
            )

        # The body size is a property of the DOCUMENT, not of this page. A
        # footnote long enough to run onto the next page can dominate it —
        # elizares p2 is 35 footnote lines against 11 of body — and a
        # per-page estimate then calls the footnote size 'body', so nothing
        # reads as small and the whole continuation is left unplaced.
        body = self._haw_body_size(page)
        if body is None:
            body = Counter(round(size_of(l)) for l in lines).most_common(1)[0][0]
        top = bottom = None
        for ln in sorted(lines, key=lambda l: -l["top"]):
            txt = (ln.get("text") or "").strip()
            if txt.isdigit():
                continue  # printed folio: below the zone, not its edge
            if round(size_of(ln)) <= body - 1.5:
                top = ln["top"]
                if bottom is None:
                    bottom = ln["bottom"]
                continue
            break
        # A genuine foot-of-page block REACHES the bottom of the page. Testing
        # where the run starts would reject a footnote long enough to fill most
        # of the sheet, which is exactly the case that needs finding.
        if top is None or bottom is None or bottom < page.height * 0.75:
            return None
        return top - 1.0

    # ----------------------------------------------------------- furniture
    _haw_dropped: list = []

    def extract(self, pdf_path):
        self._haw_dropped = []
        self._haw_merged = None
        self._haw_body = None
        return super().extract(pdf_path)

    def _merge_haw_dropped(self, doc) -> None:
        """Append the recorded furniture to ``doc.dropped`` — once."""
        if getattr(self, "_haw_merged", None) is doc:
            return
        self._haw_merged = doc
        seen, uniq = set(doc.dropped), []
        for t in self._haw_dropped:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        if uniq:
            doc.dropped = list(doc.dropped) + uniq

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the furniture BEFORE the completeness sweep.

        It was being merged only after ``extract`` returned, but the sweep runs
        *inside* extract — so the e-filing stamp was recorded, rendered in the
        Removed box, AND reported as unplaced content at the same time
        ('Electronically Filed' / '22-JUL-2026' / '08:51 AM' / 'Dkt. 94 MO')."""
        self._merge_haw_dropped(doc)
        super()._sweep_residual(doc, source_pages)

    def page_lines(self, page):
        out = []
        for l in super().page_lines(page):
            t = (l.get("text") or "").strip()
            chars = l.get("chars") or []
            # The reporter advisory comes in both polarities — '*** FOR
            # PUBLICATION IN WEST'S …' on a published opinion and 'NOT FOR
            # PUBLICATION IN WEST'S …' on an unpublished one — and the leading
            # 'NOT' meant a startswith test matched only the published half,
            # leaving the advisory sitting in the caption on every memorandum
            # opinion. Test for the phrase anywhere in the line: the corpus
            # prints eleven variants of it (asterisk-wrapped, and with the
            # ʻokina coming out as 'ʻ', '‘', '#', '(cid:35)' or a space), and
            # 'PUBLICATION IN WEST' is the part all of them share.
            if "PUBLICATION IN WEST" in t.upper() or (chars and _is_red(chars[0])):
                if t:
                    if self._haw_dropped is type(self)._haw_dropped:
                        self._haw_dropped = []
                    self._haw_dropped.append(t)
                continue
            out.append(l)
        return out
