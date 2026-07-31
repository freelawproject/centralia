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
    # A California Court of Appeal caption names the document in the RIGHT
    # column of the two-column caption block ('ORDER MODIFYING OPINION',
    # 'ORDER CERTIFYING OPINION FOR PUBLICATION', 'ORDER DENYING PETITION FOR
    # REHEARING'). That title, plus the order's operative sentence, is what
    # tells a stapled administrative order from the opinion it modifies.
    _ORDER_CUES = (
        "unmodified opinion attached",
        "unmodified opn",
        "order modifying",
        "order certifying",
        "order denying",
        "order granting",
        "certifying opinion",
        "it is ordered",
        "is ordered certified",
        "is modified",
        "no change in judgment",
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

        # The court-printed folio, physical page -> printed number. Registered
        # before the folio LINES are stripped as furniture, so ``page_marker``
        # can put the number back into the body.
        self._printed_folio_by_page = {
            i: num for i, (_, _, num) in enumerate(pages, 1) if num is not None
        }

        # One PDF can hold several distinct documents (e.g. a modification
        # order followed by the opinion). The bottom page number resets at each
        # new document, so split on that.
        segs = self._segments([num for _, _, num in pages])

        def is_order(rng):
            # Read the whole FIRST page of the segment: the caption's document
            # title sits in the right column, well past the first few lines.
            lo, _hi = rng
            txt = " ".join(ln["text"].lower() for ln in pages[lo][0])
            return any(cue in txt for cue in self._ORDER_CUES)

        # The primary document (whose caption fills the headmatter) is the
        # opinion — the first segment that is not an order.
        primary = next((k for k, r in enumerate(segs) if not is_order(r)), 0)
        multi = len(segs) > 1

        for si, (s, e) in enumerate(segs):
            seg_bodies = [pages[i][0] for i in range(s, e)]
            seg_fns = [ln for i in range(s, e) for ln in pages[i][1]]
            flat, furniture = self._strip_running(seg_bodies, page_offset=s)
            if not flat:
                continue
            if furniture:
                doc.dropped = list(doc.dropped) + furniture
            hm = self._segment_headmatter(flat, first_page=s + 1)
            seg_is_order = is_order((s, e))

            if si == primary:
                # The primary (opinion) caption fills the headmatter box; its
                # body is everything after the caption.
                doc.summary = hm["summary"]
                doc.parties = hm["parties"]
                doc.decision_date = hm["date"]
                doc.docket_number = hm["docket"]
                body = flat[hm["body_start"] :]
                secondary_caption = []
            else:
                # There is only one document-level headmatter box, belonging
                # to the primary opinion. Keep an attached order's repeated
                # caption with that order in ``Opinion.caption`` instead of
                # flattening it into malformed body paragraphs.
                secondary_caption = flat[: hm["body_start"]]
                body = flat[hm["body_start"] :]

            before = len(doc.opinions)
            self._build_opinions(doc, body)
            new_ops = doc.opinions[before:]
            if secondary_caption and new_ops:
                new_ops[0].caption = self._caption_blocks(secondary_caption)
            notes = self._collect_footnotes(seg_fns)
            if notes and new_ops:
                new_ops[0].footnotes = notes

            # When the PDF holds multiple documents, label each one and tag a
            # leading order as such.
            if multi and new_ops:
                tag = "ORDER" if seg_is_order else "OPINION"
                label = f"{tag} — Filed {hm['date']}" if hm["date"] else tag
                # The label belongs to the page the segment opens on, so it
                # doesn't read as a block of unknown provenance.
                new_ops[0].blocks.insert(
                    0,
                    Block(kind="heading", text=escape(label), page=s + 1),
                )
                if seg_is_order:
                    for op in new_ops:
                        op.type = "order"

        if not doc.opinions:
            doc.doc_type = DocType.UNKNOWN
        elif all(op.type == "order" for op in doc.opinions):
            # The whole PDF is an administrative order, not an opinion.
            doc.doc_type = DocType.ORDER
        return doc

    def _caption_blocks(self, rows: list) -> list:
        """Loss-resistant caption blocks for an attached order/opinion."""
        blocks = []
        for pno, line in rows:
            text = line["text"].strip()
            if not text or (len(text) <= 3 and not text.strip(")|§: ")):
                continue
            kind = (
                "heading"
                if line.get("centered") and line.get("bold")
                else "p"
            )
            blocks.append(Block(kind=kind, text=escape(text), page=pno))
        return blocks

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
        pending_label = None
        for ln in page.extract_text_lines(layout=False):
            text = (ln.get("text") or "").strip()
            if not text:
                continue
            chars = ln.get("chars") or []
            size = round(max((c.get("size", 0) for c in chars), default=0), 1)
            top = round(ln["top"], 1)
            fn_zone = sep_y is not None and top >= sep_y
            # A left-margin bare digit inside the footnote zone is a footnote
            # label, not the bottom page number.
            if text.isdigit() and top > bottom_top and not (
                fn_zone and round(ln["x0"], 1) < 250
            ):
                bottom_top, bottom_num = top, int(text)
            rec = {
                "text": text,
                "top": top,
                "x0": round(ln["x0"], 1),
                "x1": round(ln["x1"], 1),
                "size": size,
                "page_height": round(page.height, 1),
                "_chars": chars,
            }
            # Any physical page can open an attached opinion/order segment.
            # Preserve style/runs on every page so that segment's own caption
            # can be reconstructed, not only the PDF's physical page 1.
            _sz, font, bold = self.line_meta(ln)
            rec["bold"] = bold
            rec["italic"] = ("Italic" in font) or ("Oblique" in font)
            rec["html"] = self.line_inline_text(ln)
            rec["align"] = self.line_alignment(ln, page.width)
            cx = (ln["x0"] + ln["x1"]) / 2
            rec["centered"] = abs(cx - page.width / 2) < 30
            rec["runs"] = self._hm_runs(ln)
            if fn_zone:
                # A bare-integer line below the rule is either the centred
                # bottom page number (x0 out at the page axis, ~300pt) or a
                # footnote LABEL that the PDF sets on its own raised baseline
                # at the text margin. Only the former is furniture; the latter
                # belongs to the footnote line that follows it.
                if text.isdigit():
                    if rec["x0"] >= 250:  # centred page number
                        continue
                    pending_label = text
                    continue
                first = chars[0] if chars else {}
                rec["first"] = first.get("text", "")
                rec["first_size"] = round(first.get("size", size), 1)
                # Structural label cue: leading digit run set smaller than the
                # line, or on a baseline raised above the following glyph.
                rec["label"] = pending_label
                if pending_label is None:
                    rec["label"] = self._inline_label(chars, size)
                pending_label = None
                fns.append(rec)
            else:
                body.append(rec)
        return self._rejoin_raised_body_digits(body), fns, bottom_num

    def _rejoin_raised_body_digits(self, lines: list) -> list:
        """Attach a raised standalone footnote mark to its body line.

        Some California PDFs put a same-size superscript on its own baseline,
        about 3pt above the prose line it annotates. It is not a bare folio:
        geometrically it sits inside (or immediately after) that line's
        horizontal span. Preserve it as an inline ``footnotemark`` token.
        """
        absorbed = set()
        for i, mark in enumerate(lines):
            label = mark["text"].strip()
            if not label.isdigit() or mark["top"] > mark.get("page_height", 792) - 90:
                continue
            candidates = []
            for j, host in enumerate(lines):
                if i == j or host["text"].strip().isdigit():
                    continue
                rise = host["top"] - mark["top"]
                if not 0 < rise <= 5:
                    continue
                if not host["x0"] - 2 <= mark["x0"] <= host["x1"] + 3:
                    continue
                candidates.append((rise, j, host))
            if not candidates:
                continue
            _rise, j, host = min(candidates)
            chars = list(host.get("_chars") or [])
            mark_chars = [dict(c, text="\ue000") for c in (mark.get("_chars") or [])]
            merged = dict(host)
            merged["chars"] = sorted(chars + mark_chars, key=lambda c: c.get("x0", 0))
            host["text"] = self.line_plain_text(merged)
            host.setdefault("_footnote_labels", []).append(label)
            absorbed.add(i)
        return [line for i, line in enumerate(lines) if i not in absorbed]

    @staticmethod
    def _inline_label(chars: list, size: float) -> str | None:
        """The footnote number when it is set INLINE at the head of the line.
        It is a leading digit run distinguished from the prose either by a
        smaller size (a true superscript) or by a raised baseline (same size,
        lifted off the line) — never by what the digits say."""
        if not chars or not chars[0].get("text", "").isdigit():
            return None
        small = round(chars[0].get("size", size), 1) < size - 1.5
        raised = False
        for c in chars[1:]:
            if c.get("text", "").isdigit():
                continue
            raised = c.get("bottom", 0) - chars[0].get("bottom", 0) > 1
            break
        if not (small or raised):
            return None
        k = 0
        while k < len(chars) and chars[k].get("text", "").isdigit():
            k += 1
        return "".join(c.get("text", "") for c in chars[:k])

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
            digit_label = fl.get("label")
            # A symbol label is a SINGLE raised/small glyph followed by prose —
            # not a run of section signs opening a continuation line ('§§ 452').
            symbol_label = (
                t[:1] in self._FN_SYMBOLS
                and t[1:2] not in self._FN_SYMBOLS
                and fl.get("first_size", 99) < fl["size"] - 1.5
            )
            if digit_label or symbol_label:
                flush()
                if symbol_label:
                    cur_label = t[:1]
                    cur_text = [t[1:].strip()]
                else:
                    cur_label = digit_label
                    # The label may be set inline (strip it off the prose) or on
                    # its own preceding baseline (prose starts clean).
                    body = t[len(digit_label) :] if t.startswith(digit_label) else t
                    cur_text = [body.strip()]
            elif cur_label is not None:
                cur_text.append(t)
            else:
                # Footnote-zone prose with no label yet (a footnote continued
                # from the previous page). Keep it — never silently drop.
                cur_label = ""
                cur_text = [t]
        flush()
        return notes

    # Running head / footer band: a repeated case-name or docket line lives in
    # the page's top or bottom margin. Body text never does.
    _RUN_TOP = 100.0
    _RUN_BOTTOM = 680.0

    def _strip_running(self, pages: list, page_offset: int = 0) -> tuple:
        """Return (flat, furniture).

        ``flat`` is [(physical_page, line)] with the bare page-number lines and
        the repeated case-name/docket footer removed; ``furniture`` is the
        removed footer text, for the Removed box. The folio's VALUE is not
        discarded with its line — ``extract`` registers it in
        ``_printed_folio_by_page`` so it comes back as a ``<pagenumber/>``
        marker inside the body, the same as every other court.

        The repetition test is confined to the running-head/footer BAND. A
        conformed-signature marker ('/s/') or a stacked signature name repeats
        just as often as a footer does, but it sits in the middle of the page —
        counting it as furniture deleted real content."""
        from collections import Counter

        freq = Counter()
        for lines in pages:
            for ln in lines:
                if len(ln["text"]) <= 60 and (
                    ln["top"] < self._RUN_TOP or ln["top"] > self._RUN_BOTTOM
                ):
                    freq[ln["text"]] += 1
        repeated = {t for t, c in freq.items() if c >= max(3, len(pages) // 2)}

        flat = []
        furniture = []
        for pno, lines in enumerate(pages, 1 + page_offset):
            for ln in lines:
                t = ln["text"]
                folio = getattr(self, "_printed_folio_by_page", {}).get(pno)
                near_bottom = ln["top"] > ln.get("page_height", 792.0) - 90
                if (
                    t.isdigit()
                    and folio is not None
                    and int(t) == folio
                    and near_bottom
                    and ln["x0"] >= 250
                ):  # folio — carried as a page marker instead
                    continue
                # Some filed modification orders carry a tiny compositor's
                # initial in the extreme lower-left trim area ('jl'). It is
                # page furniture, not the order's final paragraph.
                marginal_mark = (
                    near_bottom
                    and ln["x0"] < 60
                    and ln["x1"] - ln["x0"] < 30
                    and len(t) <= 4
                    and t.isalpha()
                )
                if marginal_mark:
                    furniture.append(t)
                    continue
                if t in repeated and (
                    ln["top"] < self._RUN_TOP or ln["top"] > self._RUN_BOTTOM
                ):  # running head / footer
                    furniture.append(t)
                    continue
                # The page a line came from is content, not scratch state: the
                # blocks built from it carry it as ``Block.page`` and use it to
                # place page markers.
                ln["page"] = pno
                flat.append((pno, ln))
        return flat, furniture

    def _segment_headmatter(self, flat: list, first_page: int = 1) -> dict:
        """Parse the caption on the FIRST page of one document segment. Returns
        a dict with summary / parties / date / docket / body_start (the index in
        ``flat`` where this segment's body begins).

        ``flat`` carries physical page numbers, so a second segment's caption
        opens at its own first page rather than at page 1."""
        page1 = []  # (idx, rec) for caption-page lines
        last_role = -1
        date = None
        docket = None
        party_cands = []  # (idx, text)
        i = -1
        # The caption page's own measure. A role word inside a FULL-measure
        # wrapping line is body prose that happens to say 'Plaintiff'
        # (chemical_toxin opens 'Plaintiff filed a complaint against
        # defendants…' right on page 1, and the role scan dragged body_start
        # past the whole first page of the opinion). A caption or counsel role
        # line stops short of the measure.
        p1_lines = [ln for pno, ln in flat if pno == first_page]
        p1_left = min((ln.get("x0") or 0.0 for ln in p1_lines), default=0.0)
        p1_measure = max(
            ((ln.get("x1") or 0.0) - p1_left for ln in p1_lines), default=0.0
        )
        for idx, (pno, ln) in enumerate(flat):
            if pno > first_page:
                break
            t = ln["text"]
            page1.append((idx, ln))
            if date is None and t.lower().startswith("filed"):
                date = t[len("Filed") :].split("(")[0].strip()
            d = self._docket(t)
            if d and docket is None:
                docket = d
            # 'Short of the measure' is an absolute half-inch, matching the
            # full-line rule in _measure_doc_geometry: a counsel line's last
            # row stops visibly short; body prose runs to the margin.
            short_of_measure = (
                not p1_measure
                or (ln.get("x1") or 0.0) <= p1_left + p1_measure - 36
            )
            if any(w in t for w in _ROLE_WORDS) and short_of_measure:
                last_role = idx
            elif self._is_caption_party(t):
                # Keep only the left caption column. A merged PDF row can also
                # carry the brace rail and docket on the right; centered court
                # banners and right-only document titles are not parties.
                left_runs = [
                    txt
                    for x0, txt in (ln.get("runs") or [])
                    if x0 < 300 and txt.strip(")| ")
                ]
                cand = left_runs[0] if left_runs else t
                cand = cand.rstrip(")| ").strip()
                if (
                    cand
                    and not ln.get("centered")
                    and ln.get("x0", 999) < 200
                    and self._is_caption_party(cand)
                ):
                    party_cands.append((idx, cand))
            i = idx
        body_start = (last_role + 1) if last_role >= 0 else (i + 1)
        # A long counsel block wraps onto the next page (osborne: '…for
        # Defendant and Respondent.' opens page 2; mata's amicus roster runs
        # eight lines before its 'Appellant.'). Follow it paragraph by
        # paragraph: consume a run up to its short last line, and claim the
        # run for the caption only when that line ENDS on a role word — the
        # signature of a counsel entry. A body paragraph that merely mentions
        # 'Plaintiff' ends on ordinary prose and stops the walk.
        role_end = {
            "Appellant", "Appellants", "Respondent", "Respondents",
            "Petitioner", "Petitioners", "Defendant", "Defendants",
            "Plaintiff", "Plaintiffs", "Intervener", "Interveners",
            "Interest", "Curiae",
        }
        def role_period_end(k):
            words = flat[k][1]["text"].split()
            return (
                bool(words)
                and words[-1].endswith(".")
                and words[-1].strip(".,;") in role_end
            )

        while body_start < len(flat):
            end = next(
                (
                    k
                    for k in range(body_start, min(body_start + 12, len(flat)))
                    if flat[k][0] <= first_page + 1 and role_period_end(k)
                ),
                None,
            )
            if end is None:
                break
            body_start = end + 1
        # Rows the extension claimed join the caption facsimile.
        seen = {idx for idx, _ in page1}
        page1.extend(
            (idx, flat[idx][1]) for idx in range(body_start) if idx not in seen
        )
        # A glyph divider closing the caption page ('* * * * * *' between the
        # counsel block and the body) is headmatter furniture, not the
        # opinion's first paragraph. Extend the caption over any such rows.
        while (
            body_start < len(flat)
            and flat[body_start][0] <= first_page + 1
            and (txt := flat[body_start][1]["text"].strip())
            and set(txt) <= set("*-_—–· ")
        ):
            body_start += 1
        # The brace/parenthesis rail is sometimes emitted one row below the
        # final role line.  It still belongs to the caption even though it has
        # no left- or right-column text of its own.  Consume only pure rail
        # glyphs on the caption page; the first substantive order/opinion line
        # remains the body boundary.
        while body_start < len(flat):
            pno, rec = flat[body_start]
            compact = "".join(rec["text"].split())
            if pno != first_page or not compact or any(
                ch not in ")(|§:" for ch in compact
            ):
                break
            body_start += 1
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
        cap_rail = None
        cap_rail_rows = 0

        # The caption page's own measure, so 'centered' and 'runs to the right
        # margin' are judged against this page rather than the paper.
        xs0 = [r["x0"] for r in recs if r.get("x0") is not None]
        xs1 = [r["x1"] for r in recs if r.get("x1") is not None]
        left_margin = min(xs0) if xs0 else 72.0
        measure = (max(xs1) - left_margin) if xs1 else 0.0

        def has_right_column(r):
            runs = r.get("runs") or [(r.get("x0") or 0.0, r.get("text", ""))]
            return runs[-1][0] >= 300

        def wraps_to_margin(i):
            """True when the next line sits back on the left margin — the
            signature of a wrapped prose entry, which is what tells full-width
            prose apart from a full-width centered banner."""
            nxt = recs[i + 1] if i + 1 < len(recs) else None
            return nxt is not None and (nxt.get("x0") or 0.0) <= left_margin + 3

        def is_centered(r, i):
            """Centering is a BOTH-margin fact, not a midpoint fact.

            A full-measure line whose first line is indented also puts its
            midpoint on the page axis — marriage_of_g.e.'s 'APPEAL from an
            order…' runs 108-510 inside a 72-525 measure, midpoint 309 against
            an axis of 306 — so on the midpoint alone the entire provenance and
            counsel block read as centered banner rows. A short line on the
            axis is a banner outright; a full-measure one is a banner only if
            it does NOT wrap ('IN THE COURT OF APPEAL OF THE STATE OF
            CALIFORNIA' fills husband's 396pt measure edge-to-edge yet is a
            banner — the next row is another centered banner line, not a
            margin-set continuation)."""
            if not r.get("centered"):
                return False
            width = (r.get("x1") or 0.0) - (r.get("x0") or 0.0)
            if not measure or width <= 0.80 * measure:
                return True
            return not wraps_to_margin(i)

        def wraps_measure(r):
            """True when a line runs out to the right measure — prose, not a
            caption column entry."""
            return bool(measure) and (r.get("x1") or 0.0) >= left_margin + 0.80 * measure

        # The provenance / counsel block closing a California caption is
        # left-set prose: each entry opens on a first-line indent and wraps back
        # to the margin. It is not caption-column material, and its
        # continuations must not be orphaned into rows of their own ('for' /
        # 'Appellant.' on separate lines). Everything from the first such line
        # to the end of the caption page is that block.
        prose_start = next(
            (
                i
                for i, r in enumerate(recs)
                if not has_right_column(r)
                and not is_centered(r, i)
                and wraps_measure(r)
                and (r.get("x0") or 0.0) > left_margin + 12
            ),
            None,
        )
        prose_row = None

        pending_gap = False

        def flush_caption():
            nonlocal cap_rail, cap_rail_rows, pending_gap
            if cap_left or cap_right:
                item = {
                    "__caption__": True,
                    "left": cap_left[:],
                    "right": cap_right[:],
                }
                if cap_rail:
                    item["rail"] = cap_rail
                    item["rail_rows"] = cap_rail_rows
                out.append(item)
                cap_left.clear()
                cap_right.clear()
                cap_rail = None
                cap_rail_rows = 0
            # A real gap seen while the caption block was still accumulating
            # belongs after the block — the caption is one unit; the blank row
            # separates it from what follows.
            if pending_gap:
                out.append("")
                pending_gap = False

        # Whitespace carries meaning: a gap clearly larger than the caption
        # page's own modal lead is a real blank row (banner → caption →
        # provenance → counsel), and the facsimile keeps it. Measured, not
        # assumed — this page mixes leads (31pt caption rows over 18.7pt
        # wrapped counsel prose), so the modal lead is the yardstick.
        lead_counts = Counter()
        for a, b in zip(recs, recs[1:]):
            if a.get("top") is not None and b.get("top") is not None:
                gap = round(b["top"] - a["top"])
                if 5 < gap < 80:
                    lead_counts[gap] += 1
        modal_lead = lead_counts.most_common(1)[0][0] if lead_counts else None

        def gap_before(i):
            if not modal_lead or i == 0:
                return False
            prev, cur = recs[i - 1], recs[i]
            if prev.get("top") is None or cur.get("top") is None:
                return False
            return (cur["top"] - prev["top"]) > 1.45 * modal_lead

        seen_banner = False
        for i, r in enumerate(recs):
            t = r["text"]
            # Blank row for a real gap. While the two-column caption block is
            # accumulating, hold the gap — it is emitted after the block
            # (flush_caption), keeping the block's internal rhythm as one unit.
            if gap_before(i):
                if cap_left or cap_right:
                    pending_gap = True
                else:
                    out.append("")
            # Divider rows outrank the prose block — the '* * * * * *' closing
            # a caption page sits BELOW the counsel entries, where the prose
            # branch would swallow it as a counsel continuation. An
            # underscore/dash row is a drawn-look rule (__DIVIDER__); a glyph
            # row ('* * *') is typed content and stays literal, centered as
            # printed — never promote glyphs to a rule the PDF didn't draw.
            if t and set(t) <= set("_-—– ") and len(t.replace(" ", "")) >= 3:
                flush_caption()
                prose_row = None
                out.append("__DIVIDER__")
                continue
            if t and set(t) <= set("*·• ") and t.replace(" ", ""):
                flush_caption()
                prose_row = None
                seen_banner = True
                out.append(
                    {
                        "__hm__": True,
                        "html": escape(t),
                        "rel": round(r["size"] / base, 3) if r.get("size") else 1.0,
                        "align": "C" if r.get("centered") else "L",
                    }
                )
                continue
            if prose_start is not None and i >= prose_start:
                indent = (r.get("x0") or 0.0) - left_margin
                if prose_row is None or indent > 12:
                    flush_caption()
                    seen_banner = True
                    prose_row = {
                        "__hm__": True,
                        "html": r.get("html", t),
                        "rel": round(r["size"] / base, 3),
                        "align": "L",
                    }
                    if indent > 12:
                        prose_row["tind"] = round(indent, 1)
                    out.append(prose_row)
                else:  # a wrapped continuation of the entry above
                    prose_row["html"] = f"{prose_row['html']} {r.get('html', t)}"
                continue
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
                    stripped = txt.strip()
                    if x0 >= 300 and stripped and all(c == ")" for c in stripped):
                        cap_rail = ")"
                        cap_rail_rows += len(stripped)
                    else:
                        if x0 >= 300 and stripped.startswith(")"):
                            cap_rail = ")"
                            cap_rail_rows += 1
                            txt = stripped[1:].strip()
                            if not txt:
                                continue
                        (cap_right if x0 >= 300 else cap_left).append(txt)
            elif is_centered(r, i) and len(runs) <= 1:  # centered banner line
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
        # Never end the headmatter on a blank row — a trailing gap separates
        # nothing and reads as invented spacing.
        while out and isinstance(out[-1], str) and not out[-1].strip():
            out.pop()
        return out

    @staticmethod
    def _is_caption_party(t: str) -> bool:
        # Party-name caption lines are short, title/upper-ish, not sentences.
        return 2 <= len(t.split()) <= 12 and not t.endswith(".") and t.upper() == t

    @staticmethod
    def _docket(t: str) -> str | None:
        """California appellate docket from a caption row.

        Published Court of Appeal matters use one letter + six digits
        (``H052612``); appellate divisions use a year + division code + serial
        (``24APLC00316``). Scan tokens structurally, without case-name cues.
        """
        for tok in t.replace(",", " ").split():
            core = tok.strip("()[]:;.")
            if len(core) == 7 and "A" <= core[0] <= "Z" and core[1:].isdigit():
                return core
            if (
                9 <= len(core) <= 14
                and core[:2].isdigit()
                and core.isalnum()
                and sum(c.isalpha() for c in core) >= 3
                and sum(c.isdigit() for c in core) >= 5
                and all(not c.isalpha() or c.isupper() for c in core)
            ):
                return core
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
        # not the opinion body. It is a labelled two-column block that opens
        # the FINAL page with the label row 'Trial Court: <county>'. Both
        # conditions matter: a wrapped body sentence can begin with the words
        # 'trial court' (and does), but never as a label on the last page.
        last_page = body[-1][0] if body else 0
        em = next(
            (
                i
                for i, (p, ln) in enumerate(body)
                if p == last_page
                and ln["text"].split(":")[0].strip().lower() == "trial court"
            ),
            None,
        )
        if em is not None:
            self._set_trailer(doc, body[em:])
            body = body[:em]

        body = self._split_signature_columns(body)
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
        # A separately published concurrence opens with its bracketed short
        # title ('[In re McCowen, E087834]') and then the byline. Those one or
        # two title lines are part of the concurrence, not a phantom opinion of
        # their own, so fold them into the section that follows.
        lead_prefix = []
        if len(starts) > 1 and starts[1] <= 2 and not any(
            self._sig_at(texts, j, starts[1]) for j in range(starts[1])
        ):
            lead_prefix = body[: starts[1]]
            starts = starts[1:]
        panel = []
        segments = []  # (type, author, body_lines)

        for s_i, start in enumerate(starts):
            end = starts[s_i + 1] if s_i + 1 < len(starts) else n
            if start in headers:
                op_type, author = headers[start]
                seg_lines = body[start + 1 : end]  # header shown as the author
                if s_i == 0 and lead_prefix:
                    seg_lines = lead_prefix + seg_lines
            else:
                op_type, author = "majority", None
                seg_lines = body[start:end]
            # Read off (don't remove) the author and panel for this section.
            c = next((c for c in concur_idxs if start <= c < end), None)
            if c is not None:
                if author is None:
                    for j in range(c - 1, start - 1, -1):
                        sig = self._sig_at(texts, j, c)
                        if sig:
                            author = sig[0]
                            break
                j = c + 1  # panel names after 'We concur:'
                while j < end and self.is_rule_text(texts[j], "_"):
                    j += 1
                while j < end:
                    sig = self._sig_at(texts, j, end)
                    if not sig:
                        break
                    panel.append(sig[0])
                    j = sig[1]
            elif author is None:
                # No 'We concur:' line — California sometimes just stacks the
                # signatures (author first, then the joining panel).
                sigs, j = [], start
                while j < end:
                    sig = self._sig_at(texts, j, end)
                    if sig:
                        sigs.append(sig[0])
                        j = sig[1]
                    else:
                        j += 1
                if sigs:
                    author = sigs[0]
                    panel.extend(sigs[1:])
            segments.append((op_type, author, seg_lines))

        combined_panel = list(doc.panel)
        for name in panel:
            if name not in combined_panel:
                combined_panel.append(name)
        doc.panel = combined_panel
        if combined_panel:
            doc.judges = ", ".join(combined_panel)

        for op_type, author, lines in segments:
            blocks = self._paragraphs([ln for _, ln in lines])
            if not blocks and not author:
                continue
            op = Opinion(
                type=op_type or "majority",
                author=author or "",
                blocks=blocks,
            )
            # A page whose paragraphs all START on it gets no inline marker from
            # the cross-page join above; this puts one on its first block so
            # marker presence doesn't depend on paragraph grouping.
            self._ensure_opinion_page_markers(
                op, {p for p, _ln in lines if p is not None}
            )
            doc.opinions.append(op)

    def _split_signature_columns(self, body: list) -> list:
        """Split a same-baseline row of justice signatures into source rows.

        Appellate-division orders often print all three names beneath three
        horizontal rules on one PDF baseline. The wide gaps expose three
        geometric runs even though ``extract_text_lines`` returns one string.
        Splitting only when every run is independently a valid signature keeps
        ordinary widely justified prose untouched.
        """
        out = []
        for pno, line in body:
            runs = line.get("runs") or []
            if len(runs) >= 2 and all(self._signature(t) for _x, t in runs):
                for x0, text in runs:
                    rec = dict(line)
                    rec["text"] = text
                    rec["x0"] = x0
                    rec["runs"] = [(x0, text)]
                    out.append((pno, rec))
            else:
                out.append((pno, line))
        return out

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

    # Title words that may precede the abbreviated judicial title.
    _TITLE_LEADS = ("acting", "presiding", "associate", "senior", "retired")

    @classmethod
    def _is_title_only(cls, t: str) -> bool:
        """A line that is nothing but the abbreviated judicial title — 'J.',
        'P. J.', 'Acting P. J.'. In the stacked signature layout the surname
        sits above the drawn signature rule and the title below it."""
        toks = t.strip().split()
        if not toks or len(toks) > 4 or "." not in t:
            return False
        while toks and toks[0].lower().rstrip(".") in cls._TITLE_LEADS:
            toks = toks[1:]
        core = "".join(toks).replace(".", "")
        return 1 <= len(core) <= 2 and core.isalpha() and core.isupper()

    @staticmethod
    def _is_bare_name(t: str) -> bool:
        """A line that is nothing but a justice's surname as printed under (or
        over) a signature rule — 'HOFFSTADT', 'McKINSTER', 'BOULWARE EURIE',
        'KIM (D.)'. Set in caps, one to three words, no punctuation but the
        parenthesised initial."""
        s = t.strip()
        if not s or "," in s or ":" in s:
            return False
        core = s
        for ch in "().-’'":
            core = core.replace(ch, " ")
        toks = core.split()
        if not 1 <= len(toks) <= 3 or not all(tok.isalpha() for tok in toks):
            return False
        letters = "".join(toks)
        # Caps (a lowercase 'c' in 'McKINSTER' is the only expected exception).
        return len(letters) <= 24 and sum(
            1 for ch in letters if ch.isupper()
        ) >= len(letters) - 2

    def _sig_at(self, texts: list, j: int, end: int) -> tuple | None:
        """Read the justice's signature that begins at line ``j``; returns
        ``(name, next_index)`` or None.

        California draws it three ways, and all three must fold into ONE name:
          1. inline           — 'CHUNG, J.'
          2. rule-then-name   — '______________, P.J.' / 'HOFFSTADT'
          3. name-then-title  — 'RAPHAEL' / 'J.'  (stacked across a drawn rule)
        Reading only form 1 made the underscore RULE the author's name."""
        if j < 0 or j >= end:
            return None
        t = texts[j].strip()
        sig = self._signature(t)
        if sig:
            head, _, title = sig.rpartition(",")
            if head and all(ch == "_" for ch in head.strip()):
                if j + 1 < end and self._is_bare_name(texts[j + 1]):
                    return (f"{texts[j + 1].strip()}, {title.strip()}", j + 2)
                return None
            return (sig, j + 1)
        if self._is_bare_name(t) and j + 1 < end and self._is_title_only(texts[j + 1]):
            return (f"{t}, {texts[j + 1].strip()}", j + 2)
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

    def _fold_signatures(self, lines: list) -> list:
        """Join a stacked signature into one row.

        A conformed signature is drawn across a rule: the surname above it and
        the abbreviated title below ('CODRINGTON' / 'J.'), or the rule itself
        typed with the title ('_________, J.') over the printed name. Left
        split, each half came out as its own one-word heading block — the
        signature read as two stray headings instead of one signature."""
        out, i, n = [], 0, len(lines)
        while i < n:
            a = lines[i]
            b = lines[i + 1] if i + 1 < n else None
            if b is not None:
                at, bt = a["text"].strip(), b["text"].strip()
                pair = None
                if self._is_bare_name(at) and self._is_title_only(bt):
                    pair = f"{at}, {bt}"
                else:
                    sig = self._signature(at)
                    head, _, title = (sig or "").rpartition(",")
                    if (
                        sig
                        and head
                        and all(ch == "_" for ch in head.strip())
                        and self._is_bare_name(bt)
                    ):
                        pair = f"{bt}, {title.strip()}"
                if pair is not None:
                    merged = dict(a)
                    merged["text"] = pair
                    out.append(merged)
                    i += 2
                    continue
            out.append(a)
            i += 1
        return out

    def _paragraphs(self, lines: list) -> list:
        """Build paragraphs and blockquotes from California's line geometry.

        Ordinary prose uses x≈72 with a first-line indent at x≈108. Hanging
        list continuations can run deeper (x≈126), while displayed quotations
        hold a stable inset across consecutive wrapped lines and usually pull
        in the right margin too. Those are different structures: a continuation
        must stay with its list item, and a quote must not become one paragraph
        per physical line.
        """
        if not lines:
            return []
        lines = self._fold_signatures(lines)
        left = min(ln["x0"] for ln in lines)
        # Measure the paragraph-break threshold from the document's OWN body
        # lead instead of trusting the absolute constant. The first line of a
        # page sits slightly high on the grid, so the gap from it to the second
        # line exceeds the steady lead (eagle_colton page 2: 26.5pt against a
        # 23.4pt lead) — read against a fixed 26pt that broke the opinion's
        # opening sentence in half at every page turn.
        lead = self._body_lead(lines)
        gap_max = lead * 1.35 if lead else self._PARA_GAP
        right = max(ln["x1"] for ln in lines)
        quote_flags = self._blockquote_flags(lines, left, right, lead)
        quote_lead = self._flagged_lead(lines, quote_flags) or lead
        quote_gap_max = quote_lead * 1.4 if quote_lead else gap_max
        blocks = []
        buf = []
        buf_kind = "p"
        prev_top = None
        prev_line = None

        def flush():
            if buf:
                # A paragraph that runs across a page turn carries the new
                # page's folio inline, so the break stays visible in the text.
                parts = []
                for k, x in enumerate(buf):
                    if k and x.get("page") != buf[k - 1].get("page"):
                        marker = self.page_marker(x.get("page"))
                        if marker:
                            parts.append(marker)
                    text = escape(x["text"])
                    for label in x.get("_footnote_labels") or []:
                        text = text.replace(
                            "\ue000",
                            f"<footnotemark>{escape(label)}</footnotemark>",
                            1,
                        )
                    parts.append(text)
                blocks.append(
                    Block(
                        kind=buf_kind,
                        text=" ".join(parts),
                        page=buf[0].get("page"),
                    )
                )
                buf.clear()

        for i, ln in enumerate(lines):
            t = ln["text"]
            top = ln["top"]
            is_quote = quote_flags[i]
            # gap to the previous line (None across a page break, where top
            # resets to a smaller value)
            gap = top - prev_top if prev_top is not None and top >= prev_top else None
            short = len(t.split()) <= 6
            if not is_quote and short and self._is_heading(t):
                flush()
                blocks.append(
                    Block(kind="heading", text=escape(t), page=ln.get("page"))
                )
                prev_top = top
                prev_line = ln
                continue

            kind = "blockquote" if is_quote else "p"
            page_changed = bool(
                prev_line is not None and ln.get("page") != prev_line.get("page")
            )
            first_indent = left + 20 <= ln["x0"] <= left + 48
            returned_from_margin = bool(
                prev_line is not None and prev_line["x0"] <= left + 12
            )
            structured_start = (
                ln["x0"] >= left + 20
                and (
                    self._is_subdivision_start(t)
                    or self._is_numbered_list_start(t)
                )
            )
            starts_paragraph = (
                (gap is not None and gap > gap_max)
                or structured_start
                or (first_indent and (returned_from_margin or page_changed))
            )
            starts_quote_paragraph = gap is not None and gap > quote_gap_max

            if buf and (
                kind != buf_kind
                or (is_quote and starts_quote_paragraph)
                or (not is_quote and starts_paragraph)
            ):
                flush()
            if not buf:
                buf_kind = kind
            buf.append(ln)
            prev_top = top
            prev_line = ln
        flush()
        return blocks

    @staticmethod
    def _is_numbered_list_start(text: str) -> bool:
        """A leading Arabic outline marker (``1. Text``), not a citation."""
        t = text.lstrip()
        dot = t.find(".")
        return (
            0 < dot <= 3
            and t[:dot].isdigit()
            and dot + 1 < len(t)
            and t[dot + 1].isspace()
        )

    @staticmethod
    def _flagged_lead(lines: list, flags: list) -> float | None:
        """Modal same-page lead inside lines marked as quoted matter."""
        from collections import Counter

        gaps = Counter()
        for i in range(1, len(lines)):
            if not (flags[i - 1] and flags[i]):
                continue
            if lines[i - 1].get("page") != lines[i].get("page"):
                continue
            gap = round(lines[i]["top"] - lines[i - 1]["top"], 1)
            if 5 < gap < 50:
                gaps[round(gap)] += 1
        return float(gaps.most_common(1)[0][0]) if gaps else None

    def _blockquote_flags(self, lines: list, left: float, right: float, lead) -> list:
        """Mark stable indented runs that are displayed quoted matter.

        A normal first-line indent is isolated: its wrapped continuation
        returns to ``left``. A quote holds one inset over at least two tightly
        led lines and also narrows the right measure; a deeply nested inserted
        passage (two indent steps) is sufficient with three lines even when
        the source keeps the ordinary right margin.
        """
        flags = [False] * len(lines)
        max_close_gap = (lead * 1.35) if lead else 32.0
        i = 0
        while i < len(lines):
            anchor = lines[i]["x0"]
            first_text = lines[i]["text"].strip()
            if (
                anchor < left + 30
                or first_text.isdigit()
                or self.is_rule_text(first_text, "_")
                or self._signature(first_text)
            ):
                i += 1
                continue
            j = i + 1
            while (
                j < len(lines)
                and lines[j].get("page") == lines[i].get("page")
                and abs(lines[j]["x0"] - anchor) <= 3
                and not lines[j]["text"].strip().isdigit()
                and not self.is_rule_text(lines[j]["text"].strip(), "_")
                and not self._signature(lines[j]["text"].strip())
            ):
                j += 1
            run = lines[i:j]
            close_pairs = sum(
                1
                for a, b in zip(run, run[1:])
                if 0 < b["top"] - a["top"] <= max_close_gap
            )
            tight_pairs = sum(
                1
                for a, b in zip(run, run[1:])
                if 0
                < b["top"] - a["top"]
                <= ((lead * 0.9) if lead else 20.0)
            )
            right_inset = right - max((ln["x1"] for ln in run), default=right)
            deeply_inset = anchor >= left + 60 and len(run) >= 3
            if len(run) >= 2 and close_pairs and (
                (right_inset >= 24 and tight_pairs) or deeply_inset
            ):
                mark_end = j
                # A new ordinary paragraph can open at the quote indent and
                # then wrap back to the body margin. Its first line is the
                # trailing member of this stable-x run, but the return on the
                # next line proves it is prose, not part of the quote.
                if (
                    j < len(lines)
                    and lines[j].get("page") == lines[j - 1].get("page")
                    and lines[j]["x0"] <= left + 12
                    and j - i >= 3
                    and lines[j - 1]["top"] - lines[j - 2]["top"]
                    > ((lead * 0.9) if lead else 20.0)
                ):
                    mark_end -= 1
                for k in range(i, mark_end):
                    flags[k] = True
            i = max(j, i + 1)

        # A one-line deeply inset insertion immediately after an introductory
        # colon is also displayed quoted matter (modification orders often
        # replace a citation with one short line). Both the transition depth
        # and the colon boundary are required.
        for i in range(1, len(lines)):
            if flags[i] or lines[i]["x0"] < left + 60:
                continue
            if lines[i - 1].get("page") != lines[i].get("page"):
                continue
            if lines[i - 1]["text"].rstrip().endswith(":"):
                flags[i] = True
        return flags

    @staticmethod
    def _body_lead(lines: list) -> float | None:
        """The document's modal line lead, or None.

        Taken from consecutive same-page lines only — a page turn resets ``top``
        and would otherwise contribute a meaningless negative gap."""
        from collections import Counter

        gaps = Counter()
        for a, b in zip(lines, lines[1:]):
            if a.get("page") != b.get("page"):
                continue
            gap = round(b["top"] - a["top"], 1)
            if 5 < gap < 60:
                gaps[round(gap)] += 1
        return float(gaps.most_common(1)[0][0]) if gaps else None

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
