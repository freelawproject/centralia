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

import re

from ._abbrevtitle import AbbrevTitleSupreme


class WisconsinSupreme(AbbrevTitleSupreme):
    court_id = "wis"
    court_label = "Supreme Court of Wisconsin."

    # Body sits at x0=108; a numbered paragraph's first line indents to 144
    # ('¶13 …') and wraps back to 108, while a block quote keeps EVERY line at
    # 144 (both margins in, x1≈467). The two share a left edge, so the ¶ marker
    # is the discriminator: quote-split on the deep indent, but never on a line
    # that opens a paragraph. indent_step lowered so 'deep' (108+1.5·20=138)
    # falls between the body margin and the quote indent.
    body_baseline_x0 = 108.0
    indent_step = 20.0
    blockquote_by_indent = True

    _running_writing = re.compile(r"^JUSTICE .+?,\s+(?:concurring|dissenting)$", re.I)

    _separate_byline = re.compile(
        r"^(?P<name>.+?,\s*[A-Z]\.)(?:,\s*with whom .+? joins,)?\s*"
        r"(?P<kind>concurring|dissenting)\.?$",
        re.IGNORECASE,
    )

    def find_authors(self, all_segments) -> list:
        starts = list(super().find_authors(all_segments))
        self._wis_extra_authors = {}
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip()
            if "with whom" not in text.lower() and not self._separate_byline.match(text):
                continue
            candidate = text
            consumed = []
            # The court often wraps the final `with whom ... joins,
            # dissenting.` clause over one or two text lines immediately
            # before paragraph 1.
            for j in range(i + 1, min(i + 3, len(all_segments))):
                nxt = all_segments[j][1]
                if not nxt:
                    break
                first = self.line_plain_text(nxt[0]).strip()
                candidate += " " + first
                consumed.append(j)
                if self._separate_byline.match(candidate):
                    break
            match = self._separate_byline.match(candidate)
            if match and i not in starts:
                starts.append(i)
                self._wis_extra_authors[i] = (
                    candidate,
                    match.group("kind").lower(),
                    consumed,
                )
        return sorted(starts)

    def build_opinion(self, op_start, op_end, **kwargs):
        extra = getattr(self, "_wis_extra_authors", {}).get(op_start)
        removed = []
        if extra:
            all_segments = kwargs["all_segments"]
            for nxt in extra[2]:
                if nxt >= op_end or not all_segments[nxt][1]:
                    continue
                first = all_segments[nxt][1][0]
                old_kind = all_segments[nxt][2]
                rest = all_segments[nxt][1][1:]
                all_segments[nxt] = (
                    all_segments[nxt][0], rest or [first], old_kind if rest else "notice"
                )
                removed.append((nxt, first, old_kind))
        try:
            op = super().build_opinion(op_start, op_end, **kwargs)
        finally:
            if removed:
                all_segments = kwargs["all_segments"]
                for nxt, first, old_kind in reversed(removed):
                    all_segments[nxt] = (
                        all_segments[nxt][0], [first] + all_segments[nxt][1], old_kind
                    )
        if extra:
            op.author, op.type = extra[:2]
        return op

    def _begins_paragraph_block(self, lines):
        """A first-line-indented body paragraph — its 144pt indent is a first
        line, not a block-quote edge. Two openers: a '¶N …' numbered paragraph,
        or a non-numbered paragraph (e.g. after a '* * *' break) whose first
        line is indented BUT reaches the full right measure. A block quote is
        indented on both margins, so it stays short on the right (≈467)."""
        if not lines:
            return False
        l = lines[0]
        if self.line_plain_text(l).lstrip().startswith("¶"):
            return True
        right = (getattr(self, "_page1_width", None) or 612.0) - self.body_baseline_x0
        return (
            l.get("x0", 0) > self.body_baseline_x0 + 20
            and l.get("x1", 0) >= right - 20
        )

    def page_lines(self, page):
        """A centered '* * *' section break is its own line: mark it (and the
        paragraph that follows) as a segment boundary so the break isn't glued
        onto the next paragraph by the C→L short-line rule, and the paragraph
        after it starts clean."""
        furniture = getattr(self, "_wis_furniture", None)
        if furniture is not None:
            for raw in page.extract_text_lines():
                text = self.line_plain_text(raw).strip()
                if (
                    raw.get("top", 0) < 75
                    and self.line_alignment(raw, page.width) == "C"
                    and self._running_writing.match(text)
                    and text not in furniture
                ):
                    furniture.append(text)
        lines = super().page_lines(page)
        if furniture is None:
            return lines
        kept = []
        for line in lines:
            text = self.line_plain_text(line).strip()
            if (
                line.get("top", 0) < 75
                and self.line_alignment(line, page.width) == "C"
                and self._running_writing.match(text)
            ):
                if text not in furniture:
                    furniture.append(text)
                continue
            kept.append(line)
        ordered = sorted(range(len(kept)), key=lambda i: kept[i].get("top", 0))
        for pos, i in enumerate(ordered):
            t = self.line_plain_text(kept[i]).strip()
            if t and set(t.replace(" ", "")) == {"*"}:
                kept[i]["_seg_break"] = True
                if pos + 1 < len(ordered):
                    kept[ordered[pos + 1]]["_seg_break"] = True
        return kept

    def _sweep_residual(self, doc, source_pages):
        if getattr(self, "_wis_furniture", None):
            doc.dropped = list(doc.dropped) + self._wis_furniture
        super()._sweep_residual(doc, source_pages)

    # ------------------------------------------------------ footnote separator
    def find_footnote_separator(self, page):
        """The footnote rule is a fixed ~144pt rect at the body's left margin
        (x0≈108) — but on a short page it can sit HIGH (footnote 2 opens at
        top≈195), so the shared bottom-half cutoff misses it. Match the rule by
        its width/left-edge signature at any height, gated on footnote-size
        (11pt < the 12pt body) text directly below it."""
        from statistics import median

        tls = page.extract_text_lines()
        best = None
        for r in page.rects:
            w = r["x1"] - r["x0"]
            if (
                r["height"] >= 2
                or not (100 <= w <= 200)
                or r["x0"] >= page.width * 0.3
                or r["top"] <= 90
            ):
                continue
            below = sorted(
                (l for l in tls if l["top"] > r["top"] + 1),
                key=lambda l: l["top"],
            )[:4]
            if not below:
                continue
            szs = [
                median([c["size"] for c in (l.get("chars") or []) if c.get("size")]
                       or [12.0])
                for l in below
            ]
            first = (below[0].get("chars") or [{}])[0].get("size", 12.0)
            if (szs and median(szs) <= 11.4) or first <= 9:
                if best is None or r["top"] < best:
                    best = r["top"]
        return best if best is not None else super().find_footnote_separator(page)

    # ------------------------------------------------------ style adaptation
    @staticmethod
    def _body_line_height(pdf) -> float:
        """Median top-to-top gap of 12pt body chars on a mid-opinion page. The
        five WI layout styles single-space the body at either 15pt (A/C/D) or
        16.2pt (B); the gap bands must key off this so 16.2pt body doesn't fall
        in the block-quote band and render every paragraph as a quote."""
        from statistics import median

        pages = pdf.pages
        pg = pages[min(3, len(pages) - 1)]
        body = [c for c in pg.chars if abs((c.get("size") or 0) - 12) < 0.5]
        tops = sorted({round(c["top"], 1) for c in body})
        gaps = [b - a for a, b in zip(tops, tops[1:]) if 12 < (b - a) < 20]
        return round(median(gaps), 1) if gaps else 15.0

    def _wis_facets(self, pdf, doc, line_h) -> str:
        """Measure the layout facets the reporter's styles vary on — text-block
        left margin, body line height, footnote size + separator-rule width,
        block-quote indent + size, body font — and format a compact signature
        for the review fingerprint. These are the same signals the grouping app
        compares; the extractor surfaces the raw facets to inform it rather than
        assigning a (competing) style letter."""
        from collections import Counter
        from statistics import median

        pages = pdf.pages
        pg = pages[min(3, len(pages) - 1)]
        body = [c for c in pg.chars if abs((c.get("size") or 0) - 12) < 0.5]
        left = round(min((c["x0"] for c in body), default=108))
        bfont = (
            "italic"
            if sum("Italic" in (c.get("fontname") or "") for c in body) > len(body) / 2
            else "roman"
        )

        fn = "none"
        for p in pages:
            sep = self.find_footnote_separator(p)
            if not sep:
                continue
            rule_w = next(
                (round(r["x1"] - r["x0"]) for r in p.rects
                 if abs(r["top"] - sep) < 1 and r["height"] < 2),
                144,
            )
            below = [c["size"] for c in p.chars
                     if c["top"] > sep + 1 and 6 < (c.get("size") or 0) <= 11.6]
            fn = f"fn {round(median(below), 1) if below else 11}pt/{rule_w}rule"
            break

        # block-quote facet: LINES indented on both margins (left+~36 in, short
        # of the right) that do NOT open a numbered paragraph — a ¶N first line
        # shares the indent but wraps back to the body margin, so excluding it
        # leaves the true quote size (11pt on some styles, 12pt on others).
        right = pg.width - left
        qi, qs = [], []
        for p in pages:
            for ln in p.extract_text_lines():
                x0, x1 = ln["x0"], ln["x1"]
                if (
                    left + 20 < x0 < left + 60
                    and x1 < right - 20
                    and not (ln.get("text") or "").lstrip().startswith("¶")
                ):
                    szc = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
                    if szc:
                        qi.append(x0 - left)
                        qs.append(median(szc))
        bq = (
            f"bq {round(median(qi))}pt/{round(median(qs), 1)}pt" if qs else "no bq"
        )
        return f"WI · L{left}pt · {line_h}pt line · {fn} · {bq} · {bfont}"

    def is_non_digital(self, pdf) -> bool:
        """Style E is a scanned opinion: after the digital caption/syllabus, the
        body pages carry only the running header as live text (~a line or two)
        and are otherwise a full-page raster. Flag it so the body isn't emitted
        as a stub — most pages are header-only + image-dominated."""
        pages = pdf.pages
        if len(pages) < 4:
            return super().is_non_digital(pdf)
        header_only = 0
        for pg in pages:
            txt = (pg.extract_text() or "").strip()
            if pg.images and len(txt) < 120:
                header_only += 1
        if header_only >= 0.6 * len(pages):
            return True
        return super().is_non_digital(pdf)

    def extract(self, pdf_path):
        import pdfplumber

        self._wis_furniture = []
        with pdfplumber.open(pdf_path) as pdf:
            line_h = self._body_line_height(pdf)
        # Single-spaced body (15pt A/C/D · 16.2pt B) must classify as body, not
        # a block quote — quotes are found by both-margins indent, so collapse
        # the gap-based block-quote band to nothing and key 'tight' just above
        # the measured line height.
        self.gap_tight_max = round(line_h) + 2
        self.gap_single_max = self.gap_tight_max

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
        if not doc.non_digital:
            with pdfplumber.open(pdf_path) as pdf:
                sig = self._wis_facets(pdf, doc, line_h)
            doc.caption_box = dict(doc.caption_box or {})
            doc.caption_box["style_label"] = sig
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
