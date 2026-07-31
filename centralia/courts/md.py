"""Supreme Court of Maryland.

Two document shapes, both handled here:

  * OPINIONS — reporter HEADNOTES on the first page(s) (an italic case-name
    attribution line, then BOLD topical headings 'LANDLORD-TENANT LAW – …'
    each over summary prose), then a centered caption page ('IN THE SUPREME
    COURT / OF MARYLAND / No. / September Term / parties / coram JJ.'), then
    the opinion(s). The author is named at the BOTTOM of a caption page, not
    at the body: 'Opinion by Fader, C.J.' / 'Dissenting Opinion by Gould,
    J., which Biran, J., joins.' (title-case surname, abbreviated title,
    optional joinder clause). A concurrence/dissent gets its own REPEATED
    caption page before it continues. The headnotes are lifted into a
    Headnotes section; a 'Biran and Gould, JJ., dissent.' vote roster is not
    an opinion start (its name is not a clean surname).

  * ORDERS — an asterisk-rail caption ('PARTY  *  IN THE / * SUPREME COURT
    …'), a centered ALL-CAPS 'ORDER' (or 'PER CURIAM ORDER') that opens the
    body, and a '/s/ <Judge>' + title signature with a court seal beside it.
    The body is one writing typed 'order'; the signature is lifted into a
    Signature section and the seal is dropped as furniture.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

# Longest-first so the compound prefixes win over the bare 'Opinion by'.
_PREFIXES = (
    ("Concurring and Dissenting Opinion by", "concurring and dissenting"),
    ("Concurring Opinion by", "concurring"),
    ("Dissenting Opinion by", "dissenting"),
    ("Opinion by", None),
)

_BANNER = "IN THE SUPREME COURT"
_JUDGE_TITLE = ("justice", "judge")


class MarylandSupreme(AbbrevTitleSupreme):
    court_id = "md"
    court_label = "Supreme Court of Maryland."
    allow_titlecase_name = True
    # An order's asterisk-rail caption starts as high as y≈29 — its opening
    # '* IN THE' row sat above the shared 32pt margin and was filtered away
    # before anything could place it, so the caption lost its first line. No
    # other page in the corpus prints anything in that band.
    margin_top = 24
    # Block quotes sit a full inch in (x0≈144 vs the 72 body margin), single
    # spaced at ~15pt — inside the 'notice' gap band, so they rendered as
    # plain paragraphs. The both-margins-indent geometry is the tell.
    blockquote_by_indent = True
    # The centered caption banner that opens the caption page — the reporter
    # headnotes are the page(s) before it. The Appellate Court (mdctspecapp)
    # shares the whole anatomy under its own banner.
    caption_banner = _BANNER

    # ------------------------------------------------------------- bylines
    def _md_strip(self, text: str):
        for prefix, kind in _PREFIXES:
            if text.startswith(prefix):
                return text[len(prefix) :].strip(), kind
        return None, None

    def _md_author(self, rest: str):
        """(name, title) from the text after an 'Opinion by' prefix. Tolerates
        a trailing joinder clause ('Gould, J., which Biran, J., joins.') and a
        bare trailing comma — the author is the leading surname + title."""
        r = self._abbrev_parse(rest)
        if r is not None:
            return r[0], r[1]
        if "," in rest:
            name = rest.split(",", 1)[0].strip()
            after = rest.split(",", 1)[1].strip()
            if self._name_ok(name):
                for ab, full in self.abbrev_titles:
                    if after.startswith(ab):
                        return name, full
        return None

    def parse_author_line(self, text):
        rest, kind = self._md_strip(text.strip())
        if rest is not None:
            a = self._md_author(rest)
            if a is not None:
                return a[0], a[1], kind
        # Deliberately NO fall-through to the bare abbreviated-title parser: a
        # 'Fader, C.J.' coram listing or a 'Killough' signature is not an
        # opinion byline here — only the caption's 'Opinion by ...' line is.
        return None

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        rest, _kind = self._md_strip(text)
        if rest is not None:
            return (text, "") if self._md_author(rest) is not None else None
        # 'PER CURIAM ORDER' is an order heading, not a per-curiam opinion
        # byline — let the order path handle it (it is usually signed).
        if text.upper().startswith("PER CURIAM") and not self._is_order_heading(text):
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        return None

    # --------------------------------------------------------- headmatter
    @classmethod
    def _is_order_heading(cls, text: str) -> bool:
        t = cls._squeeze_spaced(text.strip())
        return t in ("ORDER", "PER CURIAM ORDER") or (
            t.isupper() and t.endswith("ORDER") and 5 <= len(t) <= 28
        )

    @staticmethod
    def _seg_page(seg) -> int:
        for l in seg:
            chars = l.get("chars") or []
            if chars and chars[0].get("page_number"):
                return chars[0]["page_number"]
            if l.get("page_number"):
                return l["page_number"]
        return 1

    def _banner_page(self, segs) -> int | None:
        """Page of the centered 'IN THE SUPREME COURT' caption banner — the
        reporter headnotes are the page(s) BEFORE it. A contains-match (the
        court-below text can share the banner's line); the ALL-CAPS phrase
        never appears in the mixed-case headnote prose. None for orders,
        whose '* IN THE' rail line is not this banner."""
        for seg in segs:
            for l in seg:
                if self.caption_banner in self.line_plain_text(l):
                    return self._seg_page(seg)
        return None

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        # Split the reporter headnotes (the page(s) before the caption banner
        # page) off into their own section; the court-of-origin block on the
        # banner's own page stays with the caption headmatter.
        bp = self._banner_page(headmatter_segs)
        if bp is not None and bp > 1:
            head = [s for s in headmatter_segs if self._seg_page(s) < bp]
            headmatter_segs = [s for s in headmatter_segs if self._seg_page(s) >= bp]
            if head:
                self._md_headnotes = self._group_headnote_rows(
                    self._styled_headmatter(head).get("summary", [])
                )
        # Maryland centers its caption (banner / docket / parties) on the
        # right-half axis (~x413), not the page center — take that axis from
        # the caption's own underscore divider rule so ``line_alignment``
        # centers those rows instead of reading them as left/right.
        self._md_cap_axis = self._caption_axis(headmatter_segs)
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        # Asterisk-rail order captions fold into a clean two-column block;
        # the centered opinion banner has no '*' token, so it passes through.
        if d.get("summary"):
            d["summary"] = self._fold_asterisk_caption(d["summary"], headmatter_segs)
        return d

    # ---------------------------------------------------------- headnotes
    _BOLD_OPEN, _BOLD_CLOSE = "<strong>", "</strong>"

    def _group_headnote_rows(self, rows: list) -> list:
        """Join the reporter headnotes' wrapped rows into logical units.

        The headnote page is prose, not a caption: the attribution line, each
        bold topical heading and each summary paragraph wrap over several rows
        that must read as ONE unit, and a blank row is the real separator. Runs
        of consecutive rows of the same weight are joined; a run of fully bold
        rows becomes one bold heading rather than a heading split mid-phrase."""
        out: list = []
        run: list = []
        run_bold = False

        def flush():
            nonlocal run, run_bold
            if run:
                if run_bold:
                    inner = " ".join(
                        r[len(self._BOLD_OPEN) : -len(self._BOLD_CLOSE)] for r in run
                    )
                    html = f"{self._BOLD_OPEN}{inner}{self._BOLD_CLOSE}"
                else:
                    html = " ".join(run)
                out.append({"__hm__": True, "html": html, "rel": 1.0, "align": "L"})
            run = []

        for r in rows:
            if not (isinstance(r, dict) and r.get("__hm__")):
                flush()
                out.append(r)
                continue
            html = str(r.get("html", "")).strip()
            if not html:
                flush()
                continue
            bold = html.startswith(self._BOLD_OPEN) and html.endswith(self._BOLD_CLOSE)
            if run and bold != run_bold:
                flush()
            run_bold = bold
            run.append(html)
        flush()
        return out

    def _caption_axis(self, segs):
        """Horizontal center of the caption column — the midpoint of its
        full-width underscore divider rule (KAPNECK is bracketed by
        '______' rules spanning x290-537). None if there is no such rule
        (orders use the asterisk rail instead)."""
        best = None
        banner = False
        for seg in segs:
            for l in seg:
                t = self.line_plain_text(l).strip()
                if len(t) >= 12 and set(t) <= set("_"):
                    w = l["x1"] - l["x0"]
                    if best is None or w > best[1]:
                        best = ((l["x0"] + l["x1"]) / 2, w)
                if self.caption_banner in t:
                    banner = True
        if best:
            return best[0]
        if not banner:
            return None
        # Some caption pages print no underscore divider at all. The column is
        # still centered on its own axis, so the rows themselves reveal it: the
        # banner, docket, term and party rows all share one midpoint. Take the
        # agreed midpoint of the right-hand column rather than falling back to
        # the page center, which would read the whole caption as left-aligned.
        centers = sorted(
            (l["x0"] + l["x1"]) / 2
            for seg in segs
            for l in seg
            if l["x0"] > 230 and (l["x1"] - l["x0"]) < 300
        )
        if len(centers) >= 4:
            mid = centers[len(centers) // 2]
            near = [c for c in centers if abs(c - mid) <= 6]
            if len(near) >= 4:
                return sum(near) / len(near)
        return None

    def line_alignment(self, line, page_width) -> str:
        axis = getattr(self, "_md_cap_axis", None)
        if axis is not None:
            x0, x1 = line["x0"], line["x1"]
            cx, w = (x0 + x1) / 2, x1 - x0
            # a row centered on the caption axis (and not the small left
            # court-of-origin block) renders centered
            if x0 > 230 and abs(cx - axis) < 28 and w < page_width * 0.5:
                return "C"
        return super().line_alignment(line, page_width)

    def _fold_asterisk_caption(self, summary: list, headmatter_segs: list) -> list:
        """Fold an order's asterisk-rail caption into one two-column block —
        party lines left of the '*' rail, court/docket lines right — rebuilt
        from the page-1 line RUNS rather than from the styled text.

        The rail is printed on its own baseline rhythm, independent of the two
        columns'. Where a party row happens to land on a rail row the glyph
        comes through on that row; where it doesn't, pdfplumber hands back the
        two columns fused into one string with no rail at all ('IN THE MATTER
        OF THE       SUPREME COURT'). A token fold can only split the first
        kind, so the second kind piled both columns into the left cell and
        left the right cell empty. Splitting each row at the rail's x instead
        works on every row, whether or not the glyph was printed on it.

        A caption with no rail (the opinion banner) passes through untouched."""
        import re as _re

        lines = []
        for seg in headmatter_segs:
            for l in seg:
                chars = l.get("chars") or []
                pno = (
                    chars[0].get("page_number", 1) if chars else l.get("page_number", 1)
                ) or 1
                if pno == 1:
                    lines.append(l)
        lines.sort(key=lambda l: (l["top"], l["x0"]))

        runs_by_line = [(l, self._split_line_runs(l)) for l in lines]
        rails = [
            r
            for _l, rs in runs_by_line
            for r in rs
            if (r.get("text") or "").strip() == "*"
        ]
        if len(rails) < 2:
            return summary
        rail_x = sorted((r["x0"] + r["x1"]) / 2 for r in rails)[len(rails) // 2]
        rail_tops = [
            l["top"]
            for l, rs in runs_by_line
            if any((r.get("text") or "").strip() == "*" for r in rs)
        ]
        lo, hi = min(rail_tops), max(rail_tops)

        # One cell pair per printed row; a row is every line sharing a baseline.
        zone: list = []  # [{top, lines, left, right}]
        for l, rs in runs_by_line:
            if not (lo - 1 <= l["top"] <= hi + 1):
                continue
            left = " ".join(
                (r.get("text") or "").strip()
                for r in rs
                if (r.get("text") or "").strip() != "*"
                and (r["x0"] + r["x1"]) / 2 < rail_x
            ).strip()
            right = " ".join(
                (r.get("text") or "").strip()
                for r in rs
                if (r.get("text") or "").strip() != "*"
                and (r["x0"] + r["x1"]) / 2 > rail_x
            ).strip()
            if zone and abs(l["top"] - zone[-1]["top"]) <= 3:
                z = zone[-1]
                z["lines"].append(l)
                z["left"] = " ".join(x for x in (z["left"], left) if x)
                z["right"] = " ".join(x for x in (z["right"], right) if x)
            else:
                zone.append(
                    {"top": l["top"], "lines": [l], "left": left, "right": right}
                )
        if not zone:
            return summary

        block = {
            "__caption__": True,
            "left": [z["left"] for z in zone],
            "right": [z["right"] for z in zone],
            "rail": "*",
            "rail_rows": len(zone),
        }

        # Splice: the block replaces exactly the styled rows the zone lines
        # produced, and swallows the blank rows between them.
        def norm(s):
            return " ".join(
                _re.sub(r"<[^>]+>", "", str(s)).replace("&amp;", "&").split()
            )

        # Match on the rebuilt plain text, not the raw ``text``: the styled row
        # comes from the same gap-aware routine, and the raw string can differ
        # by exactly one space ('GRIEVANCE*' vs 'GRIEVANCE *').
        targets = [
            " ".join(self.line_plain_text(l).split()) for z in zone for l in z["lines"]
        ]
        out, ti, placed, at_tail = [], 0, False, False
        for row in summary:
            txt = (
                norm(row.get("html", ""))
                if isinstance(row, dict) and row.get("__hm__")
                else None
            )
            if ti < len(targets) and txt is not None and txt == targets[ti]:
                if not placed:
                    out.append(block)
                    placed, at_tail = True, True
                ti += 1
                continue
            if at_tail and isinstance(row, str) and not row.strip():
                continue  # a gap row inside the folded block
            at_tail = False
            out.append(row)
        return out if placed else summary

    # ------------------------------------------------------------- orders
    def find_authors(self, all_segments) -> list:
        self._order_start = None
        self._order_author = None
        starts = super().find_authors(all_segments)
        # The headnote page's attribution line can wrap so 'Opinion by Zic,
        # J.' sits alone and reads as a byline — but a real byline never
        # appears BEFORE the caption-banner page. Drop pre-banner starts.
        bp = self._banner_page([seg for _p, seg, _k in all_segments])
        if bp is not None and starts:
            starts = [
                i for i in starts
                if self._seg_page(all_segments[i][1]) >= bp
            ]
        if starts:
            return starts
        # No 'Opinion by' byline: an ORDER. The body starts at the centered
        # ALL-CAPS 'ORDER' heading; the author is the '/s/' signer.
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._is_order_heading(self.line_plain_text(seg[0]).strip()):
                start = i
                break
        if start is None:
            return []
        self._order_start = start
        heading = self.line_plain_text(all_segments[start][1][0]).strip()
        self._order_author = self._md_signer(all_segments) or (
            "PER CURIAM" if "PER CURIAM" in heading.upper() else None
        )
        return [start]

    def _md_signer(self, all_segments):
        """The '/s/ <Name>' signer over a 'Chief Justice' / 'Justice' title."""
        lines = [l for _p, seg, _k in all_segments for l in seg]
        for i, line in enumerate(lines):
            t = self.line_plain_text(line).strip()
            if t.lower().startswith(("/s/", "/s ")):
                name = t[3:].strip()
                if i + 1 < len(lines):
                    nxt = self.line_plain_text(lines[i + 1]).strip()
                    if any(x in nxt.lower() for x in _JUDGE_TITLE):
                        return f"{name}, {nxt}"
                return name
        return None

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            return (self._order_author or ""), [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def correct_page_geometry(self, page) -> None:
        """Word/Cambria footnote anchors embed an INVISIBLE ~1pt 'F'+digit
        ghost pair beside the real superscript mark, which extracts as text
        ('650.7F8' / '12F13'). Strip sub-visible chars from the page's object
        cache so neither the extractor nor the audit (which reads through
        this same hook) ever sees them."""
        super().correct_page_geometry(page)
        try:
            objs = page.objects.get("char")
        except Exception:
            objs = None
        if objs:
            objs[:] = [c for c in objs if (c.get("size") or 9.0) > 1.5]

    # A long writing byline wraps inside the caption's narrow right column, and
    # the break can fall anywhere: after the prefix ('Concurring and Dissenting
    # Opinion by' / 'Killough, J.') or mid-name ('… Opinion by Watts,' / 'J.,
    # which Eaves, J., joins.'). Join the two rows whenever the first carries a
    # writing prefix that does NOT yet parse on its own and the merge does — so
    # an ordinary sentence can't be swept up, and an already-complete byline is
    # left alone.
    def page_lines(self, page):
        lines = self._recluster_caption_page(page)
        if lines is None:
            lines = super().page_lines(page)
        lines = self._recover_signature_title(page, lines)
        out, i = [], 0
        while i < len(lines):
            l = lines[i]
            if i + 1 < len(lines):
                rest, _kind = self._md_strip(self.line_plain_text(l).strip())
                if rest is not None and self._byline_split(l) is None:
                    merged = dict(l)
                    merged["chars"] = self._join_chars(l, lines[i + 1])
                    merged["x0"] = min(l["x0"], lines[i + 1]["x0"])
                    merged["x1"] = max(l["x1"], lines[i + 1]["x1"])
                    if self._byline_split(merged) is not None:
                        out.append(merged)
                        i += 2
                        continue
            out.append(l)
            i += 1
        return out

    # The caption page sets the court-of-origin block in a SMALLER face (10pt)
    # in the left column beside the 13pt caption column. The two columns keep
    # independent leading, so their baselines interleave without lining up
    # ('Case No.' at 86.0 between the banner at 75.3 and 'OF MARYLAND' at 90.1)
    # and one baseline chain swallows the other, scrambling both rows in x
    # order. Cluster the two type sizes separately so each column keeps its own
    # rows. Restricted to the caption page — a body page is one size, and
    # size-splitting there would tear a superscript off its own line.
    _CAPTION_SMALL_MAX = 12.0

    def _recluster_caption_page(self, page):
        try:
            chars = page.chars
        except Exception:
            return None
        sizes = {round(c.get("size") or 0, 1) for c in chars}
        if not any(s < self._CAPTION_SMALL_MAX for s in sizes) or not any(
            s >= self._CAPTION_SMALL_MAX for s in sizes
        ):
            return None
        self.correct_page_geometry(page)

        def band(small: bool):
            def keep(obj):
                if not self.filter_margins(obj):
                    return None
                size = obj.get("size")
                if size is None:
                    return True
                return (size < self._CAPTION_SMALL_MAX) is small

            return self._text_lines(page.filter(keep))

        big = band(False)
        if not any(self.caption_banner in self.line_plain_text(l) for l in big):
            return None
        lines = self._merge_interleaved(big) + self._merge_interleaved(band(True))
        lines.sort(key=lambda l: (l["top"], l["x0"]))
        self._tag_underlined_chars(page, lines)
        return lines

    def _recover_signature_title(self, page, lines) -> list:
        """Recover a signer's title row that sits below the printed margin.

        An order's conformed signature is set flush right at the page foot —
        '/s/ Shirley M. Watts' with 'Senior Justice' one line lower. On the
        tightest of these the title row falls past ``margin_bottom`` and the
        margin filter removes it, so the signature is only half captured and
        the title reads as unplaced content. Recover ONLY a row that directly
        continues a kept '/s/' row in the same right-hand column, which leaves
        the centered bottom folio (a different column) alone."""
        sig = [
            l
            for l in lines
            if self.line_plain_text(l).strip().lower().startswith(("/s/", "/s "))
        ]
        if not sig:
            return lines
        anchor = max(sig, key=lambda l: l["top"])
        extra = [
            l
            for l in self._text_lines(page)
            if l["top"] > self.margin_bottom
            and 0 < l["top"] - anchor["top"] <= 26
            and (abs(l["x0"] - anchor["x0"]) <= 60 or abs(l["x1"] - anchor["x1"]) <= 60)
        ]
        if not extra:
            return lines
        merged = list(lines) + extra
        merged.sort(key=lambda l: (l["top"], l["x0"]))
        return merged

    @staticmethod
    def _join_chars(first, second) -> list:
        """Chars of two wrapped rows, with the word space the wrap swallowed.

        Plain text is rebuilt from inter-glyph gaps, and at a line wrap the next
        row starts LEFT of the previous row's end — a negative gap, so no space
        would be emitted ('by Watts,J.'). Insert one explicit space glyph."""
        a = list(first.get("chars") or [])
        b = list(second.get("chars") or [])
        if a and b:
            gap = dict(a[-1])
            gap["text"] = " "
            gap["x0"] = a[-1]["x1"] + 1.0
            gap["x1"] = a[-1]["x1"] + 2.0
            return a + [gap] + b
        return a + b

    # The court SEAL beside an order's signature is a small (~64-78px) square
    # graphic — decorative furniture, dropped and noted. A real opinion
    # figure (a chart/exhibit) is much larger and kept.
    def extract_page_images(self, page) -> list:
        if not hasattr(self, "_md_dropped"):
            self._md_dropped = []
        kept = []
        for im in super().extract_page_images(page):
            w, h = im["width"], im["height"]
            if max(w, h) < 110 and 0.7 < (w / h if h else 9) < 1.4:
                self._md_dropped.append("[court seal]")
            else:
                kept.append(im)
        return kept

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path: str):
        self._md_headnotes = []
        self._md_dropped = []
        self._order_start = None
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Attach the Maryland-specific sections BEFORE the completeness sweep.

        The sweep builds its 'already placed' haystack from the document as it
        stands; anything filled in afterwards (the reporter headnotes, the
        dropped court seal, the lifted signature) would read as unplaced
        content even though it is rendered."""
        self._md_finish(doc)
        super()._sweep_residual(doc, source_pages)

    def _md_finish(self, doc) -> None:
        if getattr(self, "_md_finished", None) is doc:
            return
        self._md_finished = doc
        if self._md_dropped:
            doc.dropped = list(doc.dropped) + sorted(set(self._md_dropped))
        if getattr(self, "_md_headnotes", None):
            doc.headnotes = self._md_headnotes
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
            self._harvest_md_signature(doc)

    @staticmethod
    def _untag(text: str) -> str:
        out, i, s = [], 0, str(text)
        while True:
            j = s.find("<", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            k = s.find(">", j)
            if k < 0:
                break
            i = k + 1
        return "".join(out)

    def _harvest_md_signature(self, doc):
        """Lift the trailing '/s/ <Name>' + title off the order body into the
        Signature section.

        The signature is at most TWO trailing rows — the conformed '/s/ <Name>'
        and the signer's title, which the flush-right column usually fuses into
        one block. Anchoring on the '/s/' row itself is what keeps the order's
        final 'ORDERED …' decree paragraphs in the body: a wider trailing scan
        reads them as part of the signature block because 'judicial' /
        'judgment' prose trips a title test."""
        op = doc.opinions[-1]
        blocks = op.blocks
        if not blocks:
            return

        def txt(b) -> str:
            return " ".join(self._untag(b.text).split()).lower()

        conformed = ("/s/", "/s ")
        if txt(blocks[-1]).startswith(conformed):
            take = 1  # '/s/ <Name>' [+ fused title] is the last row
        elif (
            len(blocks) >= 2
            and any(x in txt(blocks[-1]) for x in _JUDGE_TITLE)
            and txt(blocks[-2]).startswith(conformed)
        ):
            take = 2  # the title kept its own row
        else:
            return
        doc.signature = [str(b.text) for b in blocks[-take:]]
        op.blocks = blocks[:-take]
