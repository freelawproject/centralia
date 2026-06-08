"""Supreme Court of California.

A page-driven layout, the opposite of the Alabama byline-at-start model:

  - Page 1: banner 'IN THE SUPREME COURT OF CALIFORNIA' -> caption -> docket
    ('S######') -> originating court(s) -> date -> a prose authorship summary
    ('Chief Justice Guerrero authored the opinion of the Court, in which ...
    concurred. Justice Groban filed a concurring opinion ...').
  - Every body page carries a running header whose id line names the opinion:
    'Opinion of the Court by <author>' (majority),
    'Concurring Opinion by Justice <name>', 'Dissenting Opinion by ...',
    'Concurring and Dissenting Opinion by ...'. The opinion a page belongs to
    is read from that id; consecutive same-id pages form one opinion.
  - Each opinion ends with an all-caps signature ('GUERRERO, C. J.') and,
    for the lead opinion, 'We Concur:' + the panel. Page numbers restart per
    opinion.

First pass: split headmatter from the body, section the body by running-header
id, capture each opinion's author/type, paragraphs, and footnotes. Inline
emphasis is not yet preserved (plain, escaped text).
"""

from __future__ import annotations

from xml.sax.saxutils import escape

import pdfplumber

from ..base import BaseExtractor
from ..models import Block, DocType, ExtractedDocument, Footnote, Opinion


_FN_SYMBOLS = "*†‡§¶"

_ID_PREFIXES = (
    ("Opinion of the Court by ", "majority"),
    (
        "Concurring and Dissenting Opinion by ",
        "concurring-in-part-and-dissenting-in-part",
    ),
    ("Concurring Opinion by ", "concurrence"),
    ("Dissenting Opinion by ", "dissent"),
)


