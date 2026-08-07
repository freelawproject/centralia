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
    failures). The REAL separator is a short rule at the body rail, drawn
    on almost every page and typed as an underscore run on a few; the
    signature roster is ruled the same way but in two columns, so its left
    rule is told apart by its right-hand companion;
  * running heads: 'No. <docket>' on majority pages; separate opinions
    restart with 'State v. <name>' / 'No. <docket>' / '(<Justice>, J.,
    concurring/dissenting)' heads and RESTART their printed page numbers
    (a bare centered digit at the page bottom).
"""

from __future__ import annotations

import re

from ._abbrevtitle import AbbrevTitleSupreme
from ..models import Block


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
    # A few Washington PDFs contain a glyph-only signature/footer object with
    # no ToUnicode mapping. pdfplumber exposes it as a run of CID placeholders
    # (for example ``(cid:60)(cid:88)...``). It is not authored text and must
    # not become a phantom footnote. Keep this deliberately narrow: only a
    # line made entirely of CID placeholders is furniture; a CID embedded in
    # real prose remains reviewable.
    _CID_FURNITURE = re.compile(r"^(?:\s*\(cid:\d+\)\s*)+$")

    # The family's bottom margin fence sits at y=740, above the deepest line
    # Washington actually prints. Measured over the corpus, exactly three
    # non-page-number lines print below 740 — and two of them are footnotes
    # (polinder's '† See Appendix for a list of all defendants.' at 743.2,
    # magana-arevalo's footnote 2 at 742.1). The other 511 lines down there
    # are the bare centered page digits, which ``page_lines`` identifies and
    # drops by measurement anyway, so the numeric fence buys nothing here and
    # costs a footnote. Move it below the deepest print.
    margin_bottom = 750

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
        # A consolidated appeal bundles several stamped writings — each opens
        # with its own banner and filing stamp partway through the PDF, not just
        # on page 1 — so look for the banner on every page.
        banner_top = self._banner_top(page)
        for idx, l in enumerate(lines):
            t = self.line_plain_text(l).strip()
            top = l.get("top", 0)
            # filing stamps: everything above a centered banner (the stamp zone
            # that opens each writing). The two stamps share lines — split each
            # at the wide x-gap so the dropped text reads as two coherent stamps.
            if banner_top is not None and top < banner_top - 4:
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
        # 'No. 103058-4' — consolidated pages carry the plural
        # 'Nos. 60325-0-II/ 60331-4-II/ 60335-7-II'
        if low.startswith(("no. ", "nos. ")) and any(c.isdigit() for c in t):
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
        """y (top) of the centered 'IN THE SUPREME COURT …' / 'IN THE COURT OF
        APPEALS …' banner, the line that closes the page-1 filing-stamp zone.
        None if not found."""
        for tl in page.extract_text_lines():
            s = (tl.get("text") or "").strip()
            if s.startswith("IN THE SUPREME COURT") or s.startswith(
                "IN THE COURT OF APPEALS"
            ):
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
        self._separate_stapled_writings(doc)
        self._remove_cid_furniture(doc)
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

    def split_author_line(self, line) -> tuple:
        """Split Washington's inline ``PER CURIAM—`` opening.

        The shared parser recognizes the em-dash form for justice bylines,
        but a per-curiam line can carry a superscript footnote digit before
        the dash (``PER CURIAM1—``). Treating the whole line as the author
        makes the first writing's author absorb its opening sentence.
        """
        text = self.line_plain_text(line).strip()
        if text.upper().startswith("PER CURIAM"):
            chars = line.get("chars") or []
            dash_i = next(
                (i for i, c in enumerate(chars) if (c.get("text") or "") in "—–"),
                None,
            )
            if dash_i is not None:
                body_chars = chars[dash_i + 1 :]
                body = dict(line)
                body["chars"] = body_chars
                body["text"] = "".join(c.get("text") or "" for c in body_chars).lstrip()
                return "PER CURIAM", [body] if body["text"] else []
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        page_no, seg, _kind = kwargs["all_segments"][op_start]
        if not seg:
            return op
        plain = self.line_plain_text(seg[0]).strip()
        if plain.upper().startswith("PER CURIAM") and any(mark in plain for mark in "—–"):
            chars = seg[0].get("chars") or []
            dash_i = next(
                (i for i, char in enumerate(chars) if (char.get("text") or "") in "—–"),
                None,
            )
            if dash_i is not None:
                prefix = dict(seg[0])
                prefix["chars"] = chars[: dash_i + 1]
                prefix["text"] = "".join(
                    char.get("text") or "" for char in chars[: dash_i + 1]
                )
                exact = self.line_inline_text(prefix).strip()
                if exact:
                    op.caption.insert(
                        0,
                        Block(
                            kind="p",
                            text=exact,
                            page=page_no,
                            payload={"role": "byline"},
                        ),
                    )
        return op

    @staticmethod
    def _is_wash_banner(block) -> bool:
        text = re.sub(r"<[^>]+>", "", str(block.text or "")).strip().upper()
        return text.startswith("IN THE SUPREME COURT OF THE STATE OF WASHINGTON")

    def _separate_stapled_writings(self, doc) -> None:
        """Attach repeated captions and signatures to the writing they open.

        Washington's Supreme Court PDFs sometimes staple a lead/per-curiam
        summary, the lead opinion, and separate opinions into one file. The
        later caption occurs in the previous opinion's extracted range because
        it has no byline of its own. A court banner is a reliable boundary:
        move that suffix to the next Opinion and lift any immediately prior
        signature images onto the preceding writing.
        """
        for i in range(len(doc.opinions) - 1):
            current = doc.opinions[i]
            boundary = next(
                (n for n, block in enumerate(current.blocks) if self._is_wash_banner(block)),
                None,
            )
            if boundary is None:
                continue
            before = current.blocks[:boundary]
            caption = current.blocks[boundary:]
            while before and before[-1].kind == "image":
                image = before.pop()
                current.signature.insert(0, {"__image__": True, **image.payload})
            current.blocks = before
            next_op = doc.opinions[i + 1]
            next_op.caption = caption + list(getattr(next_op, "caption", []) or [])

    def _remove_cid_furniture(self, doc):
        """Remove standalone unmapped-glyph runs from rendered sections.

        These runs occur after signature rules in the Wash Supreme Court's
        text layer. The base extractor has already accounted for the source
        line while building the (spurious) footnote, so record it in the
        Removed bucket before removing that footnote from the model.
        """
        dropped = []

        def clean_blocks(blocks):
            kept = []
            for block in blocks:
                text = str(block.text or "")
                if self._CID_FURNITURE.fullmatch(text):
                    dropped.append(text.strip())
                    continue
                kept.append(block)
            return kept

        for op in doc.opinions:
            op.blocks = clean_blocks(op.blocks)
            kept_fns = []
            for fn in op.footnotes:
                paragraphs = []
                for tag, text in fn.paragraphs:
                    if self._CID_FURNITURE.fullmatch(str(text or "")):
                        dropped.append(str(text).strip())
                    else:
                        paragraphs.append((tag, text))
                if paragraphs:
                    fn.paragraphs = paragraphs
                    kept_fns.append(fn)
                else:
                    # A '?' label with no prose is the parser's unmistakable
                    # signature that this was a CID-only phantom footnote.
                    dropped.append(fn.label)
            op.footnotes = kept_fns

        if dropped:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [x for x in dict.fromkeys(dropped) if x not in have]

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
        opinion missing' root cause). Returns the topmost qualifying rule.

        The size comparison must be LOCAL — the type just above the rule
        against the type just below it. Measuring 'body size' as the modal
        size over the whole page inverts on exactly the pages that matter:
        a page carrying four long footnotes runs 921 chars of 13pt note
        against 751 chars of 14pt body (state_v._thompson p29), so the page
        mode IS the footnote size and the real separator reads as 'not
        smaller than body'. That single statistic lost footnotes in 28 of 50
        wash documents. ``_rule_over_notes`` measures the two bands around
        the rule instead, which is both correct here and still rejects a
        caption shelf (caption text above and byline below are the same
        size, so nothing drops).

        Divisions that set footnotes at body size (washctapp) opt into the
        shared structural test instead."""
        if self.footnote_sep_structural:
            return self._footnote_sep_structural(page)

        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        pw, cutoff = page.width, page.height * 0.45
        # A footnote long enough to fill the page pushes the NEXT page's rule
        # far up it — in_re_dependency_of_c.j.j.i. p16 sets its rule at y=259
        # of 792 and state_v._magana-arevalo p25 at y=295, both well above the
        # usual band, and both lost their zone to the position test alone. The
        # band is therefore extended upward, and a candidate found in the
        # extension has to earn it (``_sets_a_note_column``).
        reach = page.height * 0.25

        cands = []  # tops of thin, left-anchored horizontal rules, lower page
        for r in list(page.rects) + list(page.lines):
            if (
                abs(r["bottom"] - r["top"]) < 2.5
                and abs(r["x1"] - r["x0"]) >= 60
                and min(r["x0"], r["x1"]) < pw * 0.35
                and r["top"] > reach
            ):
                cands.append(r["top"])
        for tl in page.extract_text_lines():  # typed underscore rule
            t = (tl.get("text") or "").strip()
            # Left-anchored, like the drawn rule: Washington types its
            # SIGNATURE rules as underscore runs too, in the right-hand
            # signature column ('__________' at x0~340 over 'Melody, J.'), and
            # they are not footnote separators.
            if (
                len(t) >= 6
                and all(c == "_" for c in t)
                and tl["x0"] < pw * 0.35
                and tl["top"] > reach
            ):
                cands.append(tl["top"])

        # footnote-sized type directly below = a real separator; a caption
        # shelf carries the same body/caption size above and below it
        good = [
            top
            for top in sorted(set(cands))
            if self._rule_over_notes(page, top)
            and not self._has_signature_twin(page, top)
            and (top > cutoff or self._sets_a_note_column(page, top))
        ]
        return min(good) if good else None

    def _has_signature_twin(self, page, rule_top) -> bool:
        """Is ``rule_top`` the left half of a two-column SIGNATURE roster?

        Washington rules off its signature roster in two columns — one rule
        at the body rail and a companion on the same baseline in the right
        half (in_re_recall_of_hobbs p6 draws four such pairs at 51pt pitch).
        The left rule of a pair has exactly the footnote separator's
        geometry, so width and position cannot tell them apart; the
        COMPANION can. A footnote separator never has one."""
        return any(
            abs(r["top"] - rule_top) < 1 and min(r["x0"], r["x1"]) > page.width * 0.5
            for r in list(page.rects) + list(page.lines)
        )

    def _sets_a_note_column(self, page, rule_top) -> bool:
        """Extra corroboration for a rule found ABOVE the usual footnote band.

        High on the page, a thin left-anchored rule is far more often a
        SIGNATURE rule than a footnote separator, so the rule has to be
        followed by something shaped like a footnote column: a footnote
        column is SET SOLID — its lines follow at footnote leading (13.8pt on
        12pt type) — while a signature roster leaves the signing space open
        (a 51-300pt gap between lines)."""
        below = [
            ln
            for ln in page.extract_text_lines()
            if ln["top"] > rule_top and (ln.get("chars") or [])
        ]
        if len(below) < 3:
            return False
        tops = sorted(ln["top"] for ln in below)
        gaps = sorted(b - a for a, b in zip(tops, tops[1:]))
        lead = gaps[len(gaps) // 2]
        sizes = sorted(self._line_type_size(ln["chars"]) for ln in below)
        return lead <= sizes[len(sizes) // 2] * 1.5

    def _rule_over_notes(self, page, rule_top) -> bool:
        """Is ``rule_top`` a footnote separator rather than a caption shelf?

        Read the type on both sides of the rule and require it to DROP.
        Equal type above and below is the caption shelf (caption block above,
        byline below) — the 'first opinion missing' root cause — and is
        always rejected.

        How big a drop counts is not one number, because Washington does not
        set one. Most files drop a full point or more (14.04 body over 12.96
        note, state_v._thompson); j.m.i. drops 12.96 to 12.48, well inside
        the shared test's 0.75pt margin, so requiring that margin alone
        loses its footnote 6. A small drop is real when the typesetter
        corroborates it the other way a footnote zone is marked — a RAISED
        label on the first line beneath the rule (j.m.i.'s '6' at 8.04pt on a
        12.48pt line). So: an unambiguous drop stands on its own; a narrow
        one needs the label."""
        from statistics import median

        above, below = [], []
        for ln in page.extract_text_lines():
            sizes = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
            if not sizes:
                continue
            med = median(sizes)
            if rule_top - 120 <= ln["top"] < rule_top:
                above.append(med)
            elif rule_top < ln["top"] <= rule_top + 200:
                below.append(med)
        if not below:
            return False  # nothing below -> not a separator
        if not above:
            return True  # a page that opens in the footnote zone
        drop = median(above) - median(below)
        if drop <= 0:
            return False
        if drop > 0.75:
            return True
        return self._labelled_note_below(page, rule_top)
