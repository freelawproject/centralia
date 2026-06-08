"""California Court of Appeal.

A different document family from the Alabama appellate courts, so this is a
self-contained extractor rather than a thin subclass. Layout:

  - Page 1: 'Filed M/D/YY' -> 'CERTIFIED FOR PUBLICATION' -> banner
    'IN THE COURT OF APPEAL OF THE STATE OF CALIFORNIA' -> '<N> APPELLATE
    DISTRICT' -> two-column caption (party names left, docket / county / trial
    court no. right) -> body.
  - The author byline is a *signature at the end* ('CHUNG, J.') followed by
    'WE CONCUR:' and the concurring panel — not a byline at the start.
  - Separate concurring/dissenting opinions (when present) open with a
    '<NAME>, J., concurring.' / '... dissenting.' header.

First pass: split headmatter from body, capture the lead opinion + its author
from the end signature, and any separately-authored concur/dissent sections.
Inline emphasis is not yet preserved (plain, escaped text).
"""

from __future__ import annotations

from xml.sax.saxutils import escape

import pdfplumber

from ..base import BaseExtractor
from ..models import Block, DocType, ExtractedDocument, Footnote, Opinion


_ROLE_WORDS = (
    "Plaintiff",
    "Defendant",
    "Appellant",
    "Respondent",
    "Petitioner",
    "Real Party",
    "Cross-",
    "Intervener",
    "Amicus",
    "in Interest",
)


