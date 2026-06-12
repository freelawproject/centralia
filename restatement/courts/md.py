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
    @staticmethod
    def _is_order_heading(text: str) -> bool:
        t = text.strip()
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
                if _BANNER in self.line_plain_text(l):
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
                self._md_headnotes = self._styled_headmatter(head).get("summary", [])
        # Maryland centers its caption (banner / docket / parties) on the
        # right-half axis (~x413), not the page center — take that axis from
        # the caption's own underscore divider rule so ``line_alignment``
        # centers those rows instead of reading them as left/right.
        self._md_cap_axis = self._caption_axis(headmatter_segs)
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        # Asterisk-rail order captions fold into a clean two-column block;
        # the centered opinion banner has no '*' token, so it passes through.
        if d.get("summary"):
            d["summary"] = self._fold_asterisk_caption(d["summary"])
        return d

    def _caption_axis(self, segs):
        """Horizontal center of the caption column — the midpoint of its
        full-width underscore divider rule (KAPNECK is bracketed by
        '______' rules spanning x290-537). None if there is no such rule
        (orders use the asterisk rail instead)."""
        best = None
        for seg in segs:
            for l in seg:
                t = self.line_plain_text(l).strip()
                if len(t) >= 12 and set(t) <= set("_"):
                    w = l["x1"] - l["x0"]
                    if best is None or w > best[1]:
                        best = ((l["x0"] + l["x1"]) / 2, w)
        return best[0] if best else None

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

    def _fold_asterisk_caption(self, rows: list) -> list:
        """Fold an order's asterisk-rail caption into one two-column block:
        party lines left of the '*' rail, court/docket lines right. Unlike
        the generic token fold, a wrapped party line with no '*'
        ('COMMISSION') continues the open left column instead of breaking
        it, and blank rows inside the caption are absorbed. A caption with
        no '*' at all (the opinion banner) passes through untouched."""
        import re

        out, left, right = [], [], []
        state = {"open": False}

        def flush():
            if left or right:
                out.append(
                    {"__caption__": True, "left": list(left),
                     "right": list(right), "rail": "*"}
                )
                left.clear()
                right.clear()
            state["open"] = False

        for r in rows:
            if not (isinstance(r, dict) and r.get("__hm__")):
                if r == "" and state["open"]:
                    continue  # blank within the caption — keep folding
                flush()
                out.append(r)
                continue
            text = re.sub("<[^>]+>", "", str(r.get("html", ""))).strip()
            toks = text.split()
            if "*" in toks:
                idx = toks.index("*")
                lpart = " ".join(toks[:idx]).strip()
                rpart = " ".join(t for t in toks[idx + 1 :] if t != "*").strip()
                if lpart:
                    left.append(lpart)
                if rpart:
                    right.append(rpart)
                state["open"] = True
            elif state["open"] and text and (
                text.isupper() or text.rstrip(".") in ("v", "vs") or len(text) <= 24
            ):
                left.append(text)  # wrapped left-column party continuation
            else:
                flush()
                out.append(r)
        flush()
        return out

    # ------------------------------------------------------------- orders
    def find_authors(self, all_segments) -> list:
        self._order_start = None
        self._order_author = None
        starts = super().find_authors(all_segments)
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

    # A long writing byline wraps: 'Concurring and Dissenting Opinion by' on
    # one line, the justice name ('Killough, J.') on the next. Join them so
    # the byline parses — only when the merge actually forms a valid byline,
    # so an ordinary line ending '... Opinion by' can't be swept up.
    def page_lines(self, page):
        lines = super().page_lines(page)
        out, i = [], 0
        while i < len(lines):
            l = lines[i]
            if i + 1 < len(lines) and self.line_plain_text(l).rstrip().endswith(
                "Opinion by"
            ):
                merged = dict(l)
                merged["chars"] = (l.get("chars") or []) + (
                    lines[i + 1].get("chars") or []
                )
                if self._byline_split(merged) is not None:
                    out.append(merged)
                    i += 2
                    continue
            out.append(l)
            i += 1
        return out

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
        doc = super().extract(pdf_path)
        if self._md_dropped:
            doc.dropped = list(doc.dropped) + sorted(set(self._md_dropped))
        if getattr(self, "_md_headnotes", None):
            doc.headnotes = self._md_headnotes
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
            self._harvest_md_signature(doc)
        return doc

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
        Signature section."""
        op = doc.opinions[-1]
        blocks = op.blocks
        if not blocks:
            return
        last = self._untag(blocks[-1].text).strip().lower()
        # The order signs '/s/ <Name>' over a title line; on some orders the
        # title line falls out of the body, leaving '/s/' itself last.
        if not (any(x in last for x in _JUDGE_TITLE) or last.startswith(("/s/", "/s "))):
            return
        take = 1
        for b in reversed(blocks[:-1]):
            t = self._untag(b.text).strip().lower()
            if t.startswith(("/s/", "/s ")):
                take += 1
                break
            if any(x in t for x in _JUDGE_TITLE) or take >= 3:
                break
            take += 1
        sig = blocks[-take:]
        # don't strip a lone non-signature paragraph
        if not any(self._untag(b.text).strip().lower().startswith(("/s/", "/s "))
                   for b in sig):
            return
        doc.signature = [str(b.text) for b in sig]
        op.blocks = blocks[:-take]
