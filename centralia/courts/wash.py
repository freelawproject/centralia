"""Washington Supreme Court.

Byline abbreviates the title and runs inline after an em-dash, not bold:
'GONZÁLEZ, J.—Our constitutional system ...' / 'MUNGIA, J. — If a person ...' /
'STEPHENS, C.J. (concurring)' / 'MADSEN, J.P.T.*—At issue ...' (justice pro
tempore, with a footnote star). The all-caps surname is the discriminator
(accented capitals like 'GONZÁLEZ' included; two-token surnames like
'GORDON MCCLOUD' too).

Slip-print anatomy (every file shares it):
  * page 1 carries TWO filing stamps above the banner — a box at top left
    ('FILED / IN CLERK'S OFFICE / SUPREME COURT, STATE OF WASHINGTON /
    <date>') and free text at top right ('THIS OPINION WAS FILED FOR RECORD
    AT 8 A.M. ON / <date> / <clerk> / SUPREME COURT CLERK'). They share
    text lines (pdfplumber merges 'FILE' + 'THIS OPINION WAS FILED'), so
    each line is split at the wide x-gap and both stamps go to ``dropped``;
  * the caption is a ')' rail closed by a half-rule on the LEFT that ends
    AT the rail — the generic footnote-separator detector must not mistake
    that shelf for a footnote rule (it chops the majority byline off into
    the footnote flow — the root cause of the 'first opinion missing'
    failures). The REAL separator is a TYPED underscore run;
  * running heads: 'No. <docket>' on majority pages; separate opinions
    restart with 'State v. <name>' / 'No. <docket>' / '(<Justice>, J.,
    concurring/dissenting)' heads and RESTART their printed page numbers
    (a bare centered digit at the page bottom).
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class WashingtonSupreme(AbbrevTitleSupreme):
    court_id = "wash"
    court_label = "Washington Supreme Court."

    # 'J.P.T.' (justice pro tempore) before the bare 'J.' so the longer
    # title wins; same for the chief variant.
    abbrev_titles = (
        ("C.J.P.T.", "Chief Justice Pro Tempore"),
        ("J.P.T.", "Justice Pro Tempore"),
        ("A.C.J.", "Acting Chief Judge"),
    ) + AbbrevTitleSupreme.abbrev_titles

    # Footnote-marker glyphs a pro-tempore designation hangs on the title
    # ('MADSEN, J.P.T.*—' / buck's 'MADSEN, J.∗—' uses U+2217).
    _STAR_GLYPHS = "*∗†‡"

    # ------------------------------------------------------------- byline
    def _abbrev_parse(self, text):
        """One rule for every Washington byline: an ALL-CAPS surname, a
        comma, an abbreviated justice title, an optional '(kind)' clause, an
        optional footnote star, then an EM-DASH that opens the inline
        opinion ('GONZÁLEZ, J.—…', 'MADSEN, J.P.T.*—…', 'MUNGIA, J.
        (concurring/dissenting)—…'). The em-dash is the clincher: it sits on
        every wash writing and on no signature-page sign-off ('Madsen,
        J.P.T.' is title-case and dashless), so it bounds the byline cleanly
        without the generic roster/announcement heuristics.

        Returns (name, title, kind, byline_end) — byline_end is the dash
        index, matching the base contract (the base strips leading dashes
        from the inline body).
        """
        t = text.replace("\xa0", " ").strip()
        # The em-dash opens the inline opinion body. On a full opinion-start
        # line it's present and bounds the byline; when the caller passes
        # the already-extracted byline clause alone ('WHITENER, J.
        # (dissenting)'), there is no dash and the whole string is the
        # byline. Either way the ALL-CAPS surname + abbreviated title is the
        # discriminator; rosters/sign-offs are title-case and excluded.
        di = next((i for i, c in enumerate(t) if c in "—–"), len(t))
        if "," not in t[:di]:
            return None
        name, after = t[:di].split(",", 1)
        name = name.strip()
        if not self._name_ok(name):
            return None
        after = after.strip()
        # a '(kind)' clause sits between the title and the dash, AFTER the
        # footnote star ('J.P.T.* (dissenting)') — peel it first, then the
        # star, leaving the bare title to match.
        kind = None
        if after.endswith(")") and "(" in after:
            after, _, kpart = after.partition("(")
            kind = kpart.rstrip(") ").strip() or None
        after = after.strip().rstrip(self._STAR_GLYPHS + " ")
        # byline ends at the last byline glyph (trim the space before a
        # spaced dash, 'MUNGIA, J. —'); the base strips the dash off the body
        end = di
        while end > 0 and t[end - 1] == " ":
            end -= 1
        for ab, full in self.abbrev_titles:
            if after.rstrip(".") == ab.rstrip("."):
                return name, full, kind, end
        return None

    # ------------------------------------------------------- page furniture
    def page_lines(self, page):
        # ``extract`` resets these per document, but ``page_lines`` may be
        # called standalone (the inspector tool) — initialize lazily so a
        # bare call doesn't AttributeError.
        if not hasattr(self, "_wash_dropped"):
            self._wash_dropped = []
        if not hasattr(self, "_head_kinds"):
            self._head_kinds = {}
        lines = super().page_lines(page)
        kept = []
        pno = page.page_number
        h, w = page.height, page.width
        banner_top = self._banner_top(page) if pno == 1 else None
        for idx, l in enumerate(lines):
            t = self.line_plain_text(l).strip()
            top = l.get("top", 0)
            # page-1 filing stamps: everything above the centered banner.
            # The two stamps share lines — split each at the wide x-gap so
            # the dropped text reads as two coherent stamps.
            if pno == 1 and banner_top is not None and top < banner_top - 4:
                for part in self._x_parts(l):
                    if part.strip():
                        self._wash_dropped.append(part.strip())
                continue
            # bottom page number: a bare centered digit in the bottom band
            # (printed numbers RESTART per writing, so they are furniture,
            # not document page ids)
            if (
                top > h - 80
                and t.isdigit()
                and len(t) <= 3
                and abs((l["x0"] + l["x1"]) / 2 - w / 2) < 60
            ):
                self._wash_dropped.append(t)
                continue
            # running heads: the first line(s) of the page band. 'No. <dkt>'
            # on majority pages; separate opinions also restate the case
            # name and their kind ('(Mungia, J., concurring/dissenting)') —
            # record the kind per page so a bare second byline ('MADSEN,
            # J.P.T.—' with no parenthetical) can be typed from its head.
            if top < 90 and idx <= 2 and self._is_running_head(t):
                low = t.lower()
                if "concur" in low or "dissent" in low:
                    self._head_kinds[pno] = low
                self._wash_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def _is_running_head(self, t: str) -> bool:
        if not t or len(t) > 70:
            return False
        low = t.lower()
        if low.startswith("no. ") and any(c.isdigit() for c in t):
            return True
        # 'State v. Abrams' / 'State v. Abrams, No. 103058-4'
        if " v. " in t and len(t) <= 60 and not t.endswith((".", ",")):
            head = t.split(",")[0]
            if len(head.split()) <= 8:
                return True
        if " v. " in t and "no." in low:
            return True
        # '(Mungia, J., concurring/dissenting)' second head line
        if (
            t.startswith("(")
            and t.endswith(")")
            and ("concur" in low or "dissent" in low)
        ):
            return True
        # 'In re Recall of Hobbs'-style case names restated as heads
        if low.startswith(("in re ", "in the matter")) and len(t) <= 60:
            return True
        return False

    @staticmethod
    def _banner_top(page):
        """y (top) of the centered 'IN THE SUPREME COURT …' banner, the line
        that closes the page-1 filing-stamp zone. None if not found."""
        for tl in page.extract_text_lines():
            if (tl.get("text") or "").strip().startswith("IN THE SUPREME COURT"):
                return tl["top"]
        return None

    # The clerk's seal and conformed-signature GRAPHICS sit in the page-1
    # stamp zone (above the banner) — they are part of the filing stamps,
    # not opinion figures, so they are excluded and noted with the stamps.
    def extract_page_images(self, page) -> list:
        if not hasattr(self, "_wash_dropped"):
            self._wash_dropped = []
        imgs = super().extract_page_images(page)
        if page.page_number != 1:
            return imgs
        banner = self._banner_top(page)
        if banner is None:
            return imgs
        kept, dropped = [], 0
        for im in imgs:
            if im["top"] < banner - 4:
                dropped += 1
            else:
                kept.append(im)
        if dropped:
            self._wash_dropped.append("[filing-stamp seal / clerk signature]")
        return kept

    @staticmethod
    def _x_parts(line):
        """Split a line's chars at wide x-gaps (>30pt) into separate texts —
        the page-1 stamps interleave on shared lines."""
        chars = sorted(line.get("chars") or [], key=lambda c: c["x0"])
        parts, cur = [], []
        for c in chars:
            if cur and c["x0"] - cur[-1]["x1"] > 30:
                parts.append(cur)
                cur = [c]
            else:
                cur.append(c)
        if cur:
            parts.append(cur)
        return ["".join(c.get("text") or "" for c in p) for p in parts]

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        d = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        if d.get("summary"):
            d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path: str):
        self._wash_dropped = []
        self._head_kinds = {}
        doc = super().extract(pdf_path)
        # A separate writing whose byline has no kind parenthetical
        # ('MADSEN, J.P.T.—…') announces its kind only in the running head
        # ('(Madsen, J.P.T., dissenting)') — type it from there.
        for n, op in enumerate(doc.opinions):
            if n == 0 or op.type != "majority":
                continue
            pages = [b.page for b in op.blocks if getattr(b, "page", None)]
            kind = next(
                (self._head_kinds[p] for p in pages if p in self._head_kinds),
                None,
            )
            if kind:
                if "concur" in kind and "dissent" in kind:
                    op.type = "concurring-in-part-and-dissenting-in-part"
                elif "dissent" in kind:
                    op.type = "dissent"
                else:
                    op.type = "concurrence"
        if self._wash_dropped:
            seen, extra = set(), []
            for t in self._wash_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    # -------------------------------------------------- footnote separator
    def find_footnote_separator(self, page):
        """A wash footnote separator is a thin horizontal rule — DRAWN (a
        rect/line) or TYPED ('______') — with FOOTNOTE-SIZED text directly
        beneath it. The font-size test is the tight discriminator: a real
        separator sits above smaller footnote type, while a caption-box
        shelf (the left rule closing a party block at the ')' rail, or the
        edges of j.m.i.'s stacked consolidated-caption boxes) carries
        body-size caption text — the byline — below it. Keying off width and
        position alone mistakes the lowest caption shelf for the separator
        and chops the majority byline into the footnote flow (the 'first
        opinion missing' root cause). Returns the topmost qualifying rule."""
        from collections import Counter

        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        body = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        pw, cutoff = page.width, page.height * 0.45

        cands = []  # tops of thin, left-anchored horizontal rules, lower page
        for r in page.rects:
            if (
                r["bottom"] - r["top"] < 2.5
                and (r["x1"] - r["x0"]) >= 60
                and r["x0"] < pw * 0.35
                and r["top"] > cutoff
            ):
                cands.append(r["top"])
        for ln in page.lines:
            if (
                abs(ln["bottom"] - ln["top"]) < 2.5
                and abs(ln["x1"] - ln["x0"]) >= 60
                and min(ln["x0"], ln["x1"]) < pw * 0.35
                and ln["top"] > cutoff
            ):
                cands.append(ln["top"])
        for tl in page.extract_text_lines():  # typed underscore rule
            t = (tl.get("text") or "").strip()
            if len(t) >= 6 and all(c == "_" for c in t) and tl["top"] > cutoff:
                cands.append(tl["top"])

        good = []
        for top in cands:
            below = [
                round(c.get("size", 0)) for c in chars if top < c["top"] < top + 24
            ]
            # footnote-sized type directly below = a real separator; a caption
            # shelf has body-size (or larger) text, or none, below it
            if below and Counter(below).most_common(1)[0][0] < body:
                good.append(top)
        return min(good) if good else None
