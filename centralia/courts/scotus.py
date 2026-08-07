"""Supreme Court of the United States ('scotus').

Slip-opinion structure, section by section:

* Page 1: the Reporter's small-print NOTE (7pt — a notice, dropped and
  recorded), the 'SUPREME COURT OF THE UNITED STATES' banner with the case
  line, 'CERTIORARI TO ...', and 'No. NN–NNN. Argued ... Decided ...' —
  that cover is the document headmatter.
* The Syllabus: runs as long as the running head at the top of each page
  says 'Syllabus'; extracted into ``doc.syllabus`` (its own section, not
  opinion body), paragraph-grouped by the first-line indent.
* Each writing — opinion of the Court, every concurrence and dissent —
  opens on its own fancy first page: a 7pt revision NOTICE (notice,
  dropped+recorded), the banner / docket / caption / 'ON WRIT OF ...' /
  '[date]' cover, then the byline. The writing starts at the TOP of that
  page (the cover belongs to it; nothing is dropped), and the byline
  supplies the author and opinion type — including wrapped 'JUSTICE ALITO,
  with whom THE CHIEF JUSTICE and JUSTICE KAVANAUGH join, dissenting.'

Furniture and geometry:

* Running heads sit at y≈115/139 ('(Slip Opinion) OCTOBER TERM, 2025 1',
  '2 BERK v. CHOY', 'Cite as: 607 U. S. ___ (2026) 5', and the center
  section label). They are dropped by position and recorded; the label
  drives the Syllabus boundary, and the PRINTED page number (slip numbering
  restarts for each writing) replaces the PDF page index on every block.
* 9pt body, lines lead ~13.2pt, indented quotes ~10.8pt; the footnote rule
  is a row of em-dashes drawn as text, not a graphic.
"""

from __future__ import annotations

import html

from ._reversedjustice import _KIND_ENDINGS, ReversedJusticeSupreme, _allcaps_token

_SECTION_LABELS = ("Syllabus", "Opinion of the Court", "Per Curiam")
_BYLINE_OPENERS = ("JUSTICE", "CHIEF JUSTICE", "THE CHIEF JUSTICE", "PER CURIAM")
# Kind words an 'opinion relating to orders' byline closes on.
_ORDER_KIND_WORDS = ("dissent", "concurr", "respecting")
_ROMAN_OUTLINE = frozenset(
    ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII")
)


