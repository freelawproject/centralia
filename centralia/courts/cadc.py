"""United States Court of Appeals for the District of Columbia Circuit."""

from __future__ import annotations

from ._circuit import (
    _DOC_TITLE_WORDS,
    FederalCircuitBase,
    _HISTORY_OPENERS,
    _plain,
)


class DCCircuit(FederalCircuitBase):
    court_id = "cadc"
    court_label = (
        "United States Court of Appeals for the District of " "Columbia Circuit."
    )
    circuit_phrase = "district of columbia circuit"

    # Headmatter criteria: drawn dividers; dates, docket and caption share the first zone.
    parse_criteria_enabled = True

    # A district court's own number, as CADC prints it under the appeal's
    # docket: a chamber, a colon, the year, the case type, the number.
    _TRIAL_TYPES = ("-cv-", "-cr-", "-mc-", "-md-", "-ms-", "-sc-")

    # ------------------------------------------------ unpublished judgments
    # Below this share of the document left after a byline, the 'byline' is
    # the closing signature. Measured, not absolute: see _is_closing_signature.
    _SIGNATURE_TAIL_MAX = 0.08

    def find_authors(self, all_segments) -> list:
        """Drop a lone byline that turns out to be the closing signature.

        Only when it is the ONLY one found — a genuine short concurrence at
        the end of a multi-writing opinion leaves just as little behind it, and
        must not be discarded."""
        found = super().find_authors(all_segments)
        if len(found) == 1 and self._is_closing_signature(all_segments, found[0]):
            return []
        return found

    def _is_closing_signature(self, all_segments, i) -> bool:
        """A 'byline' with almost nothing after it is the closing signature.

        An unpublished judgment carries no author byline at all. It prints a
        centered bold 'Per Curiam' near the END, above the clerk's 'FOR THE
        COURT:' block. Read as a byline that anchors the opinion's start at the
        signature — and since headmatter is *defined* as everything preceding
        the first opinion, municipal_energy_agency_of_nebraska came out as 75
        caption rows against 3 body blocks, and np_red_rock as 68 against 3.

        Judged as a SHARE of the document rather than by what sits below it. An
        earlier attempt asked whether any line below returned to the body rail;
        np_red_rock defeated it, because page 9 ends with two lines of a
        footnote carried over from page 8, set at the body rail and at body
        size, with no rule and no size drop to separate them."""
        counts = [len(seg) for _p, seg, _k in all_segments]
        total = sum(counts)
        if not total:
            return False
        return sum(counts[i + 1:]) / total <= self._SIGNATURE_TAIL_MAX

    # A banner set this many times the document's body size is a placeholder
    # standing in FOR the text, not a heading over it.
    _BANNER_SIZE_RATIO = 2.0

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """A sealed-opinion placeholder is a NOTICE, not a lost opinion.

        When this court seals an opinion it still dockets a public sheet in its
        place: the masthead, the docket and term, the caption, the 'BEFORE:'
        roster — and then, where the opinion would be, two banner rows set at
        28pt against the 12pt body ('OPINION UNDER SEAL' / 'NOT AVAILABLE TO
        THE PUBLIC') and nothing after them. (``john_doe_v._sec``; the text
        arrives later as the separate ``john_doe_v._sec_public_reissued_
        opinion``.) There is no body to parse, so an empty ``opinions`` list is
        the correct outcome and the reviewer should not be sent hunting for a
        parser bug.

        The evidence is typographic and needs no wording: nothing authored the
        document, no judgment or order title anchors it, and the LAST thing on
        the sheet is an oversized bold banner. A real opinion cannot end that
        way — its last line is prose, a footnote or a signature.
        """
        if not author_indices and self._ends_in_banner(all_segments):
            from ..models import DocType

            return DocType.NOTICE
        return super().classify_document_type(
            all_segments, author_indices, n_pages
        )

    def _ends_in_banner(self, all_segments) -> bool:
        """True when the document's final rows are an oversized bold banner
        measured against the size the document itself sets most often."""
        lines = [
            line
            for _page, seg, _kind in all_segments
            for line in seg
            if self.line_plain_text(line).strip()
        ]
        if not lines:
            return False
        counts: dict = {}
        for line in lines:
            size = round(self.line_meta(line)[0], 1)
            counts[size] = counts.get(size, 0) + 1
        body_size = max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]
        size, _font, bold = self.line_meta(lines[-1])
        return bold and size >= body_size * self._BANNER_SIZE_RATIO

    def _order_fallback(self, all_segments) -> list:
        """Anchor an unsigned judgment on its own title row.

        The shared fallback looks for a title opening with 'ORDER'. A judgment
        titles itself 'J U D G M E N T' — letter-spaced, bold, centered — so
        the spacing has to come out before the word is recognisable."""
        start = next(
            (
                i
                for i, (_p, seg, _k) in enumerate(all_segments)
                if seg and self._is_judgment_title(seg[0])
            ),
            None,
        )
        if start is None:
            return super()._order_fallback(all_segments)
        self._order_start = start
        self._order_author = "Per Curiam"
        return [start]

    def _is_judgment_title(self, line) -> bool:
        text = "".join(self.line_plain_text(line).split())
        if not text or len(text) > 40:
            return False
        return text.lower() in _DOC_TITLE_WORDS

    @classmethod
    def _is_trial_docket(cls, text):
        """'1:25-cv-03581-UNA' — the court BELOW, not this appeal.

        CADC sets it on a row of its own directly under the appeal's docket,
        and it answers the docket test like any other number: it opened a
        second, empty case, and its own text was read as the first case's
        name."""
        bare = " ".join(text.split())
        if " " in bare or ":" not in bare:
            return False
        return any(kind in bare.lower() for kind in cls._TRIAL_TYPES)

    def _is_disposition(self, text):
        """CADC names who wrote what under the roster:

            Opinion for the Court filed by Circuit Judge RAO.
            Concurring opinion filed by Circuit Judge WALKER.

        It reads like a byline and names a judge like a roster, so with no
        field of its own it was left out of the criteria entirely."""
        low = " ".join(text.split()).lower()
        return "opinion" in low and "filed by" in low

    def _counsel_band(self, doc):
        """The appearances, taken from the band that holds them.

        CADC's published opinions set counsel in the ruled band BETWEEN the
        origin and the roster, and the entries announce nothing about
        themselves — they open with the advocate's name ('Brett A. Shumate,
        Assistant Attorney General, U.S. Department of Justice, ...'). There
        is nothing here to recognise, so the band is delimited instead: after
        the origin, before 'Before:', and nothing else is ever there."""
        texts = [
            (i, _plain(r).strip())
            for i, r in enumerate(doc.summary)
            if isinstance(r, str) and _plain(r).strip()
        ]
        start = next(
            (
                i
                for i, t in texts
                if t.lower().startswith(_HISTORY_OPENERS)
            ),
            None,
        )
        end = next(
            (i for i, t in texts if t.upper().startswith("BEFORE")), None
        )
        if start is None or end is None or end <= start:
            return None
        rows = [
            t
            for i, t in texts
            if start < i < end
            and t.strip("_- ")
            and t != self.HEADMATTER_DIVIDER      # the wall, not an appearance
            and not self._is_docket_text(t)
        ]
        return "\n".join(rows) or None

    def parse_criteria(self, doc):
        """The shared walk, then CADC's own layout read where it differs.

        CADC's order form names its parties in ORDINARY TITLE CASE, which no
        party test recognises — every other circuit sets them in caps:

            No. 26-1049                September Term, 2025
            DOD-03/03/2026 Order            <- the order under review
            Filed On: April 8, 2026
            Anthropic PBC,
                  Petitioner
            v.
            United States Department of War and Peter B. Hegseth, ...
                  Respondents
            BEFORE: Henderson, Katsas, and Rao, Circuit Judges
            O R D E R

        So the rows fell through, the agency's order number became the case
        name, and body text below opened a second case. Here the caption does
        not need recognising — it is BOUNDED: everything between the filing
        date and the roster is the parties, and nothing else is ever there."""
        super().parse_criteria(doc)
        self._read_bounded_caption(doc)
        crit = doc.criteria or {}
        counsel = crit.get("counsel") or self._counsel_band(doc)
        if not counsel:
            return
        crit["counsel"] = counsel
        # THE ORIGIN IS ONE STATEMENT, NOT EVERYTHING UNDER IT. CADC sets the
        # appearances directly beneath the appeal-from line with no wall
        # between them, so the origin ran on and took the whole counsel block
        # with it ('Appeal from the United States District Court for the
        # District of Columbia (No. 1:20-cv-00784) Matthew H. Lembke argued
        # the cause for appellant. With him on the briefs were ...'). The
        # appearances are known by now, so the origin is cut where they start.
        opener = counsel.split("\n")[0][:48]
        for case in crit.get("cases") or []:
            history = case.get("prior_history") or ""
            at = history.find(opener) if opener else -1
            if at > 0:
                case["prior_history"] = history[:at].strip()
        self._publish_criteria(doc, crit)
        crit = doc.criteria or {}
        cases = crit.get("cases") or []
        if not cases:
            return
        trial = next(
            (
                t
                for t in (
                    _plain(r).strip() for r in doc.summary if isinstance(r, str)
                )
                if self._is_trial_docket(t)
            ),
            None,
        )
        if trial:
            cases[0].setdefault("lower_docket", None)
            if not cases[0].get("lower_docket"):
                cases[0]["lower_docket"] = trial
        changed = False
        for case in cases:
            rows = [t for t in case.get("caption") or []
                    if not self._is_trial_docket(t)]
            if rows != (case.get("caption") or []):
                case["caption"] = rows
                case["case_name"] = " ".join(rows)
                changed = True
        # A CASE WITH NO NAME IS NOT A CASE. Once the trial docket stops
        # opening one, what is left behind is an empty record carrying a copy
        # of the appeal's own number.
        kept = [
            c
            for c in cases
            if (c.get("case_name") or "").strip() or c.get("prior_history")
        ]
        if kept and len(kept) != len(cases):
            crit["cases"] = kept
            changed = True
        if changed or trial:
            self._publish_criteria(doc, crit)

    body_baseline_x0 = 156.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    # The D.C. Circuit prints NO running header on continuation pages. Most of
    # its opinions set a deep top margin (nothing above ~130pt), but its
    # unpublished dispositions and its bound opinions open real text at top~73-75
    # — a '* * *' section break, a body paragraph, an 'A' subheading — and the
    # family's blanket 95pt cutoff deleted it. Where a page 2+ DOES carry the
    # 'United States Court of Appeals / FOR THE DISTRICT OF COLUMBIA CIRCUIT'
    # banner from top~39, that is a second order's COVER page, i.e. content, not
    # furniture. Lower the cutoff to the page edge and let ``margin_top`` bound it.
    page2_header_cutoff = 30.0

    # CADC once needed the ruleless size-drop path; it no longer does. Since
    # a2c4b77 taught the chain to read page.curves, every cadc separator is
    # found as a rect, line or curve — measured: ZERO cadc pages reach the
    # size-drop path. The opt-in is removed rather than left as a latent risk.

    def find_footnote_separator(self, page):
        return self._sep_at(page, 150, 165) or self._footnote_zone_by_size(page)

    def extract_page_tables(self, page):
        """Reject a three-line prose false positive in dense footnotes.

        pdfplumber can interpret word gaps in a fully justified D.C. Circuit
        footnote as eight or nine narrow columns.  A real table with that many
        columns is not only three prose baselines tall; retaining this guard at
        the court boundary avoids weakening table support elsewhere.
        """
        out = []
        for table in super().extract_page_tables(page):
            rows = table.get("rows") or []
            n_cols = max((len(row) for row in rows), default=0)
            if len(rows) <= 3 and n_cols >= 8:
                continue
            out.append(table)
        return out

    def _read_bounded_caption(self, doc):
        """Take the caption from between the filing date and the roster."""
        crit = doc.criteria or {}
        cases = crit.get("cases") or []
        if not cases:
            return
        texts = [
            (i, _plain(r).strip())
            for i, r in enumerate(doc.summary)
            if isinstance(r, str) and _plain(r).strip()
        ]
        start = next(
            (i for i, t in texts if t.lower().startswith(("filed on", "filed:"))),
            None,
        )
        end = next(
            (i for i, t in texts if t.upper().startswith("BEFORE")), None
        )
        if start is None or end is None or end <= start:
            return
        # ...and it stops at the origin. CADC states where the case came from
        # inside the same span ('ON APPEAL FROM THE UNITED STATES DISTRICT
        # COURT FOR THE DISTRICT OF COLUMBIA'), and taken as parties it ran
        # onto the end of the case name.
        rows, tail = [], []
        for i, t in texts:
            if not (start < i < end) or not t.strip("_- "):
                continue
            if self._is_trial_docket(t):
                continue
            if tail or t.lower().startswith(_HISTORY_OPENERS):
                tail.append(t)
            else:
                rows.append(t)
        if not rows:
            return
        # The order under review sits ABOVE the filing date, on its own row
        # under the appeal's docket ('DOD-03/03/2026 Order'). It is what the
        # case came from, not what the case is called.
        origin = [
            t
            for i, t in texts
            if i < start
            and not self._is_court_banner(t)
            and not self._is_docket_text(t)
            and not t.strip("_- ") == ""
        ]
        case = cases[0]
        case["caption"] = rows
        case["case_name"] = " ".join(rows)
        stated = " ".join(tail) if tail else " ".join(origin)
        if stated and not case.get("prior_history"):
            case["prior_history"] = stated
        elif tail and case.get("prior_history"):
            case["prior_history"] = " ".join(tail)
        # Everything below the roster is the court's own writing; a second
        # case read out of it is not one.
        crit["cases"] = [cases[0]]
        self._publish_criteria(doc, crit)