class CaliforniaSupreme(BaseExtractor):
    court_id = "cal"
    court_label = "Supreme Court of California."

    # ------------------------------------------------------------------
    def extract(self, pdf_path: str) -> ExtractedDocument:
        with pdfplumber.open(pdf_path) as pdf:
            n_pages = len(pdf.pages)
            pages = [self._page_lines(p) for p in pdf.pages]  # [(body, fns)]

        doc = ExtractedDocument(
            court_id=self.court_id,
            court_label=self.court_label,
            n_pages=n_pages,
            source_path=pdf_path,
            doc_type=DocType.OPINION,
        )
        if not any(b for b, _ in pages):
            doc.doc_type = DocType.UNKNOWN
            return doc

        # Per-page opinion id (None until the first opinion begins).
        page_ids = [self._page_id([ln["text"] for ln in body]) for body, _ in pages]
        first_body = next((i for i, pid in enumerate(page_ids) if pid), None)

        # Headmatter = pages before the first opinion id.
        hm_pages = pages[:first_body] if first_body is not None else pages
        self._headmatter(doc, hm_pages)
        if first_body is None:
            doc.doc_type = DocType.UNKNOWN
            return doc

        # Section consecutive same-id pages into opinions.
        sections = []  # (id_text, [page_index, ...])
        for i in range(first_body, n_pages):
            pid = page_ids[i] or (sections[-1][0] if sections else None)
            if not pid:
                continue
            if sections and sections[-1][0] == pid:
                sections[-1][1].append(i)
            else:
                sections.append((pid, [i]))

        counsel = []  # counsel / address block at the very end
        for id_text, idxs in sections:
            op_type, author = self._parse_id(id_text)
            body_lines, fn_lines = [], []
            for i in idxs:
                b, f = pages[i]
                body_lines.extend(self._strip_header(b, id_text))
                fn_lines.extend(f)
            # Split off ONLY the trailing counsel/address block into the
            # ending-matter box. Everything else — including the signature,
            # 'We Concur:' and the panel of justices — stays in the opinion.
            if not counsel:
                cut = self._trailer_start(body_lines)
                if cut is not None:
                    counsel = [ln["text"] for ln in body_lines[cut:]]
                    body_lines = body_lines[:cut]
            self._capture_panel(body_lines, doc)
            blocks = self._paragraphs(body_lines)
            notes = self._collect_footnotes(fn_lines)
            doc.opinions.append(
                Opinion(
                    type=op_type,
                    author=author,
                    blocks=blocks,
                    footnotes=notes,
                )
            )
        doc.trailer = counsel
        return doc

    _TRAILER_MARKERS = (
        "addresses and telephone numbers for counsel",
        "counsel who argued in supreme court",
    )

    def _trailer_start(self, body_lines: list) -> int | None:
        """Index of the first line that begins the trailing counsel/address
        matter, or None."""
        for i, ln in enumerate(body_lines):
            low = ln["text"].lower()
            if any(m in low for m in self._TRAILER_MARKERS):
                return i
        return None

    # ------------------------------------------------------------------
    def _page_lines(self, page) -> tuple:
        """(body_lines, footnote_lines); footnotes are below the separator
        rule (thin rect at x0~72)."""
        sep_y = self._sep_y(page)
        body, fns = [], []
        for ln in page.extract_text_lines(layout=False):
            text = (ln.get("text") or "").strip()
            if not text:
                continue
            chars = ln.get("chars") or []
            size = round(max((c.get("size", 0) for c in chars), default=0), 1)
            top = round(ln["top"], 1)
            nbold = sum(1 for c in chars if "bold" in c.get("fontname", "").lower())
            nital = sum(1 for c in chars if "italic" in c.get("fontname", "").lower())
            x0, x1 = round(ln["x0"], 1), round(ln["x1"], 1)
            rec = {
                "text": text,
                "top": top,
                "x0": x0,
                "x1": x1,
                "size": size,
                "page": page.page_number,
                "bold": bool(chars) and nbold / len(chars) > 0.6,
                "italic": bool(chars) and nital / len(chars) > 0.6,
                "align": self._align(x0, x1, size, page.width),
            }
            if sep_y is not None and top >= sep_y:
                if text.isdigit():
                    continue
                first = chars[0] if chars else {}
                rec["first"] = first.get("text", "")
                rec["first_size"] = round(first.get("size", size), 1)
                fns.append(rec)
            else:
                body.append(rec)
        return body, fns

    # The footnote divider is a very specific rule: a thin horizontal hairline
    # exactly ~144pt (2") wide, left-aligned to the text block (cal indents it
    # to x0~108; other courts use x0~72). It must NOT be confused with other
    # horizontal graphics on the page (underlines, table rules, full-width
    # rules), so both the width and thinness are matched tightly.
    _SEP_W_MIN, _SEP_W_MAX = 140.0, 150.0

    @staticmethod
    def _align(x0: float, x1: float, size: float, pw: float) -> str:
        """C / L / R for a headmatter line. A narrow line centered on the page
        midpoint is centered (the banner, caption, docket, originating courts);
        the wide authorship-summary paragraph at the left margin stays left
        because it exceeds the centering width cap."""
        width, cx = x1 - x0, (x0 + x1) / 2
        midish = abs(cx - pw / 2) < 25
        if midish and (width < pw * 0.55 or size >= 16):
            return "C"
        if x0 > pw * 0.6:
            return "R"
        return "L"

    @classmethod
    def _sep_y(cls, page):
        """Top of the footnote separator rule, or None."""

        def ok(x0, w, h):
            return 70 <= x0 <= 115 and cls._SEP_W_MIN <= w <= cls._SEP_W_MAX and h < 2

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

    @staticmethod
    def _page_id(texts: list) -> str | None:
        """The running-header opinion id on this page, if any."""
        for t in texts[:4]:
            for prefix, _ in _ID_PREFIXES:
                if t.startswith(prefix):
                    return t
        return None

    @staticmethod
    def _parse_id(id_text: str) -> tuple:
        for prefix, op_type in _ID_PREFIXES:
            if id_text.startswith(prefix):
                return op_type, id_text[len(prefix) :].strip()
        return "majority", ""

    def _strip_header(self, body: list, id_text: str) -> list:
        """Drop the running-header lines (caption / docket / id) from the top
        of a page, plus bare page numbers."""
        out = []
        for k, ln in enumerate(body):
            t = ln["text"]
            if t == id_text:
                continue
            if k < 3 and (self._is_docket(t) or self._looks_like_caption(t)):
                continue
            if t.isdigit():
                continue
            out.append(ln)
        return out

    @staticmethod
    def _looks_like_caption(t: str) -> bool:
        # Running-header caption: short, ALL-CAPS-ish 'PEOPLE v. LOPEZ' or
        # 'In re KOWALCZYK'.
        if len(t.split()) > 8:
            return False
        return " v. " in t or t.startswith("In re ") or t.isupper()

    def _capture_panel(self, body: list, doc: ExtractedDocument) -> None:
        """Record the concurring panel (the justices after 'We Concur:') into
        the structured fields. Does NOT remove anything — the signature, the
        'We Concur:' line and the panel stay in the opinion body."""
        for i, ln in enumerate(body):
            if ln["text"].lower().rstrip(":") == "we concur":
                panel = [
                    b["text"] for b in body[i + 1 :] if self._is_signature(b["text"])
                ]
                if panel and not doc.panel:
                    doc.panel = panel
                    doc.judges = ", ".join(panel)
                return

    @staticmethod
    def _is_signature(t: str) -> bool:
        s = t.strip().rstrip("*∗†‡ ").strip()
        if not s.endswith("."):
            return False
        up = s.upper()
        if not (
            up.endswith(", J.")
            or up.endswith(", C. J.")
            or up.endswith(", J.,")
            or up.endswith("C. J.")
        ):
            return False
        # All-caps name (the signature is set in caps), short.
        name = s.rsplit(",", 1)[0]
        return name.isupper() and len(s.split()) <= 5

    @staticmethod
    def _is_docket(t: str) -> bool:
        return len(t) == 7 and t[0] == "S" and t[1:].isdigit()

    # ------------------------------------------------------------------
    def _headmatter(self, doc: ExtractedDocument, hm_pages: list) -> None:
        """Style-preserving headmatter (the 'Florida' look): each line keeps its
        relative font size and alignment (bold/italic wrapped inline), and a
        larger-than-normal vertical gap becomes a blank spacer so the page-1
        layout — centered banner/caption/docket over the left-aligned authorship
        summary — is preserved."""
        from collections import Counter

        lines, fn_lines = [], []
        for body, fns in hm_pages:
            fn_lines.extend(fns)
            for ln in body:
                if not ln["text"].isdigit():
                    lines.append(ln)
        base = (
            Counter(round(l["size"]) for l in lines).most_common(1)[0][0]
            if lines
            else 13
        )

        summary, parties = [], []
        prev = None  # (page, top)
        for ln in lines:
            t = ln["text"]
            if prev is not None and (
                ln["page"] != prev[0] or ln["top"] - prev[1] > 30
            ):
                summary.append("")  # blank spacer preserves the section gap
            prev = (ln["page"], ln["top"])
            html = escape(t)
            if ln.get("italic"):
                html = f"<em>{html}</em>"
            if ln.get("bold"):
                html = f"<strong>{html}</strong>"
            summary.append(
                {
                    "__hm__": True,
                    "html": html,
                    "rel": round(ln["size"] / base, 3),
                    "align": ln.get("align", "L"),
                }
            )
            if doc.docket_number is None and self._is_docket(t):
                doc.docket_number = t
            if doc.decision_date is None and self._looks_like_date(t):
                doc.decision_date = t
            if (
                2 <= len(t.split()) <= 12
                and (" v. " in t or t.startswith("In re ") or t.endswith("."))
                and not t[0].islower()
            ):
                parties.append(t)
        doc.summary = summary
        doc.parties = parties[:6]
        # Headmatter footnotes (e.g. a note on the caption) are real footnotes.
        doc.headmatter_footnotes = self._collect_footnotes(fn_lines)

    @staticmethod
    def _looks_like_date(t: str) -> bool:
        months = (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )
        return (
            t.split()[0] in months
            and t.rstrip().endswith(tuple(str(d) for d in range(10)))
            and "," in t
        )

    def _collect_footnotes(self, fn_lines: list) -> list:
        """Group footnote-zone lines into Footnote objects. Numbered notes and
        symbol-labeled ones (``*`` assignment notes, which link to a justice in
        the 'We Concur:' panel) are all kept as opinion footnotes."""
        notes = []
        cur_label = None
        cur_text = []

        def flush():
            if cur_label is None:
                return
            text = " ".join(cur_text).strip()
            notes.append(
                Footnote(
                    label=cur_label,
                    paragraphs=[("p", escape(text))],
                )
            )

        for fl in fn_lines:
            first = fl.get("first", "")
            superscript = fl.get("first_size", 99) < fl["size"] - 1.5
            is_label = (
                bool(first)
                and superscript
                and (first.isdigit() or first in _FN_SYMBOLS)
            )
            if is_label:
                flush()
                t = fl["text"]
                if t[:1] in _FN_SYMBOLS:  # symbol label: *, †, ‡, §
                    cur_label = t[0]
                    cur_text = [t[1:].strip()]
                else:  # numeric label
                    k = 0
                    while k < len(t) and t[k].isdigit():
                        k += 1
                    cur_label = t[:k]
                    cur_text = [t[k:].strip()]
            elif cur_label is not None:
                cur_text.append(fl["text"])
        flush()
        return notes

    # Indent (pt past the body left margin) at/above which a *run* of lines is
    # a block quotation; a lone indented line is just a paragraph's first line.
    _QUOTE_INDENT = 24.0
    _PARA_INDENT = 12.0

    def _paragraphs(self, lines: list) -> list:
        if not lines:
            return []
        left = min(ln["x0"] for ln in lines)
        indents = [ln["x0"] - left for ln in lines]

        # Mark block-quote lines: maximal runs (length >= 2) where every line
        # is indented past _QUOTE_INDENT (the whole block is shifted right,
        # unlike a paragraph whose continuation lines return to the margin).
        is_q = [False] * len(lines)
        i = 0
        while i < len(lines):
            if indents[i] >= self._QUOTE_INDENT:
                j = i
                while j < len(lines) and indents[j] >= self._QUOTE_INDENT:
                    j += 1
                if j - i >= 2:
                    for k in range(i, j):
                        is_q[k] = True
                i = j
            else:
                i += 1

        blocks, buf = [], []
        buf_kind = "p"
        prev_page = None

        def flush():
            if buf:
                text = " ".join(
                    (x["text"] if x.get("raw") else escape(x["text"])) for x in buf
                )
                blocks.append(Block(kind=buf_kind, text=text))
                buf.clear()

        for idx, ln in enumerate(lines):
            pg = ln.get("page")
            if prev_page is not None and pg is not None and pg != prev_page:
                # Inline page marker so a paragraph spanning the page boundary
                # is NOT split in two; renders as the [N] page chip.
                buf.append(
                    {"text": f'<pagenumber value="{pg}"/>', "raw": True, "x0": ln["x0"]}
                )
            prev_page = pg

            t = ln["text"]
            # A heading is a bold line, or a roman-numeral / all-caps section
            # line, that is not part of a block quote. Consecutive heading
            # lines merge into one heading (font + spacing keep them together).
            is_head = (not is_q[idx]) and (ln.get("bold") or self._is_heading(t))
            kind = "heading" if is_head else "blockquote" if is_q[idx] else "p"
            if buf and kind != buf_kind:
                flush()
            elif kind == "p" and buf and indents[idx] >= self._PARA_INDENT:
                flush()  # first-line indent starts a new para
            buf_kind = kind
            buf.append(ln)
        flush()
        return blocks

    @staticmethod
    def _is_heading(t: str) -> bool:
        head = t.strip().rstrip(".")
        if not head:
            return False
        first = head.split(".")[0] if "." in head else head.split()[0]
        if first and all(c in set("IVXLC") for c in first) and len(first) <= 5:
            return True
        return (
            len(head) <= 40 and head.upper() == head and any(c.isalpha() for c in head)
        )