class SupremeCourtUS(ReversedJusticeSupreme):
    court_id = "scotus"
    court_label = "Supreme Court of the United States."
    _ROMAN_OUTLINE = _ROMAN_OUTLINE

    _HEAD_BAND = 150.0  # running heads at y≈115/139; content starts y≈158
    # 9pt body: lines lead ~13.2pt, block quotes ~10.8pt.
    gap_tight_max = 9.5
    gap_single_max = 12.4
    gap_double_max = 28
    # Body baseline x≈156.2 with an ~11pt paragraph indent.
    body_baseline_x0 = 156.0
    para_indent_min = 8

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path):
        self._head_dropped = []
        self._notice_dropped = []
        self._page_label = {}
        self._page_printed = {}
        self._authors = {}
        self._covers = {}  # op_start (top) → byline segment index for i>0 writings
        self._syllabus_rows = []
        self._sections_applied = False
        doc = super().extract(pdf_path)
        self._apply_sections(doc)
        self._remap_printed_pages(doc)
        self._read_criteria(doc)
        return doc

    # ------------------------------------------------------------- criteria
    # The bench opinion's headmatter is SHORT and in fixed order, ruled into its
    # parts by the Court itself, so it is read positionally rather than by
    # recognising each row's shape:
    #
    #     SUPREME COURT OF THE UNITED STATES        the court (bold banner)
    #     __DIVIDER__
    #     No. 25–5146                               the docket
    #     __DIVIDER__
    #     AHMAD ABOUAMMO, PETITIONER v.             the case name, over two rows
    #     UNITED STATES
    #     ON WRIT OF CERTIORARI TO THE UNITED STATES COURT OF   the origin, ditto
    #     APPEALS FOR THE NINTH CIRCUIT
    #     [June 11, 2026]                           the decision date, bracketed
    #
    # The SYLLABUS carries the sitting dates on one line that the headmatter
    # never states ('No. 25–5146.  Argued March 30, 2026—Decided June 11,
    # 2026'), so it is read for those.
    _ORIGIN_OPENERS = (
        "on writ of certiorari",
        "on certiorari",
        "on appeal from",
        "on appeals from",
        "on petition for",
        "on petitions for",
        "on writs of certiorari",
        "on application for",
        "on motion for",
        "on bill of complaint",
        "on remand from",
        "on writ of habeas corpus",
    )

    @staticmethod
    def _row_text(row) -> str:
        """A headmatter row's plain text, whatever form the row takes.

        Entities are resolved: '&amp;' otherwise carries lower-case letters into
        a row that is set entirely in caps ('AT&amp;T, INC.')."""
        if isinstance(row, dict):
            row = row.get("html", "")
        text = str(row or "")
        out, depth = [], 0
        for char in text:
            if char == "<":
                depth += 1
            elif char == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(char)
        return " ".join(html.unescape("".join(out)).split()).strip()

    def _read_criteria(self, doc) -> None:
        """Dissect the bench-opinion headmatter into ``doc.criteria``.

        A CONSOLIDATED record states each case in full — its docket, its name,
        and the application or writ it comes on — and then one bracketed date
        governing all of them:

            No. 25A1314
            WES ALLEN, ALABAMA SECRETARY OF STATE, ET AL. v. EVAN MILLIGAN, ET AL.
            ON APPLICATION FOR STAY
            No. 25A1315
            … v. BOBBY SINGLETON, ET AL.
            ON APPLICATION FOR STAY
            [June 2, 2026]

        So a docket row OPENS a case rather than filling a single one, and the
        rows after it belong to that case until the next docket row."""
        rows = [self._row_text(r) for r in (doc.summary or [])]
        crit: dict = {}
        cases: list = []
        # Rows that arrive before any docket. An ORDER states the case name and
        # the writ FIRST and puts the docket last, carrying the date with it
        # ('DISTRICT OF COLUMBIA v. R.W.' / 'ON PETITION FOR WRIT OF CERTIORARI
        # TO THE DISTRICT OF' / 'COLUMBIA COURT OF APPEALS' / 'No. 25–248.
        # Decided April 20, 2026'), so what precedes the docket is held and
        # attached to the case the docket opens.
        pending: dict = {"_name": [], "_origin": []}

        def open_case(docket):
            cases.append({
                "docket": docket,
                "_name": pending["_name"],
                "_origin": pending["_origin"],
            })
            pending["_name"], pending["_origin"] = [], []

        for text in rows:
            if not text or text == self.HEADMATTER_DIVIDER:
                continue
            low = text.lower()
            if "supreme court of the united states" in low:
                crit.setdefault("court", text)
                continue
            if low.startswith(("no. ", "nos. ")):
                docket, dates = self._split_docket_dates(text)
                crit.update(dates)
                open_case(docket)
                continue
            if text.startswith("[") and text.endswith("]"):
                crit["date_filed"] = text.strip("[]").strip()
                continue
            # A CONSOLIDATED record headed by both dockets ('Nos. 25–406 and
            # 25–567') then tags each case's own versus row with the docket it
            # belongs to ('25–406 v.'). That tag is what separates one case from
            # the next; the shared header alone cannot.
            inline = self._inline_docket(text)
            if inline:
                # The tag marks this case's hinge. Everything buffered above it
                # is its appellant side; the rows below it, up to the next
                # appellant, are its appellee side. The tag itself is dropped
                # from the NAME (the docket already records it) and the bare
                # hinge kept in its place.
                pending["_name"].append("v.")
                open_case(f"No. {inline}")
                continue
            # A row closing with a party STATUS opens the next case's appellant
            # side. Consolidated appeals share one trailing origin ('LOUISIANA,
            # APPELLANT' / '24–109 v.' / 'PHILLIP CALLAIS, ET AL.' / 'PRESS
            # ROBINSON, ET AL., APPELLANTS' / '24–110 v.' / … / 'ON APPEALS
            # FROM …'), so waiting for an origin to close a case merged the two
            # and overwrote the first one's docket.
            if cases and not cases[-1]["_origin"] and self._opens_next_party(text):
                pending["_name"].append(text)
                continue
            # THE CAPTION IS SET IN CAPS; the order's own text is not. Without
            # that bound the reader kept appending, and florida_v._california's
            # disposition ('The motion for leave to file a bill of complaint is
            # denied.') landed on the end of the case name.
            if not self._is_caption_row(text):
                continue
            target = cases[-1] if cases else pending
            # The writ wraps once or twice and no further; past that, caps rows
            # are the next case's parties, not more of this one's origin.
            if low.startswith(self._ORIGIN_OPENERS) or (
                target["_origin"] and len(target["_origin"]) < 3
            ):
                target["_origin"].append(text)
            else:
                target["_name"].append(text)

        if pending["_name"] or pending["_origin"]:
            open_case(None)

        for case in cases:
            if case["_name"]:
                case["case_name"] = " ".join(case["_name"])
            if case["_origin"]:
                joined = " ".join(case["_origin"])
                case["prior_history"] = joined
                low = joined.lower()
                for lead in (" to the ", " from the "):
                    if lead in low:
                        case["lower_court"] = joined[
                            low.index(lead) + len(lead):
                        ].strip()
                        break
            del case["_name"], case["_origin"]

        # A consolidated record headed by all its dockets ('Nos. 24–109 and
        # 24–110') states each case again below, tagged; the header itself is
        # then not a case and comes back empty.
        cases = [c for c in cases if c.get("case_name") or c.get("prior_history")]
        if cases:
            crit["cases"] = cases
        crit.update(self._syllabus_dates(doc))
        if not crit:
            return
        doc.criteria = crit
        dockets = [c["docket"] for c in cases if c.get("docket")]
        if dockets:
            doc.docket_number = dockets[0]
            if len(dockets) > 1:
                doc.other_docket = "; ".join(dockets[1:])
        lower = next((c["lower_court"] for c in cases if c.get("lower_court")), None)
        if lower:
            doc.lower_court = lower
        history = [c["prior_history"] for c in cases if c.get("prior_history")]
        if history:
            doc.history = "; ".join(dict.fromkeys(history))
        decided = crit.get("date_decided") or crit.get("date_filed")
        if decided and not doc.decision_date:
            doc.decision_date = decided
        if crit.get("date_argued") and not doc.submitted:
            doc.submitted = crit["date_argued"]

    @staticmethod
    def _is_caption_row(text) -> bool:
        """True when a row can be part of the CAPTION — i.e. it is set in caps.

        The hinge is the one lower-case thing a caption contains, so it comes out
        before the test."""
        kept = [
            token
            for token in text.split()
            if token.strip(".,").lower() not in ("v", "vs")
        ]
        return not any(ch.islower() for ch in " ".join(kept))

    _PARTY_STATUS_END = (
        "appellant", "appellants", "petitioner", "petitioners",
    )

    @classmethod
    def _opens_next_party(cls, text) -> bool:
        """True when a caps row closes with a party status, i.e. names a side."""
        words = text.rstrip(".,").split()
        # A BARE status word is the continuation of the party named on the row
        # above it ('FEDERAL COMMUNICATIONS COMMISSION, ET AL.,' / 'PETITIONERS'),
        # not a new party — a new one names itself before its status.
        if len(words) < 2:
            return False
        return words[-1].strip(".,").lower() in cls._PARTY_STATUS_END

    @staticmethod
    def _inline_docket(text) -> str:
        """'25–406' from a versus row tagged with its own docket, else ''."""
        parts = text.split()
        if len(parts) < 2 or parts[1].rstrip(".").lower() not in ("v", "vs"):
            return ""
        head = parts[0]
        return head if any(c.isdigit() for c in head) else ""

    @staticmethod
    def _split_docket_dates(text):
        """('No. 25–248', {'date_decided': 'April 20, 2026'}).

        An order runs the docket and the disposition date together on one row."""
        dates = {}
        body = text.rstrip(".")
        for label, key in (("Decided", "date_decided"), ("Argued", "date_argued")):
            if label in body:
                head, _, tail = body.partition(label)
                for stop in ("\u2014", "\u2013", "-"):
                    if stop in tail:
                        tail = tail.split(stop, 1)[0]
                dates[key] = tail.strip(" .,")
                body = head.strip(" .,")
        return body.strip(" .,"), dates

    def _syllabus_dates(self, doc) -> dict:
        """{'date_argued': …, 'date_decided': …} off the syllabus's docket line.

        'No. 25–5146.  Argued March 30, 2026—Decided June 11, 2026' — the only
        statement of when the case was argued; the headmatter gives the decision
        day alone, in brackets."""
        for row in (doc.syllabus or [])[:12]:
            text = self._row_text(row)
            low = text.lower()
            if "argued" not in low or "decided" not in low:
                continue
            out = {}
            # Split on the en dash / em dash / hyphen the Court sets between them.
            body = text
            for label, key in (("Argued", "date_argued"), ("Decided", "date_decided")):
                if label not in body:
                    continue
                tail = body.split(label, 1)[1]
                for stop in ("—", "–", "—", "–"):
                    if stop in tail:
                        tail = tail.split(stop, 1)[0]
                out[key] = tail.strip(" .,")
            return out
        return {}

    def _apply_sections(self, doc) -> None:
        """Move the collected syllabus rows and the recorded furniture onto the
        document. Idempotent: it runs from ``_sweep_residual`` (so the
        completeness sweep can see both) and again after ``super().extract``."""
        if getattr(self, "_sections_applied", False):
            return
        self._sections_applied = True
        if self._syllabus_rows:
            doc.syllabus = self._syllabus_rows
        extra = list(dict.fromkeys(self._notice_dropped + self._head_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra

    def _sweep_residual(self, doc, source_pages) -> None:
        # The syllabus section and the recorded running heads / notices are
        # attached by this court AFTER the base pipeline finishes — flush them
        # first or the sweep reads every one of those lines as unplaced.
        self._apply_sections(doc)
        super()._sweep_residual(doc, source_pages)

    def _remap_printed_pages(self, doc):
        """Blocks carry the slip's PRINTED page number (which restarts for
        each writing), not the PDF page index."""
        mapping = self._page_printed
        if not mapping:
            return
        marker = '<pagenumber value="'
        for op in doc.opinions:
            for b in op.blocks:
                if b.page in mapping:
                    b.page = mapping[b.page]
                if marker in (b.text or ""):
                    parts = b.text.split(marker)
                    out = [parts[0]]
                    for rest in parts[1:]:
                        i = rest.find('"')
                        if i > 0 and rest[:i].isdigit():
                            n = int(rest[:i])
                            out.append(marker + str(mapping.get(n, n)) + rest[i:])
                        else:
                            out.append(marker + rest)
                    b.text = "".join(out)

    # ---------------------------------------------------- page furniture
    def prepare_document(self, pdf) -> None:
        """Measure each page's running-head cut.

        Every slip page opens with two head lines — the folio line and the
        centered section label — and the label is the SAME text on every page
        of a writing. Most pages sit them at y≈115/139, but a page can be
        nudged down a line (chiles p3 puts 'Syllabus' at y=152). A fixed band
        then reads the label as body text and the page loses its section, so
        the cut is measured per page: the nominal band, extended past a second
        line that is a short centered label recurring elsewhere in this same
        document's head band."""
        super().prepare_document(pdf)
        from collections import Counter

        self._head_cut = {}
        per_page = []
        for page in pdf.pages:
            lines = [
                l
                for l in sorted(page.extract_text_lines(), key=lambda x: x["top"])
                if (l.get("text") or "").strip()
            ]
            per_page.append((page.page_number, page.width, lines))
        vocab = Counter(
            lines[1]["text"].strip()
            for _pno, _w, lines in per_page
            if len(lines) >= 2 and lines[1]["top"] < self._HEAD_BAND
        )
        labels = {t for t, n in vocab.items() if n >= 2 and t}
        for pno, width, lines in per_page:
            cut = self._HEAD_BAND
            if (
                len(lines) >= 3
                and lines[0]["top"] < cut <= lines[1]["top"]
                and lines[1]["text"].strip() in labels
                and (lines[1]["x1"] - lines[1]["x0"]) < 0.35 * width
                and abs((lines[1]["x0"] + lines[1]["x1"]) / 2 - width / 2) < 20
                and lines[2]["top"] > lines[1]["bottom"]
            ):
                cut = lines[1]["bottom"] + 1
            self._head_cut[pno] = cut

    def page_lines(self, page):
        lines = super().page_lines(page)
        for attr in ("_head_dropped", "_notice_dropped"):
            if getattr(self, attr, None) is None:
                setattr(self, attr, [])
        head_band = getattr(self, "_head_cut", {}).get(
            page.page_number, self._HEAD_BAND
        )
        kept, head_texts = [], []
        for ln in lines:
            if ln["top"] < head_band:
                txt = self.line_plain_text(ln).strip()
                if txt:
                    head_texts.append(txt)
                    self._head_dropped.append(txt)
                continue
            txt0 = self.line_plain_text(ln).strip()
            if len(txt0) >= 4 and all(c in "—–-" for c in txt0):
                continue  # the footnote rule, drawn as text
            size, _f, _b = self.line_meta(ln)
            if size <= 7.5 and ln["top"] < 230 and any(c.isalpha() for c in txt0):
                # The Reporter's NOTE / the revision NOTICE — small-print
                # notices, always in the cover region. (Small-caps body text
                # can read as 7pt-dominant — 'JUSTICE SOTOMAYOR' — so the
                # drop is position-bound; underscore rules stay separators.)
                if txt0:
                    self._notice_dropped.append(txt0)
                continue
            kept.append(ln)
        self._record_head(page.page_number, head_texts)
        return kept

    def _record_head(self, pno: int, head_texts: list) -> None:
        """The running head carries the section label (center line) and the
        printed page number (edge of the first line)."""
        label = None
        for t in head_texts:
            if t in _SECTION_LABELS or "dissent" in t.lower() or "concurr" in t.lower():
                label = t
                break
        if label is not None:
            self._page_label[pno] = label
        for t in head_texts:
            toks = t.split()
            digits = [w for w in toks if w.isdigit() and len(w) <= 3]
            if digits:
                self._page_printed[pno] = int(digits[-1])
                break

    def detect_footnote_label(self, line):
        label = super().detect_footnote_label(line)
        if label is not None:
            return label
        # An unnumbered asterisk footnote ('*JUSTICE JACKSON says ...').
        chars = line.get("chars") or []
        if chars and (chars[0].get("text") or "") == "*":
            return "*"
        return None

    def find_footnote_separator(self, page):
        """The slip footnote rule is a short em-dash run drawn as TEXT."""
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        best = None
        for line in page.extract_text_lines():
            t = (line.get("text") or "").strip()
            if (
                len(t) >= 4
                and all(c in "—–-" for c in t)
                and line["top"] > page.height * 0.4
                and line["x0"] < page.width * 0.4
            ):
                if best is None or line["top"] < best:
                    best = line["top"]
        return best

    # ------------------------------------------------------------ writings
    def _wrapped_byline_at(self, seg, j) -> bool:
        """True when the byline clause STARTS at ``seg[j]`` but only closes on a
        later line — the single-line byline test cannot see it."""
        texts = [self.line_plain_text(l).strip() for l in seg[j:]]
        if not texts or not self._opens_byline(texts[0]):
            return False
        if self.parse_author_line(texts[0]) is not None:
            return False  # the single-line test already cuts here
        clause, _used = self._assemble_byline(texts + [""])
        return bool(clause) and self.parse_author_line(clause) is not None

    def _split_segments_at_bylines(self, all_segments) -> list:
        """Cut at WRAPPED bylines too, then let the base cut at single-line
        ones. A writing that hangs off an order shares its segment with the
        disposition above it ('The petition for a writ of certiorari is
        denied.' / 'Statement of JUSTICE SOTOMAYOR respecting the denial' / 'of
        certiorari.'), so without this the disposition opens the writing's body
        instead of closing the cover."""
        pre = []
        for page_no, seg, kind in all_segments:
            cuts = [j for j in range(1, len(seg)) if self._wrapped_byline_at(seg, j)]
            if not cuts:
                pre.append((page_no, seg, kind))
                continue
            bounds = [0] + cuts + [len(seg)]
            for a, b in zip(bounds, bounds[1:]):
                sub = seg[a:b]
                if sub:
                    pre.append((page_no, sub, self.classify_segment(sub)))
        return super()._split_segments_at_bylines(pre)

    def find_authors(self, all_segments) -> list:
        byline_idx = super().find_authors(all_segments)
        self._authors = {}
        claimed = {all_segments[b][0]: b for b in byline_idx}
        # Supplement: a wrapped byline whose continuation line carries no
        # JUSTICE prefix — 'JUSTICE JACKSON, with whom JUSTICE SOTOMAYOR
        # joins,' / 'dissenting.', hyphenated 'con-' / 'curring in the
        # judgment.' — is invisible to the line parser. Detect it from the
        # page's opening lines (a consolidated-case cover stacks two
        # captions, so the byline can sit ~21 lines down) and accept only if
        # the assembled clause actually parses as a byline.
        pages: dict = {}
        for j, (pno, seg, _k) in enumerate(all_segments):
            pages.setdefault(pno, []).append(j)
        for pno, idxs in pages.items():
            if pno in claimed:
                continue
            lines = [
                (j, self.line_plain_text(l).strip())
                for j in idxs
                for l in all_segments[j][1]
            ][:24]
            for k, (j, t) in enumerate(lines):
                if not self._opens_byline(t):
                    continue
                texts = [x for _j, x in lines[k:]]
                clause, used = self._assemble_byline(texts)
                if clause and self.parse_author_line(clause) is not None:
                    claimed[pno] = lines[k + used][0]
                break
        starts = []
        for i, pno in enumerate(sorted(claimed)):
            b = claimed[pno]
            top = b
            while top > 0 and all_segments[top - 1][0] == pno:
                top -= 1
            if i == 0:
                # The FIRST writing starts at its byline — its cover page
                # (banner / docket / caption / [date]) is the document
                # headmatter. Later writings start at the top of their own
                # fancy first page so those segments are claimed; the cover
                # content is dropped in build_opinion.
                starts.append(b)
                self._authors[b] = self._page_byline(all_segments, top, b)
            else:
                starts.append(top)
                self._authors[top] = self._page_byline(all_segments, top, b)
                self._covers[top] = b  # cover runs from top to b-1; body starts at b
        return starts

    def _title_at(self, toks) -> str | None:
        """The reversed-justice title this token run leads with, or None."""
        up = " ".join(toks).upper()
        return next((t for t in self.rev_titles if up.startswith(t + " ")), None)

    def _opens_byline(self, text: str) -> bool:
        """A line that can start a byline clause: the title itself, PER CURIAM,
        or a short prose lead-in ahead of the title — 'Statement of JUSTICE
        SOTOMAYOR respecting the denial of certiorari.' The clause still has to
        parse before it is accepted as an author."""
        if text.upper().startswith(_BYLINE_OPENERS):
            return True
        toks = text.split()
        return any(
            self._title_at(toks[i:]) is not None
            and all(w.isalpha() for w in toks[:i])
            for i in range(1, min(len(toks), 4))
        )

    def _assemble_byline(self, texts) -> tuple:
        """Join up to 5 lines starting at the byline opener into one clause:
        hyphenated wraps rejoin ('con-' + 'curring'), and a kind-ending only
        closes the clause when the NEXT line doesn't continue it lowercase
        ('... concurring in part and' / 'dissenting in part.'). An
        orders-byline clause names the disposition it attaches to and so ends
        on a word no fixed list can hold ('... dissenting from the denial of
        motion for leave to file complaint.') — it closes on the sentence stop
        once the clause parses. Returns (clause, lines_used) or (None, 0) if
        the clause never closes."""
        out = ""
        for i, t in enumerate(texts[:5]):
            if out.endswith("-"):
                out = out[:-1] + t
            else:
                out = f"{out} {t}".strip()
            if t.rstrip().lower().endswith(_KIND_ENDINGS):
                nxt = texts[i + 1].lstrip() if i + 1 < len(texts) else ""
                if nxt[:1].islower():
                    continue
                return out, i
            if out.rstrip().endswith(".") and self._orders_byline(out) is not None:
                return out, i
        return None, 0

    # ------------------------------------------- opinions relating to orders
    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        return self._orders_byline(text)

    def _orders_byline(self, text: str):
        """Parse an 'opinion relating to orders' byline -> (name, title, kind).

        These writings hang off a disposition rather than a merits judgment, so
        the kind clause names that disposition and cannot be closed by a fixed
        ending word:

            'JUSTICE THOMAS, with whom JUSTICE ALITO joins, dissenting from
             the denial of motion for leave to file complaint.'
            'Statement of JUSTICE SOTOMAYOR respecting the denial of
             certiorari.'

        Accepted only when the clause is a complete sentence whose CLOSING
        clause is the kind clause. A syllabus sentence ('JUSTICE THOMAS,
        dissenting, argues that ...') keeps going past the kind and is
        rejected, which is what keeps this from claiming prose."""
        t = " ".join(text.split())
        if not t.endswith("."):
            return None
        toks = t.split()
        start = next(
            (
                i
                for i in range(min(len(toks), 4))
                if self._title_at(toks[i:]) is not None
                and all(w.isalpha() for w in toks[:i])
            ),
            None,
        )
        if start is None:
            return None
        rest = toks[start:]
        title = self._title_at(rest)
        rest = rest[len(title.split()) :]
        name_toks = []
        for tok in rest:
            if not _allcaps_token(tok):
                break
            name_toks.append(tok.rstrip(",:"))
            if tok.endswith(","):
                break
        if not name_toks:
            return None
        after = " ".join(rest[len(name_toks) :]).lower()
        words = after.split()
        last = None
        for i, w in enumerate(words):
            if w.strip(",.;").startswith(_ORDER_KIND_WORDS):
                last = i
        if last is None:
            return None
        # The kind clause must CLOSE the sentence — no further clause after it.
        if "," in " ".join(words[last:]):
            return None
        clause = " ".join(words[last:])
        if "concurr" in after and "dissent" in after:
            kind = "concurring in part and dissenting in part"
        elif "concurr" in after:
            kind = "concurring"
        elif "dissent" in after:
            kind = "dissenting"
        elif clause.startswith("respecting"):
            kind = "statement"
        else:
            return None
        return " ".join(name_toks), title.title(), kind

    def _page_byline(self, all_segments, top, b) -> str:
        """The full byline text: from the first JUSTICE/PER CURIAM line on
        the page through the line that closes the byline clause."""
        texts = []
        for j in range(top, b + 1):
            for l in all_segments[j][1]:
                texts.append(self.line_plain_text(l).strip())
        start = next(
            (k for k, t in enumerate(texts) if self._opens_byline(t)),
            None,
        )
        if start is None:
            return texts[-1] if texts else ""
        clause, _used = self._assemble_byline(texts[start:] + [""])
        return clause or " ".join(texts[start:]).strip()

    def split_author_line(self, line):
        # The start line is the cover banner; it stays in the body, the
        # author comes from the page's byline.
        return "", [line]

    def build_opinion(self, op_start, op_end, **kw):
        # For i>0 writings the opinion is claimed from the top of its cover
        # page, but the cover content (banner/docket/caption/date) is the
        # same boilerplate as the first-opinion headmatter — drop it and
        # start the body at the byline segment.
        byline_seg = getattr(self, "_covers", {}).get(op_start)
        if byline_seg is not None:
            all_segs = kw.get("all_segments", [])
            for j in range(op_start, byline_seg):
                for ln in all_segs[j][1]:
                    txt = self.line_plain_text(ln).strip()
                    if txt:
                        self._notice_dropped.append(txt)
            body_start = byline_seg
        else:
            body_start = op_start
        op = super().build_opinion(body_start, op_end, **kw)
        author = getattr(self, "_authors", {}).get(op_start)
        if author:
            op.author = author
            r = self.parse_author_line(author)
            op.type = self.normalize_opinion_type(r[2] if r else None)
        return op

    # ------------------------------------------------------ paragraph types
    def _is_outline_label(self, line) -> bool:
        """A standalone centered hierarchy label — ``I`` / ``II`` / ``A`` /
        ``1`` — set on its own short centered row between body paragraphs. The
        slip style prints them without a trailing period, and it stacks two
        levels on consecutive rows ('I' then 'A'), so each row has to be cut
        out before paragraph grouping or the pair joins into 'I A'."""
        text = self.line_plain_text(line).strip()
        core = text[:-1] if text.endswith(".") else text
        if not core or " " in core:
            return False
        if not (
            core in self._ROMAN_OUTLINE
            or (len(core) == 1 and core.isalpha() and core.isupper())
            or (core.isdigit() and len(core) <= 2)
        ):
            return False
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        center = (line["x0"] + line["x1"]) / 2
        return abs(center - pw / 2) <= 20 and (line["x1"] - line["x0"]) <= 40

    @property
    def _block_indent_min(self) -> float:
        """Left edge a run must clear to be a block quotation rather than a
        paragraph first-line indent: the body baseline plus TWO indent steps
        (body 156.2, paragraph indent 167.2, block quotation 178.3)."""
        return self.body_baseline_x0 + 2 * self.para_indent_min

    def split_body_paragraphs(self, seg) -> list:
        """Cut outline-label rows and indent-LEVEL changes before the generic
        first-line-indent splitter runs.

        The generic splitter opens a paragraph on an indent but not on the
        outdent back to the body margin, so the prose paragraph that follows a
        block quotation is swallowed into the quotation and the whole run then
        reads as plain body text. Splitting on the level change in both
        directions keeps the quotation one unit and the prose after it its
        own."""
        if not seg:
            return []
        out, run = [], []
        for line in seg:
            if self._is_outline_label(line):
                if run:
                    out.extend(self._split_indent_levels(run))
                    run = []
                out.append([line])
            else:
                run.append(line)
        if run:
            out.extend(self._split_indent_levels(run))
        return out

    def _split_indent_levels(self, seg) -> list:
        out, run, run_deep = [], [], None
        block_min = max(self.body_baseline_x0, min(l["x0"] for l in seg)) + (
            2 * self.para_indent_min
        )
        for line in seg:
            deep = line["x0"] > block_min
            if run and deep is not run_deep:
                out.extend(super().split_body_paragraphs(run))
                run = []
            run_deep = deep
            run.append(line)
        if run:
            out.extend(super().split_body_paragraphs(run))
        return out

    def classify_paragraph(self, lines) -> str:
        """Outline label → heading; a run set wholly inside the block-quotation
        indent → blockquote; otherwise the shared centered/caps heading grammar
        decides, falling back to a paragraph."""
        if not lines:
            return "p"
        if len(lines) == 1 and self._is_outline_label(lines[0]):
            return "heading"
        tag = super().classify_paragraph(lines)
        if tag != "p":
            return tag
        if min(l["x0"] for l in lines) <= self._block_indent_min:
            return "p"
        # A lone deep line that is set flush RIGHT is the closing line of the
        # writing ('It is so ordered.'), not a quotation.
        if len(lines) == 1:
            pw = getattr(self, "_page1_width", 612.0) or 612.0
            if self.line_alignment(lines[0], pw) in ("C", "R"):
                return "p"
        return "blockquote"

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """The headmatter is the FIRST OPINION PAGE's cover (banner / docket
        / caption / 'ON WRIT OF ...' / '[date]'). Everything on the
        Syllabus-labeled pages — the slip cover and the syllabus itself —
        is the syllabus section."""
        hm_segs, syl_lines = [], []
        for seg in headmatter_segs:
            if not seg:
                continue
            chars = seg[0].get("chars") or []
            pno = (chars[0].get("page_number") if chars else None) or 1
            if self._page_label.get(pno) == "Syllabus":
                syl_lines.extend(seg)
            else:
                hm_segs.append(seg)
        self._syllabus_rows = self._syllabus_paragraphs(syl_lines)
        return self._styled_headmatter(hm_segs, page1_rules)

    def _syllabus_paragraphs(self, lines) -> list:
        """Styled syllabus rows.

        The cover section (SUPREME COURT banner through the docket/date line
        "No. NNN–NNN. Argued … Decided …") renders each line as its own
        centered row.  Everything after groups into paragraphs: a line whose
        x0 is off the continuation margin (> 4pt) starts a new paragraph,
        matching the same logic used for the opinion body."""
        from collections import Counter

        body = [l for l in lines if self.line_plain_text(l).strip()]
        if not body:
            return []

        # Continuation margin = most common x0 across all lines; body lines
        # dominate because there are far more of them than cover headings.
        margin = Counter(round(l["x0"], 1) for l in body).most_common(1)[0][0]

        rows, para = [], []
        cover_done = False  # True once we have passed the docket/date line

        def gap():
            if rows and rows[-1] != "":
                rows.append("")

        def flush():
            if para:
                text = " ".join(
                    self.line_inline_text(l).strip() for l in para
                ).strip()
                if text:
                    gap()
                    rows.append(
                        {"__hm__": True, "html": text, "rel": 1.0, "align": "L"}
                    )
                del para[:]

        for l in body:
            txt = self.line_plain_text(l).strip()

            if not cover_done:
                # Render each cover line as its own centered heading row.
                gap()
                rows.append(
                    {
                        "__hm__": True,
                        "html": self.line_inline_text(l),
                        "rel": 1.0,
                        "align": "C",
                    }
                )
                # Docket/date line closes the cover: "No. 17–646. Argued …"
                if txt.startswith("No.") and any(c.isdigit() for c in txt[:20]):
                    cover_done = True
                continue

            # Body text: off-margin x0 opens a new paragraph.
            if para and abs(l["x0"] - margin) > 4:
                flush()
            para.append(l)

        flush()
        return rows