class CaliforniaCourtOfAppeal(BaseExtractor):
    court_id = "calctapp"
    court_label = "Court of Appeal of California."

    # ------------------------------------------------------------------
    _ORDER_CUES = (
        "unmodified opinion attached",
        "order modifying",
        "it is ordered",
        "is modified",
        "petition for rehearing",
    )

    def extract(self, pdf_path: str) -> ExtractedDocument:
        with pdfplumber.open(pdf_path) as pdf:
            n_pages = len(pdf.pages)
            pages = [self._page_lines(p) for p in pdf.pages]  # (body,fns,num)

        doc = ExtractedDocument(
            court_id=self.court_id,
            court_label=self.court_label,
            n_pages=n_pages,
            source_path=pdf_path,
            doc_type=DocType.OPINION,
        )

        # One PDF can hold several distinct documents (e.g. a modification
        # order followed by the opinion). The bottom page number resets at each
        # new document, so split on that.
        segs = self._segments([num for _, _, num in pages])

        def is_order(rng):
            lo, hi = rng
            txt = " ".join(
                ln["text"].lower() for i in range(lo, hi) for ln in pages[i][0][:8]
            )
            return any(cue in txt for cue in self._ORDER_CUES)

        # The primary document (whose caption fills the headmatter) is the
        # opinion — the first segment that is not an order.
        primary = next((k for k, r in enumerate(segs) if not is_order(r)), 0)
        multi = len(segs) > 1

        for si, (s, e) in enumerate(segs):
            seg_bodies = [pages[i][0] for i in range(s, e)]
            seg_fns = [ln for i in range(s, e) for ln in pages[i][1]]
            flat = self._strip_running(seg_bodies)
            if not flat:
                continue
            hm = self._segment_headmatter(flat)
            seg_is_order = is_order((s, e))

            if si == primary:
                # The primary (opinion) caption fills the headmatter box; its
                # body is everything after the caption.
                doc.summary = hm["summary"]
                doc.parties = hm["parties"]
                doc.decision_date = hm["date"]
                doc.docket_number = hm["docket"]
                body = flat[hm["body_start"] :]
            else:
                # Secondary documents (e.g. a leading order) keep their own
                # caption inline so nothing is dropped — there is only one
                # headmatter box, which belongs to the opinion.
                body = flat

            before = len(doc.opinions)
            self._build_opinions(doc, body)
            new_ops = doc.opinions[before:]
            notes = self._collect_footnotes(seg_fns)
            if notes and new_ops:
                new_ops[0].footnotes = notes

            # When the PDF holds multiple documents, label each one and tag a
            # leading order as such.
            if multi and new_ops:
                tag = "ORDER" if seg_is_order else "OPINION"
                label = f"{tag} — Filed {hm['date']}" if hm["date"] else tag
                new_ops[0].blocks.insert(0, Block(kind="heading", text=escape(label)))
                if seg_is_order:
                    for op in new_ops:
                        op.type = "order"

        if not doc.opinions:
            doc.doc_type = DocType.UNKNOWN
        return doc

    @staticmethod
    def _segments(bottom_nums: list) -> list:
        """Split page indices into (start, end) runs, breaking where the bottom
        page number resets (decreases) — the start of a new document."""
        segs = []
        start = 0
        prev = None
        for i, num in enumerate(bottom_nums):
            if num is not None and prev is not None and num < prev:
                segs.append((start, i))
                start = i
            if num is not None:
                prev = num
        segs.append((start, len(bottom_nums)))
        return segs

    # ------------------------------------------------------------------
    def _page_lines(self, page) -> tuple:
        """Return (body_lines, footnote_lines, bottom_page_number). The footnote
        zone is below the separator rule (thin rect at x0~72, width ~144). The
        bottom page number (used to detect a reset = a new document) is the
        bottom-most bare-integer line on the page."""
        sep_y = self._sep_y(page)
        body, fns = [], []
        bottom_num = None
        bottom_top = -1.0
        p1 = page.page_number == 1
        for ln in page.extract_text_lines(layout=False):
            text = (ln.get("text") or "").strip()
            if not text:
                continue
            chars = ln.get("chars") or []
            size = round(max((c.get("size", 0) for c in chars), default=0), 1)
            top = round(ln["top"], 1)
            if text.isdigit() and top > bottom_top:
                bottom_top, bottom_num = top, int(text)
            rec = {
                "text": text,
                "top": top,
                "x0": round(ln["x0"], 1),
                "x1": round(ln["x1"], 1),
                "size": size,
            }
            if p1:  # keep style for the headmatter facsimile
                _sz, font, bold = self.line_meta(ln)
                rec["bold"] = bold
                rec["italic"] = ("Italic" in font) or ("Oblique" in font)
                rec["html"] = self.line_inline_text(ln)
                rec["align"] = self.line_alignment(ln, page.width)
                cx = (ln["x0"] + ln["x1"]) / 2
                rec["centered"] = abs(cx - page.width / 2) < 30
                rec["runs"] = self._hm_runs(ln)
            if sep_y is not None and top >= sep_y:
                if text.isdigit():  # page number below the rule
                    continue
                first = chars[0] if chars else {}
                rec["first"] = first.get("text", "")
                rec["first_size"] = round(first.get("size", size), 1)
                fns.append(rec)
            else:
                body.append(rec)
        return body, fns, bottom_num

    @staticmethod
    def _sep_y(page):
        """Top of the footnote separator rule, or None.

        The divider is a very specific marker: a thin (<2pt) horizontal rule
        exactly ~144pt (2") wide, left-anchored to the text block. Its x0 just
        varies by appellate district (72 or 108) — the width is the tell, so it
        isn't confused with caption boxes or other rules. If several qualify,
        take the lowest (closest to the footnotes)."""

        def ok(x0, w, h):
            return 70 <= x0 <= 115 and 140 <= w <= 150 and h < 2

        cands = [
            round(r["top"], 1)
            for r in page.rects
            if ok(r["x0"], r["x1"] - r["x0"], r["height"])
        ]
        cands += [
            round(ln["top"], 1)
            for ln in page.lines
            if ok(ln["x0"], abs(ln["x1"] - ln["x0"]), abs(ln["bottom"] - ln["top"]))
        ]
        return max(cands) if cands else None

    # Footnote labels can be a superscript digit OR a symbol (the assigned-judge
    # note and similar use ∗ / * / † / ‡ / §).
    _FN_SYMBOLS = "∗*†‡§"

    def _collect_footnotes(self, fn_lines: list) -> list:
        """Group footnote-zone lines into Footnote objects. A new footnote
        starts on a line whose leading char is a superscript digit (smaller
        than the body text) or a footnote symbol; other lines continue the
        current footnote."""
        notes = []
        cur_label = None
        cur_text = []

        def flush():
            if cur_label is not None:
                notes.append(
                    Footnote(
                        label=cur_label,
                        paragraphs=[("p", escape(" ".join(cur_text).strip()))],
                    )
                )

        for fl in fn_lines:
            t = fl["text"]
            digit_label = (
                fl.get("first", "").isdigit()
                and fl.get("first_size", 99) < fl["size"] - 1.5
            )
            symbol_label = t[:1] in self._FN_SYMBOLS
            if digit_label or symbol_label:
                flush()
                if symbol_label:
                    cur_label = t[:1]
                    cur_text = [t[1:].strip()]
                else:
                    k = 0  # split leading label digits off
                    while k < len(t) and t[k].isdigit():
                        k += 1
                    cur_label = t[:k]
                    cur_text = [t[k:].strip()]
            elif cur_label is not None:
                cur_text.append(t)
        flush()
        return notes

    def _strip_running(self, pages: list) -> list:
        """Drop bare page-number lines and the repeated case-name/docket
        footer that appears on most pages."""
        # Count short lines to find repeated footers (case caption / docket).
        from collections import Counter

        freq = Counter()
        for lines in pages:
            for ln in lines:
                if len(ln["text"]) <= 60:
                    freq[ln["text"]] += 1
        repeated = {t for t, c in freq.items() if c >= max(3, len(pages) // 2)}

        flat = []
        for pno, lines in enumerate(pages, 1):
            for ln in lines:
                t = ln["text"]
                if t.isdigit():  # page number
                    continue
                if t in repeated:  # running footer
                    continue
                flat.append((pno, ln))
        return flat

    def _segment_headmatter(self, flat: list) -> dict:
        """Parse the page-1 caption of one document segment. Returns a dict
        with summary / parties / date / docket / body_start (the index in
        ``flat`` where this segment's body begins)."""
        page1 = []  # (idx, rec) for page-1 lines
        last_role = -1
        date = None
        docket = None
        party_cands = []  # (idx, text)
        i = -1
        for idx, (pno, ln) in enumerate(flat):
            if pno > 1:
                break
            t = ln["text"]
            page1.append((idx, ln))
            if date is None and t.lower().startswith("filed"):
                date = t[len("Filed") :].split("(")[0].strip()
            d = self._docket(t)
            if d and docket is None:
                docket = d
            if any(w in t for w in _ROLE_WORDS):
                last_role = idx
            elif self._is_caption_party(t):
                party_cands.append((idx, t))
            i = idx
        body_start = (last_role + 1) if last_role >= 0 else (i + 1)
        return {
            "date": date,
            "docket": docket,
            "parties": [t for idx, t in party_cands if idx < body_start],
            "summary": self._styled_summary(
                [rec for idx, rec in page1 if idx < body_start]
            ),
            "body_start": body_start,
        }

    @staticmethod
    def _hm_runs(ln) -> list:
        """Split a line into (x0, text) runs at wide x-gaps, so the two-column
        caption (parties on the left, docket/court on the right) can be told
        apart from the single-column banner lines. Word spaces are rebuilt from
        the small inter-glyph gaps (pdfplumber omits space glyphs)."""
        chars = sorted((ln.get("chars") or []), key=lambda c: c["x0"])
        if not chars:
            return []
        runs, buf = [], [chars[0]]
        for c in chars[1:]:
            if c["x0"] - buf[-1]["x1"] > 36:
                runs.append(buf)
                buf = [c]
            else:
                buf.append(c)
        runs.append(buf)

        def text(run):
            s, prev = "", None
            for c in run:
                if prev is not None and c["x0"] - prev > 1.5:
                    s += " "
                s += c.get("text", "")
                prev = c["x1"]
            return s.strip()

        return [(round(r[0]["x0"], 1), text(r)) for r in runs]

    def _styled_summary(self, recs: list) -> list:
        """Build a style-preserving headmatter: centered/single banner lines as
        styled rows (relative font size + bold/italic + alignment), and the
        two-column caption as a left/right caption block."""
        sizes = [r["size"] for r in recs if r.get("size")]
        from collections import Counter

        base = Counter(round(s) for s in sizes).most_common(1)[0][0] if sizes else 13
        out, cap_left, cap_right = [], [], []

        def flush_caption():
            if cap_left or cap_right:
                out.append(
                    {"__caption__": True, "left": cap_left[:], "right": cap_right[:]}
                )
                cap_left.clear()
                cap_right.clear()

        seen_banner = False
        for r in recs:
            t = r["text"]
            runs = r.get("runs") or [(r.get("x0", 0), t)]
            if t and all(c in "_-—–" for c in t):
                flush_caption()
                out.append("__DIVIDER__")
                continue
            two_col = len(runs) >= 2 and runs[-1][0] >= 300
            right_only = len(runs) == 1 and runs[0][0] >= 300
            if two_col or right_only:  # caption (has a right column)
                seen_banner = True
                for x0, txt in runs:
                    (cap_right if x0 >= 300 else cap_left).append(txt)
            elif r.get("centered") and len(runs) <= 1:  # centered banner line
                flush_caption()
                seen_banner = True
                out.append(
                    {
                        "__hm__": True,
                        "html": r.get("html", t),
                        "rel": round(r["size"] / base, 3),
                        "align": "C",
                    }
                )
            elif not seen_banner:  # 'Filed ...' above the banner
                out.append(
                    {
                        "__hm__": True,
                        "html": r.get("html", t),
                        "rel": round(r["size"] / base, 3),
                        "align": r.get("align", "L"),
                    }
                )
            else:  # left-column caption line
                cap_left.append(t)
        flush_caption()
        return out

    @staticmethod
    def _is_caption_party(t: str) -> bool:
        # Party-name caption lines are short, title/upper-ish, not sentences.
        return 2 <= len(t.split()) <= 12 and not t.endswith(".") and t.upper() == t

    @staticmethod
    def _docket(t: str) -> str | None:
        """California Court of Appeal docket: one uppercase letter + 6 digits
        (e.g. 'H052612'). Scan tokens; no regex."""
        for tok in t.replace(",", " ").split():
            if len(tok) == 7 and "A" <= tok[0] <= "Z" and tok[1:].isdigit():
                return tok
        return None

    # ------------------------------------------------------------------
    def _build_opinions(self, doc: ExtractedDocument, body: list) -> None:
        """Split body into opinions and emit paragraph blocks.

        Completeness first: every body line is RETURNED somewhere — the
        signature, 'We concur:' line, the panel of justices, and any trailing
        counsel block all stay in the opinion body so we can verify nothing was
        dropped. Author/panel are read off (not removed): each opinion's author
        is the signature just before its 'We concur:'; separately-authored
        opinions open with a '<NAME>, J., concurring.' header."""
        # The reporter's ending matter (trial court / trial judge / counsel)
        # closes the document — route it to the trailer ('Ending matter'),
        # not the opinion body. It always opens with 'Trial Court:'.
        em = next(
            (
                i
                for i, (_p, ln) in enumerate(body)
                if ln["text"].strip().lower().startswith("trial court")
            ),
            None,
        )
        if em is not None:
            self._set_trailer(doc, body[em:])
            body = body[:em]

        texts = [ln["text"] for _, ln in body]
        n = len(texts)
        concur_idxs = [
            i
            for i, t in enumerate(texts)
            if t.strip().lower().rstrip(":") == "we concur"
        ]

        # Section starts: 0 (lead) plus each separate-opinion header.
        headers = {
            i: self._separate_header(t)
            for i, t in enumerate(texts)
            if self._separate_header(t)
        }
        starts = [0] + sorted(headers)
        panel = []
        segments = []  # (type, author, body_lines)

        for s_i, start in enumerate(starts):
            end = starts[s_i + 1] if s_i + 1 < len(starts) else n
            if start in headers:
                op_type, author = headers[start]
                seg_lines = body[start + 1 : end]  # header shown as the author
            else:
                op_type, author = "majority", None
                seg_lines = body[start:end]
            # Read off (don't remove) the author and panel for this section.
            c = next((c for c in concur_idxs if start <= c < end), None)
            if c is not None:
                if author is None:
                    for j in range(c - 1, start - 1, -1):
                        sig = self._signature(texts[j])
                        if sig:
                            author = sig
                            break
                for j in range(c + 1, end):  # panel names after 'We concur:'
                    nm = self._signature(texts[j])
                    if not nm:
                        break
                    panel.append(nm)
            elif author is None:
                # No 'We concur:' line — California sometimes just stacks the
                # signatures (author first, then the joining panel).
                sigs = [
                    s
                    for s in (self._signature(texts[j]) for j in range(start, end))
                    if s
                ]
                if sigs:
                    author = sigs[0]
                    panel.extend(sigs[1:])
            segments.append((op_type, author, seg_lines))

        doc.panel = panel
        if panel:
            doc.judges = ", ".join(panel)

        for op_type, author, lines in segments:
            blocks = self._paragraphs([ln for _, ln in lines])
            if not blocks and not author:
                continue
            doc.opinions.append(
                Opinion(
                    type=op_type or "majority",
                    author=author or "",
                    blocks=blocks,
                )
            )

    def _set_trailer(self, doc: ExtractedDocument, trailer_body: list) -> None:
        """Add the reporter's ending matter (trial court / counsel) to the
        trailer, dropping the repeated case-name / docket running footer."""
        docket = doc.docket_number
        lines = []
        for _p, ln in trailer_body:
            t = ln["text"].strip()
            if not t:
                continue
            if docket and t == docket:  # docket running footer
                continue
            if (
                " v. " in t
                and len(t) <= 60  # case-name footer
                and not t.endswith((".", ":", ","))
            ):
                continue
            lines.append(t)
        if lines:
            doc.trailer = list(doc.trailer) + lines

    @staticmethod
    def _signature(t: str) -> str | None:
        """A signature line: 'NAME, J.' / 'NAME, P. J.' / 'NAME, Acting P.J.'
        possibly with a trailing footnote mark. Returns the cleaned line."""
        s = t.rstrip("*∗†‡ ").strip()
        if not s.endswith("."):
            return None
        upper = s.upper()
        if (
            upper.endswith(", J.")
            or upper.endswith(", P. J.")
            or upper.endswith(", P.J.")
            or upper.endswith("ACTING P.J.")
            or upper.endswith("ACTING P. J.")
            or upper.endswith(", C. J.")
        ):
            # Must look like a name (mostly letters), short.
            if len(s.split()) <= 5:
                return s
        return None

    @staticmethod
    def _separate_header(t: str) -> tuple | None:
        """A separately-authored section header: '<NAME>, J., concurring.' or
        '... dissenting.' Returns (type, author) or None."""
        low = t.lower().rstrip(". ")
        if low.endswith("concurring"):
            return ("concurrence", t.strip())
        if low.endswith("dissenting"):
            return ("dissent", t.strip())
        if low.endswith("concurring and dissenting"):
            return ("concurring-in-part-and-dissenting-in-part", t.strip())
        return None

    # A vertical gap larger than this (pt) starts a new paragraph — separates
    # the distinct counsel/trial-court entries in the trailing block, which are
    # single-spaced within an entry but spaced further apart between entries.
    _PARA_GAP = 26.0

    def _paragraphs(self, lines: list) -> list:
        """Group body lines into paragraph / heading blocks, splitting on a
        first-line indent OR a larger-than-normal vertical gap so distinct
        entries aren't merged together."""
        if not lines:
            return []
        left = min(ln["x0"] for ln in lines)
        blocks = []
        buf = []
        prev_top = None

        def flush():
            if buf:
                text = " ".join(escape(x["text"]) for x in buf)
                blocks.append(Block(kind="p", text=text))
                buf.clear()

        for ln in lines:
            t = ln["text"]
            top = ln["top"]
            # gap to the previous line (None across a page break, where top
            # resets to a smaller value)
            gap = top - prev_top if prev_top is not None and top >= prev_top else None
            indented = ln["x0"] > left + 12
            short = len(t.split()) <= 6
            if short and self._is_heading(t):
                flush()
                blocks.append(Block(kind="heading", text=escape(t)))
                prev_top = top
                continue
            if buf and (indented or (gap is not None and gap > self._PARA_GAP)):
                flush()
            buf.append(ln)
            prev_top = top
        flush()
        return blocks

    @staticmethod
    def _is_heading(t: str) -> bool:
        s = t.strip()
        # Roman-numeral / lettered section headings, or short ALL-CAPS lines.
        head = s.rstrip(".")
        first = (
            head.split(".")[0]
            if "." in head
            else head.split()[0] if head.split() else ""
        )
        roman = set("IVXLC")
        if first and all(c in roman for c in first):
            return True
        if len(head) <= 40 and head.upper() == head and any(c.isalpha() for c in head):
            return True
        return False
