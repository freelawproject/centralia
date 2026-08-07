"""United States Court of Appeals for the Ninth Circuit."""

from __future__ import annotations

from ._circuit import (
    FederalCircuitBase,
    _LOWER_DOCKET_MARKERS,
    _plain,
)
from .generic import _is_name


class NinthCircuit(FederalCircuitBase):
    court_id = "ca9"
    court_label = "United States Court of Appeals for the Ninth Circuit."
    circuit_phrase = "ninth circuit"

    # CA9 draws NO rules or dividers in its headmatter — the sections are held
    # apart by spacing alone. The row-by-row criteria walk needs no walls, so
    # the court parses on the same footing as the rest of the family.
    parse_criteria_enabled = True
    # CA9's memorandum dispositions do not fence their bands. The court
    # appealed from, the date and place of submission and the panel roster all
    # arrive on ONE row ('On Petition for Review of an Order of the Board of
    # Immigration Appeals Argued and Submitted May 19, 2026 Pasadena,
    # California Before: ..., Circuit Judges.'), so the roster has to be split
    # off the end of it or the panel goes unread.
    roster_can_share_row = True
    history_can_share_row = True

    def parse_criteria(self, doc):
        """The shared walk, then CA9's two-column caption read as two things.

        CA9 holds the caption in columns: the parties on the left, and on the
        right the docket, the agency numbers the petition is from, and the
        document's own label —

            ALFREDO SILVA-PALOMARES;            No. 16-72588
            ...                                 Agency Nos. A206-373-927
            Petitioners,                        A206-373-929
            v.                                  ...
            TODD BLANCHE, Acting Attorney       MEMORANDUM*
            General,
            Respondent.

        Flattened into one roll the right column ran onto the end of the case
        name, so the parties came out followed by five agency numbers and the
        word MEMORANDUM."""
        super().parse_criteria(doc)
        crit = doc.criteria or {}
        cases = crit.get("cases") or []
        # A CAPTION CAN RUN OVER THE PAGE. CA9 sets a long roll of real
        # parties in interest across page 1 and page 2, which arrives as TWO
        # caption blocks — the second with no right column at all. Reading
        # only the first stopped the case name half way through its parties.
        blocks = [
            r
            for r in doc.summary
            if isinstance(r, dict) and r.get("__caption__")
        ]
        if not blocks or not cases:
            return

        def cells(rows):
            out = []
            for cell in rows or []:
                text = _plain(cell).strip()
                # The court rules OFF the 'In re' half of a mandamus caption
                # inside the column; the rule is a wall, not a party.
                if not text or not text.strip("_- "):
                    continue
                out.append(text)
            return out

        left = [t for b in blocks for t in cells(b.get("left"))]
        right = next(
            (cells(b.get("right")) for b in blocks if cells(b.get("right"))), []
        )
        if not left or not right:
            return
        case = cases[0]
        case["caption"] = left
        case["case_name"] = " ".join(left)
        # The right column, in the order CA9 sets it: the docket, then the
        # numbers the case carries below, then the document's label.
        agency, title = [], None
        for text in right:
            if self._is_docket_text(text) and not case.get("docket"):
                case["docket"] = self._split_docket(text)[0]
            elif any(m.lower() in text.lower() for m in _LOWER_DOCKET_MARKERS) \
                    or text.lower().startswith(("agency no", "bia no", "tax ct")):
                # THE LABEL OPENS THE GROUP; ITS NUMBERS MAY BE BELOW IT. CA9
                # sets the district court's docket over two rows ('D.C. No.' /
                # '5:21-cv-01978'), so a label read on its own published a
                # lower docket with no number in it at all.
                agency.append(text)
            elif agency and not self._is_party_text(text) and (
                any(ch.isdigit() for ch in text) or agency[-1].endswith("-")
            ):
                # A DOCKET BROKEN OVER TWO ROWS KEEPS ITS HYPHEN. CA9's column
                # is narrow enough to split one ('5:24-cv-06147-' / 'EJD'), and
                # the tail carries no digits of its own.
                if agency[-1].endswith("-"):
                    agency[-1] += text
                else:
                    agency.append(text)
            elif self._is_party_text(text):
                title = title or text
        if agency:
            # THE AGENCY NUMBERS ARE THE DOCKET BELOW. A petition for review
            # comes from a tribunal, not a district court, and these are that
            # tribunal's own numbers — one per petitioner on a family's case.
            # Run together they read as one long number, so the label is kept
            # once and the numbers listed.
            head, rest = agency[0], agency[1:]
            label, first = head, ""
            for marker in ("Nos.", "No.", "Nos", "No"):
                at = head.find(marker)
                if at >= 0:
                    label = head[: at + len(marker)]
                    first = head[at + len(marker) :].strip()
                    break
            numbers = [n for n in ([first] + rest) if n]
            case["lower_docket"] = f"{label} " + "; ".join(numbers) \
                if numbers else head
        if title:
            # The court hangs a footnote on its own label ('MEMORANDUM*'); the
            # mark belongs to the note, not to the title.
            crit["title"] = title.rstrip("*†‡∗ ")
        # ...and on the submission date the same way ('February 11, 2026**').
        for key, value in list(crit.items()):
            if key.startswith("date_") and isinstance(value, str):
                crit[key] = value.rstrip("*†‡∗ ")
        # THE CLERK'S STAMP IS NOT PART OF THE COURT'S NAME. CA9 sets 'FILED /
        # <date> / MOLLY C. DWYER, CLERK / U.S. COURT OF APPEALS' in the top
        # right corner, and its last line merged onto the banner's own row.
        court = crit.get("court")
        if court:
            at = court.lower().find(self.circuit_phrase)
            if at >= 0:
                crit["court"] = court[: at + len(self.circuit_phrase)].strip()
        self._publish_criteria(doc, crit)

    def _tail_kind(self, text):
        """CA9 DOES NOT PRINT APPEARANCES IN ITS HEADMATTER, or so rarely that
        anything the shared reader claims is something else wearing an
        appearance's clothes.

        Its order is: the caption in two columns — parties on the left, docket
        numbers on the right — then the court below, then the dates and the
        place of submission, then the panel, then the authors. No counsel
        band anywhere in it, so the field stays absent."""
        return "summary"
    body_baseline_x0 = 54.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    # The family's blanket page-2 cutoff (95pt) assumes a deep running header.
    # The Ninth has none that deep: its reporter-format published opinions
    # print ONE short head line ('2 USA V. SANCHEZ') inside the top 40pt and
    # open real text at top~73, and its memorandum format prints no head at
    # all. So the blanket cutoff swallowed the first one or two real lines of
    # every continuation page — headmatter rows ('Argued and Submitted ...',
    # 'Opinion by Judge R. Nelson;'), body text, and even a concurrence byline.
    # The head is identified by its own geometry below instead.
    page2_header_cutoff = 0.0
    # ... and the head is let THROUGH filter_margins (default margin_top 39 sits
    # just below it) so it can be recorded in `dropped` rather than vanish.
    margin_top = 30.0

    # Running-head signature: pinned in the top band and set smaller than the
    # 12/14pt body (8pt, or 10pt in some volumes). Footnote text is also 10pt
    # but always sits below the footnote rule, far outside this band.
    running_head_max_top = 60.0
    running_head_max_size = 10.5
    running_head_first_page = 1  # an amended opinion heads page 1 as well

    # A tight-gapped run inside the Ninth's single-spaced body is NOT an
    # advisory notice — it is content whose leading is compressed, e.g. the
    # two-column sentencing-guidelines table in United States v. Kheyre, whose
    # wrapped cells sit ~7pt apart. Dropping 'notice' segments (the default,
    # right for double-spaced courts) silently deleted those rows.
    drop_notice_in_body = False

    def extract(self, pdf_path):
        self._pc_order_starts = set()
        return super().extract(pdf_path)

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        return self._join_wrapped_bylines(self._drop_head_band(page, lines))

    # ------------------------------------------------------- wrapped bylines
    def _join_wrapped_bylines(self, lines):
        """Fold a byline that WRAPS onto a second line back into one line.

        A separate writing names its kind in the byline, which can run past the
        reporter measure's 288pt column:

            BEA, Circuit Judge, concurring in part and dissenting in
            part:
            BERZON, Circuit Judge, with whom W. FLETCHER,
            Circuit Judge, joins, concurring:

        The terminator then sits on the SECOND line, so the first line parses as
        an unterminated byline (or not at all) and the remainder is orphaned as
        a stray body paragraph — which also mis-typed the writing, since the
        'dissenting in part' half of the kind never reached the parser.

        A join is only made when the two lines TOGETHER parse as a terminated
        byline and the second is part of the same single-spaced run (not a new,
        indented paragraph), so ordinary prose can never be folded."""
        out = []
        skip = False
        for i, ln in enumerate(lines):
            if skip:
                skip = False
                continue
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            joined = self._byline_join_candidate(ln, nxt)
            if joined is not None:
                out.append(joined)
                skip = True
                continue
            out.append(ln)
        return out

    def _byline_join_candidate(self, line, nxt):
        """The single merged line for a two-line byline, or None."""
        if nxt is None:
            return None
        text = (line.get("text") or "").strip()
        if not text or text.endswith((".", ":")) or "," not in text:
            return None
        if not _is_name(text[: text.index(",")].strip()):
            return None
        # Same single-spaced run, and the continuation is not a fresh indented
        # paragraph (a byline's runover returns to the body margin).
        gap = nxt.get("top", 0) - line.get("top", 0)
        if not 0 < gap <= self.gap_single_max + 2:
            return None
        if nxt.get("x0", 0) > line.get("x0", 0) + 2:
            return None
        merged = self._rebuild_line(
            line, list(line.get("chars") or []) + list(nxt.get("chars") or [])
        )
        merged["text"] = f"{text} {(nxt.get('text') or '').strip()}"
        split = self._byline_split(merged)
        if split is None or not split[0].rstrip().endswith((".", ":")):
            return None
        return merged

    # ------------------------------------------------------------- bylines
    # Most Ninth bylines spell the bench title out ('NGUYEN, Circuit Judge:'),
    # which the family detector already reads. But the published reports also
    # set a separate writing with the ABBREVIATED reporter title —
    # 'R. Nelson, J., concurring:' / 'Forrest, J., dissenting.' — and those were
    # invisible to a detector keyed on the word 'Judge'. The writing was then
    # swept into the majority, and because its footnotes restart at 1 they
    # collided with the majority's labels and were discarded outright.
    abbrev_bench_titles = ("C.J.", "J.")

    def _byline_split(self, line):
        # The page-1 headmatter names the writings in CENTERED descriptor rows
        # ('Opinion by Judge Nguyen;' / 'Concurrence by Judge R. Nelson' /
        # 'Per Curiam Opinion'). A real byline is flush at the body's left
        # margin, so a centered candidate is a descriptor, not an opinion start
        # — without this, 'Per Curiam Opinion' opened an opinion in the middle
        # of the caption and swallowed the rest of the headmatter.
        if self.line_alignment(line, getattr(self, "_page1_width", 612.0)) == "C":
            return None
        found = super()._byline_split(line)
        if found is not None:
            return found
        return self._abbrev_byline_split((line.get("text") or "").strip())

    def _abbrev_byline_split(self, text):
        """The abbreviated-title byline, as (byline_text, inline_body) or None.

        Everything between the name's comma and the abbreviation must be title
        qualifiers, which is what keeps a citation parenthetical out: in
        'Flores Molina, 37 F.4th at 648 (VanDyke, J., dissenting).' the run up
        to the 'J.' is sentence text, not a title run, so it is rejected."""
        if not text or "," not in text:
            return None
        comma = text.index(",")
        if not _is_name(text[:comma].strip()):
            return None
        for title in self.abbrev_bench_titles:
            start = comma + 1
            while True:
                idx = text.find(title, start)
                if idx == -1:
                    break
                end = idx + len(title)
                if not self._is_title_run(text[comma + 1 : idx]):
                    start = end
                    continue
                j = end
                while j < len(text) and text[j] == " ":
                    j += 1
                if j >= len(text):
                    return text, ""
                if text[j] in ".:":
                    return text[: j + 1], text[j + 1 :].strip()
                if text[j] == ",":
                    k = self._kind_clause_end(text, j)
                    if k is not None:
                        return text[: k + 1], text[k + 1 :].strip()
                start = end
        return None

    def parse_author_line(self, text):
        found = super().parse_author_line(text)
        if found is not None:
            return found
        # Same abbreviated form, for LABELLING (name / title / concur-dissent
        # kind). The family parser demands the spelled-out office in the part
        # after the comma, so 'Forrest, J., dissenting.' produced no kind and
        # the writing would have been typed 'majority'.
        split = self._abbrev_byline_split((text or "").strip())
        if split is None:
            return None
        byline = split[0].strip().rstrip(".:").strip()
        if "," not in byline:
            return None
        name, rest = byline.split(",", 1)
        name, rest = name.strip(), rest.strip()
        low = rest.lower()
        kind = None
        for k in (
            "concurring in part and dissenting in part",
            "concurring in the judgment and dissenting in part",
            "concurring and dissenting",
            "concurring in the judgment",
            "concurring in part",
            "dissenting in part",
            "concurring",
            "dissenting",
        ):
            if k in low:
                kind = k
                break
        return (name, rest, kind)

    # ---------------------------------------------------------- order style
    # The reporter format hands off from headmatter to the ruling with a
    # standalone BOLD CENTERED heading: 'OPINION' for an argued opinion,
    # 'ORDER' for a motions ruling (a stay pending appeal, an amendment on
    # rehearing). A signed opinion follows the heading with a byline, but an
    # unsigned ORDER has none — and the family's fallback looks for a
    # 'Before … Circuit Judges.' roster, which in this format WRAPS ('Before:
    # Andrew D. Hurwitz and Roopali H. Desai, Circuit / Judges.*') so the
    # 'Judge' never appears on the roster's own line. The result was that the
    # whole order (Background, Discussion, disposition) stayed in the
    # headmatter and the document reported zero opinions.
    _BODY_HEADINGS = ("ORDER", "OPINION")

    def _percuriam_start(self, all_segments):
        self._pc_order_starts = set()
        heading = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if len(seg) != 1:
                continue
            line = seg[0]
            words = self.line_plain_text(line).strip().upper().split()
            if not words or words[-1] not in self._BODY_HEADINGS:
                continue
            if len(words) > 2:  # 'ORDER' / 'AMENDED ORDER', never a sentence
                continue
            if self.line_alignment(
                line, getattr(self, "_page1_width", 612.0)
            ) != "C" or not self._line_all_bold(line):
                continue
            heading = i
        if heading is not None:
            start = self._first_content_after(all_segments, heading)
            if start is not None:
                word = self.line_plain_text(all_segments[heading][1][0]).strip().upper()
                if word.split()[-1] == "ORDER":
                    self._pc_order_starts = {start}
                return start
        return super()._percuriam_start(all_segments)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        # The document STYLE follows the heading that opened the ruling: an
        # unsigned ruling under the bold 'ORDER' heading is an order, even
        # though locating its body gives it an author index.
        if getattr(self, "_pc_order_starts", None):
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # A ruling opened by the bold 'ORDER' heading is an order, not a
        # majority opinion; the review page and the casebody both key off type.
        if op_start in getattr(self, "_pc_order_starts", set()):
            op.type = "order"
        return op

    def _first_content_after(self, all_segments, i):
        for j in range(i + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def find_footnote_separator(self, page):
        """The separator is anchored at the BODY's left margin, so measure that
        margin rather than assume it.

        The corpus carries two layouts: the reporter format sets its body at
        x0≈54, and a slip format sets it at x0≈72. A window fixed on the
        reporter's margin (50–60) missed every rule in the slip format, so
        those opinions returned no footnotes at all while their marks stayed in
        the text (dickinson_v._trump: 8 marks, 0 footnotes)."""
        from collections import Counter

        starts = Counter(round(w["x0"]) for w in page.extract_words())
        anchor = starts.most_common(1)[0][0] if starts else 54
        return self._sep_at(page, anchor - 6, anchor + 6)

    def skip_headmatter_segment(self, seg) -> bool:
        if seg and (seg[0].get("text") or "").strip().upper() in (
            "FOR PUBLICATION",
            "NOT FOR PUBLICATION",
        ):
            return True
        return super().skip_headmatter_segment(seg)

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Give the SUMMARY and COUNSEL blocks their own fields.

        CA9 prints two named sections between the panel line and the opinion:
        a court-written SUMMARY (a topic head plus several paragraphs, marked
        with an asterisk noting it is not part of the opinion) and the COUNSEL
        block. Both were landing in the headmatter as undifferentiated rows —
        ``syllabus`` and ``attorneys`` were empty on every file — so the
        summary read as though it were part of the caption.

        The page names both sections, so the boundaries are read off the
        headings rather than guessed."""
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        rows = result.get("summary", [])

        def heading(row):
            if not isinstance(row, str):
                return ""
            return " ".join(_plain(row).split()).rstrip("*").strip().upper()

        start = next(
            (i for i, r in enumerate(rows) if heading(r) == "SUMMARY"), None
        )
        counsel = next(
            (i for i, r in enumerate(rows) if heading(r) == "COUNSEL"), None
        )
        if start is None and counsel is None:
            return result

        def content(chunk):
            return [
                r
                for r in chunk
                if isinstance(r, str) and _plain(r).strip()
                and not _plain(r).strip().startswith("__")
            ]

        keep = list(rows)
        keep_source = list(rows)
        if start is not None:
            end = counsel if counsel is not None and counsel > start else len(rows)
            # From the heading INCLUSIVE. The asterisks on 'SUMMARY**' carry a
            # footnote saying the summary is not part of the opinion, so the
            # row is content; starting one row later dropped it from every
            # section and it surfaced as unplaced.
            body = content(rows[start:end])
            if body:
                result["syllabus"] = body
            keep = [r for i, r in enumerate(keep) if not (start <= i < end)]
        if counsel is not None:
            # Everything after the COUNSEL heading is the counsel block. It
            # moves OUT of the headmatter into its own section — the reporter
            # prints it under its own heading, and a page of counsel sitting in
            # the caption read as though it were part of the case caption.
            # The OPINION banner trails the counsel block; it belongs to the
            # opinion, not to counsel, so it stays behind for the banner
            # rehoming to pick up.
            end = len(rows)
            for i in range(len(rows) - 1, counsel, -1):
                text = " ".join(_plain(rows[i]).split()) if isinstance(rows[i], str) else ""
                if not text:
                    continue
                if text.rstrip("*").upper() in ("OPINION", "ORDER"):
                    end = i
                break
            # From the heading INCLUSIVE, for the same reason as the summary:
            # taking only the rows AFTER it left 'COUNSEL' with no home and it
            # surfaced as unplaced content on every published file.
            tail = content(rows[counsel:end])
            if tail:
                result["attorneys"] = "\n".join(tail)
                keep = [
                    r for i, r in enumerate(keep_source)
                    if not (counsel <= i < end)
                    and not (start is not None and start <= i < counsel)
                ]
        result["summary"] = keep
        return result
