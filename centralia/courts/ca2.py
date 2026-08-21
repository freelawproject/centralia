"""United States Court of Appeals for the Second Circuit."""

from __future__ import annotations

from collections import Counter

import pdfplumber

from ..base import BaseExtractor, _BENCH_WORDS
from ._circuit import FederalCircuitBase
from .generic import _is_name


class SecondCircuit(FederalCircuitBase):
    court_id = "ca2"
    court_label = "United States Court of Appeals for the Second Circuit."
    circuit_phrase = "second circuit"

    # CA2 rules its headmatter with drawn dividers (published opinion) or typed
    # '-----' rules (summary order), and opens the roster with 'PRESENT:' on
    # the latter. The term line runs the argued/decided dates together above
    # the docket.
    #
    # The shared row-shape walk cannot read this court: it put the defendants
    # into the counsel field, left the docket empty, and pulled the party status
    # labels into the summary. CA2's sections are separated GEOMETRICALLY — an
    # indented caption block between typed rules, a hanging-indent counsel block
    # with its own label column — and its party names are caps on one record and
    # title case on the next, so text shape alone cannot tell them apart.
    #
    # So CA2 reads its own headmatter, off x-position and rule geometry, per the
    # archetype the document belongs to. Summary orders (and the en banc denials
    # that share their skeleton) are read by ``_read_summary_order``; the
    # published-opinion archetypes are not read yet and record nothing rather
    # than publish values known to be wrong.
    parse_criteria_enabled = True
    criteria_has_summary = True

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Keep the headmatter's LINES, not just its rendered rows.

        ``parse_criteria`` runs at the end of extraction, against
        ``doc.summary`` — strings, from which x-position and font are gone. CA2's
        sections are told apart by exactly those, so the reader needs the lines
        the rows were built from."""
        self._hm_segs = list(headmatter_segs)
        # The published-opinion archetype partitions page 1 with DRAWN rules;
        # they are the zone boundaries its reader walks.
        self._hm_rules = sorted(page1_rules or [])
        return super().extract_headmatter(headmatter_segs, page1_rules)

    # CA2's headmatter comes in named STYLES, and each is read by its own
    # walker. A style is a layout contract, not a document type: it says where
    # the sections are and what marks their edges.
    #
    #   'stated-term order'  — the summary order and the en banc denial that
    #        shares its skeleton. Bold-caps banner, the convening recital, a
    #        'Present:' roster, and a LEFT two-column caption between typed
    #        underscore rules. 18 of the 50 records.
    #
    #   'engraved ladder'    — the published opinion. An engraved (Old English)
    #        masthead over a CENTERED column rung by four short drawn rules:
    #        term/dates, caption, origin, then the panel. 19 of the 50.
    #
    # Anything else records nothing rather than publish a misreading.
    #   'numbered paper'     — the published opinion set on NUMBERED paper: a
    #        left-margin line-number gutter, typed rules ('______' or '- - - -')
    #        instead of drawn ones, and every row flush LEFT rather than
    #        centered. Its masthead is engraved on some records (cruz) and a
    #        caps banner on others (campbell), but the skeleton is the ladder's:
    #        term, dates, docket, caption, origin, panel. It therefore shares the
    #        ladder's reader — the sections are found by landmark, and the
    #        landmarks do not move when the column does. 6 of the 50.
    #   'plain ladder'       — the same ladder with the masthead set in the body
    #        face at display size instead of engraved. 9 of the 50.
    STYLE_STATED_TERM = "stated-term order"
    STYLE_ENGRAVED_LADDER = "engraved ladder"
    STYLE_PLAIN_LADDER = "plain ladder"
    STYLE_NUMBERED_PAPER = "numbered paper"

    def headmatter_style(self) -> str | None:
        """Which headmatter style this document is set in, or None."""
        if getattr(self, "_style", "").startswith("summary_order"):
            return self.STYLE_STATED_TERM
        # The engraved masthead alone identifies the style. The ladder of rules
        # is its LOOK, not its fingerprint: the group draws its rules at four
        # different widths, doubles them (knapp draws one rule twice, 0.9pt
        # apart), and two records draw none at all. Numbered paper is excluded —
        # an engraved masthead over a line-number gutter is its own style.
        if self._style == "opinion_numbered":
            return self.STYLE_NUMBERED_PAPER
        # ENGRAVING IS A FONT CHOICE, NOT THE STYLE. ullah sets the identical
        # ladder — same centered column, same landmarks in the same order — with
        # its masthead in Palatino at 20pt instead of Old English, and gating on
        # the engraved face left nine records recording nothing at all. The two
        # are named apart because the catalogue tracks the look, but they are one
        # layout and share one reader.
        if self._style == "opinion":
            return (
                self.STYLE_ENGRAVED_LADDER
                if getattr(self, "_engraved", False)
                else self.STYLE_PLAIN_LADDER
            )
        return None

    def parse_criteria(self, doc):
        if not self.parse_criteria_enabled:
            return
        style = self.headmatter_style()
        if style == self.STYLE_STATED_TERM:
            crit = self._read_summary_order()
        elif style in (
            self.STYLE_ENGRAVED_LADDER,
            self.STYLE_PLAIN_LADDER,
            self.STYLE_NUMBERED_PAPER,
        ):
            # One reader, two styles: numbered paper prints the ladder's sections
            # flush left with typed rules instead of centered with drawn ones,
            # and the reader keys on the landmarks, not the column.
            crit = self._read_engraved_ladder()
        else:
            # Not a style we read yet. Record nothing rather than publish the
            # shared walk's misreading.
            return
        if crit:
            crit["headmatter_style"] = style
            self._publish_criteria(doc, crit)

    # ------------------------------------------------------- headmatter reader
    def _hm_lines(self):
        """The headmatter's lines in document order, with geometry intact.

        Page 1's footnote separator is the headmatter's floor: the caption's own
        footnote sits below it ('* The Clerk of Court is respectfully directed to
        amend the official case caption as set forth above'), and it is a
        footnote, not a headmatter row.

        Records that draw no separator at all get one inferred from the note's
        reference mark (see ``_marked_footnote_top``), so by the time the reader
        runs there is a floor either way and the note's lines are already gone
        from the headmatter — continuation lines included."""
        out = []
        for seg in getattr(self, "_hm_segs", None) or ():
            for line in seg:
                if not (line.get("text") or "").strip():
                    continue
                out.append(line)
        out.sort(key=lambda ln: (self._page_number([ln]), ln.get("top", 0)))
        floor = getattr(self, "_hm_footnote_top", None)
        if floor is None:
            return out
        return [
            line
            for line in out
            if self._page_number([line]) != 1 or line.get("top", 0) <= floor
        ]

    @staticmethod
    def _is_underscore_rule(text) -> bool:
        """A typed rule — the divider CA2 draws with underscores or hyphens."""
        bare = text.replace(" ", "")
        return len(bare) >= 8 and set(bare) <= {"_", "-"}

    @staticmethod
    def _is_caps(text) -> bool:
        letters = [c for c in text if c.isalpha()]
        return bool(letters) and all(c.isupper() for c in letters)

    @staticmethod
    def _opens_caps(text, least=2) -> bool:
        """True when the row OPENS with a run of all-caps words.

        A caption sets the party's name in caps and may follow it with a
        lower-case descriptor, so the opening run is what identifies the row."""
        run = 0
        for token in text.split():
            letters = [c for c in token if c.isalpha()]
            if letters and all(c.isupper() for c in letters):
                run += 1
                continue
            break
        return run >= least

    @staticmethod
    def _is_italic_font(font) -> bool:
        """True for an italic face, however the PDF spells it.

        Most of the corpus names the face ('...-ItalicMT', '...-Oblique'), but
        the numbered-paper records carry the slant as a FLAG on the roman name
        ('PalatinoLinotype-Roman,I' / '...,BI') — so campbell's party status
        labels read as roman and were filed as party names."""
        if "Italic" in font or "Oblique" in font:
            return True
        _, _, flags = font.rpartition(",")
        return bool(flags) and flags.upper() in ("I", "BI", "IB")

    @classmethod
    def _line_all_italic(cls, line) -> bool:
        seen = False
        for char in line.get("chars") or ():
            glyph = char.get("text") or ""
            if not glyph.strip() or not glyph.isalnum():
                continue
            seen = True
            if not cls._is_italic_font(char.get("fontname") or ""):
                return False
        return seen

    # 'on the 9th day of June, two thousand twenty-six.' — CA2 spells the year
    # out in the convening recital, and that recital is the ONLY statement of
    # the decision date on a summary order (there is no 'Decided:' line).
    _ONES = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
        "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    }
    _TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}

    @classmethod
    def _spelled_year(cls, words):
        """1000*n + … from 'two thousand twenty-six', or None."""
        total = seen = 0
        index = 0
        while index < len(words):
            word = words[index].strip(".,").lower()
            if word == "thousand":
                total = (total or 1) * 1000
                seen = 1
            elif word in cls._ONES:
                total += cls._ONES[word]
                seen = 1
            elif "-" in word and word.split("-")[0] in cls._TENS:
                tens, _, ones = word.partition("-")
                total += cls._TENS[tens] + cls._ONES.get(ones, 0)
                seen = 1
            elif word in cls._TENS:
                total += cls._TENS[word]
                seen = 1
            index += 1
        return total if seen and total >= 1000 else None

    @classmethod
    def _recital_date(cls, text):
        """'June 9, 2026' out of the convening recital, or None."""
        tokens = text.replace(",", " ").split()
        for i, token in enumerate(tokens):
            if token.lower() != "day" or i + 2 >= len(tokens):
                continue
            if tokens[i + 1].lower() != "of":
                continue
            month = tokens[i + 2].strip(".,")
            day = ""
            for back in range(i - 1, -1, -1):
                digits = "".join(c for c in tokens[back] if c.isdigit())
                if digits:
                    day = digits
                    break
            year = cls._spelled_year(tokens[i + 3 :])
            if month and day and year:
                return f"{month} {day}, {year}"
        return None

    def _read_summary_order(self):
        """Dissect a summary-order / en banc-denial headmatter.

        The skeleton is fixed, and every section is announced by something the
        page itself draws or prints:

            <docket> <short case name>        running head
            UNITED STATES COURT OF APPEALS   centered banner
            SUMMARY ORDER                    centered title (absent on en banc)
            At a stated term …                convening recital, carrying the date
            Present:                          opens the roster
                <JUDGE>,  …  Circuit Judges.  the panel
            ______________________            opens the caption
            PARTY NAME,                       caption rail, caps
                Plaintiff-Appellant,          indented + italic: the status
                v.  25-1830-cv                centered: the versus row + docket
            ______________________            closes the caption
            For Plaintiff-Appellant: NAME …   counsel, one entry per party

        The caption is read by COLUMN: a name sits on the caption's own left
        rail, a status label is indented and italic, and the versus row is
        centered. That is what the shared text-shape walk could not do, and why
        it filed the defendants under counsel."""
        lines = self._hm_lines()
        if not lines:
            return None
        # The rail is measured inside the CAPTION, not across the headmatter. The
        # advisory block and the recital run to the page's own left margin (72),
        # but the caption can be inset from it (alsonidar sets its parties at
        # 108) — so a headmatter-wide minimum put every party name on the wrong
        # side of the column test and dropped all of them.
        rail = self._caption_rail(lines)

        crit = {}
        banner, panel, counsel, statuses = [], [], [], []
        roster = []
        cases, cur = [], None
        state = "banner"
        panel_open = False

        def open_case():
            # ``sides`` collects the PARTY NAMES either side of the versus row,
            # kept apart from ``caption`` (which holds every row verbatim, status
            # labels included, for fidelity). The case name is built from the
            # names alone — joining the caption wholesale reads
            # 'AMANDA BROOKS, Plaintiff-Appellant, BRIGHT HORIZONS …'.
            return {
                "docket": None,
                "caption": [],
                "prior_history": None,
                "sides": ([], []),
                "side": 0,
                # (top, row) per caption row — the caption is reproduced from
                # these, so the gaps the page leaves between one consolidated
                # case's parties and the next survive as blank lines.
                "rows": [],
            }

        for index, line in enumerate(lines):
            text = " ".join(self.line_plain_text(line).split()).strip()
            if not text:
                continue
            x0 = line.get("x0", 0)
            indented = x0 > rail + 20
            italic = self._line_all_italic(line)
            # Classify on the PLAIN text, but store the MARKED-UP text: a
            # caption's inline emphasis is part of what it says (an italicised
            # 'et al.', a party's italic descriptor), and reading the plain form
            # into the record threw it away.
            rich = " ".join(self.paragraph_text([line]).split()).strip()

            if self._is_underscore_rule(text):
                # The first rule opens the caption; the next closes it and
                # opens the counsel block. A later rule separates a SECOND
                # caption (consolidated appeals stack them), so a rule while
                # the caption is open only closes it if a party was seen.
                if state in ("banner", "panel", "after_panel"):
                    state, cur = "caption", open_case()
                elif state == "caption":
                    if cur and (cur["caption"] or cur["docket"]):
                        cases.append(cur)
                    cur = open_case()
                    state = "caption_or_counsel"
                elif state == "caption_or_counsel":
                    state = "caption_or_counsel"
                continue

            low = text.lower()

            if state == "banner":
                if index == 0 and self._running_head_docket(text):
                    crit["head_docket"] = self._running_head_docket(text)
                    continue
                # The running head's SECOND line is the reporter-style short
                # case name, printed under the docket ('Alsonidar v. Mullin').
                # It is the court's own short form — worth keeping beside the
                # long caption name built from the party rows. Italic on most
                # records but NOT all (alsonidar sets it roman), so the pairing
                # with the docket line above it is what identifies it.
                if index == 1 and crit.get("head_docket") and not crit.get(
                    "short_case_name"
                ):
                    crit["short_case_name"] = text
                    continue
                # The RECITAL is tested before the banner: it opens by naming
                # this very court ('At a stated term of the United States Court
                # of Appeals for the Second Circuit,'), so the banner test
                # matches it too and swallowed the whole recital into `court`.
                if low.startswith("at a stated term"):
                    crit["recital"] = text
                    continue
                if not crit.get("recital") and self._is_court_banner(text):
                    banner.append(text)
                    continue
                if text.upper() == "SUMMARY ORDER":
                    crit["title"] = text
                    crit["publication"] = "non-precedential"
                    continue
                # 'Present:' can stand alone or carry its first judge inline
                # ('PRESENT: RAYMOND J. LOHIER, JR.,').
                if low.rstrip(":") == "present":
                    state, panel_open = "panel", True
                    continue
                if low.startswith("present:"):
                    state, panel_open = "panel", True
                    rest = text.split(":", 1)[1].strip()
                    if rest and self._is_caps(rest):
                        panel.append(rest.rstrip(","))
                        roster.append(rest)
                    continue
                # The recital runs to three lines and its DATE is on the last
                # ('… on the 9th day of June, two thousand twenty-six.'), so the
                # continuation has to be folded back in or the only statement of
                # the decision date on a summary order is lost.
                if crit.get("recital") and not crit["recital"].rstrip().endswith("."):
                    crit["recital"] = f"{crit['recital']} {text}"
                continue

            if state == "panel":
                # The roster closes on its italic bench title ('Circuit
                # Judges.'), which is also what names the office — but only when
                # that title ENDS the roster. A Chief Judge listed first carries
                # her own title mid-roster ('DEBRA ANN LIVINGSTON,' / 'Chief
                # Judge,' / 'ROBERT D. SACK,' / … / 'Circuit Judges.'), and the
                # trailing comma says more judges follow. Closing on the first
                # one left two-thirds of the panel unread.
                if italic and "judge" in low and not text.rstrip().endswith(","):
                    roster.append(text)
                    crit["panel"] = list(panel)
                    crit["panel_line"] = " ".join(roster)
                    panel_open = False
                    state = "after_panel"
                    continue
                # A mid-roster bench title belongs to the judge above it, so it
                # stays in the printed roster line without becoming a name.
                if italic and "judge" in low:
                    roster.append(text)
                    continue
                if self._is_caps(text):
                    panel.append(text.rstrip(","))
                    roster.append(text)
                continue

            if state == "after_panel":
                continue

            if state in ("caption", "caption_or_counsel"):
                if state == "caption_or_counsel" and self._counsel_label(text):
                    state = "counsel"
                elif state == "caption_or_counsel":
                    state = "caption"

            if state == "caption":
                if cur is None:
                    cur = open_case()
                versus = self._versus_docket(line, text, rail)
                if versus is not None:
                    if cur["docket"] is None:
                        cur["docket"] = versus
                    elif versus:
                        cur["docket"] = f"{cur['docket']}; {versus}"
                    # The versus row is the caption's hinge: names above it are
                    # one side of the case, names below it the other. It is kept
                    # in the caption, which is the caption AS PRINTED — the
                    # synthesised short form lives in ``case_name``.
                    cur["caption"].append(rich)
                    cur["rows"].append((line.get("top", 0), rich))
                    cur["side"] = 1
                    continue
                if indented and italic:
                    statuses.append(rich)
                    cur["caption"].append(rich)
                    cur["rows"].append((line.get("top", 0), rich))
                    continue
                if x0 <= rail + 6:
                    # A party name wraps across as many rows as it needs; each
                    # continuation returns to the same rail, so fold it back
                    # into the name above rather than starting a new party.
                    side = cur["sides"][cur["side"]]
                    if cur["caption"] and not self._closes_party(cur["caption"][-1]):
                        cur["caption"][-1] = f"{cur['caption'][-1]} {rich}"
                        if side:
                            side[-1] = f"{side[-1]} {rich}"
                        else:
                            side.append(rich)
                        if cur["rows"]:
                            cur["rows"][-1] = (
                                line.get("top", 0),
                                f"{cur['rows'][-1][1]} {rich}",
                            )
                        else:
                            cur["rows"].append((line.get("top", 0), rich))
                    else:
                        cur["caption"].append(rich)
                        side.append(rich)
                        cur["rows"].append((line.get("top", 0), rich))
                    continue
                # A CONSOLIDATED appeal lists its remaining dockets flush right,
                # under the versus row, each tagged with its role — '23-263
                # (CON)', '23-797 (C)', '23-444 (CON)'. The generic docket test
                # rejects the tag, so every case kept only the lead docket it
                # got from the versus row.
                extra = self._consolidated_docket(text)
                if extra:
                    cur["docket"] = (
                        f"{cur['docket']}; {extra}" if cur["docket"] else f"No. {extra}"
                    )
                continue

            if state == "counsel":
                counsel.append(line)
                continue

        if cur and (cur["caption"] or cur["docket"]):
            cases.append(cur)
        if crit.get("recital"):
            date = self._recital_date(crit["recital"])
            if date:
                crit["date_filed"] = date
        if panel_open and panel:
            crit["panel"] = list(panel)
        if banner:
            crit["court"] = " ".join(banner)
        cases = self._merge_in_re(cases)
        for case in cases:
            name = self._case_name(case)
            if name:
                case["case_name"] = name
            block = self._caption_block(case["rows"])
            if block:
                case["caption_text"] = block
            del case["sides"], case["side"], case["rows"]
        if cases:
            crit["cases"] = cases
        entries = self._read_counsel_block(counsel)
        if entries:
            crit["counsel"] = "\n\n".join(entries)
        if statuses:
            crit["party_status"] = statuses
        return crit or None

    def _read_counsel_block(self, lines):
        """The counsel block as one string per entry.

        CA2 sets counsel in TWO COLUMNS — the party the entry acts for in a
        narrow column on the left, the attorney and firm on the right:

            For Debtor-Appellant Julia F.    Jeffrey L. Herzberg, Jeffrey
            Soussis:                         Herzberg, PC, Hauppauge, NY.

        pdfplumber reports each ROW as one line, so reading the rows in order
        weaves the columns together ('For Debtor-Appellant Julia F. Jeffrey L.
        Herzberg, Jeffrey Soussis: Herzberg, PC, Hauppauge, NY.'). The gutter
        between the columns is wider than any word space, so it is measured off
        the block and used to cut every row in two; each column is then read
        down its own length, and the entry is 'label: attorney'.

        Records that set counsel in ONE column (most of them) yield no
        consistent gutter and are read straight down as printed."""
        if not lines:
            return []
        gutter = self._counsel_gutter(lines)
        if gutter is None:
            return self._counsel_single_column(lines)
        entries, label, body = [], [], []

        def flush():
            head = " ".join(label).strip().rstrip(":").strip()
            tail = " ".join(body).strip()
            if head or tail:
                entries.append(f"{head}: {tail}" if head and tail else head or tail)

        for line in lines:
            left, right = self._cut_at(line, gutter)
            if left and self._counsel_label(left):
                flush()
                label, body = [], []
            if left:
                label.append(left)
            if right:
                body.append(right)
        flush()
        return entries

    def _counsel_single_column(self, lines):
        """Counsel read straight down, a new entry at each party label."""
        entries = []
        for line in lines:
            text = " ".join(self.line_plain_text(line).split()).strip()
            if not text:
                continue
            if self._counsel_label(text) or not entries:
                entries.append(text)
            else:
                entries[-1] = f"{entries[-1]} {text}"
        return entries

    def _counsel_gutter(self, lines):
        """The x of the gutter running through the counsel block, or None.

        A gutter is a vertical band every row steps across at the same place,
        and a row attests to it in one of TWO ways: it either leaps the gutter
        with a gap wider than any word space, or — once the label column has run
        out of words — it simply BEGINS at the far side. Counting only the leaps
        found the gutter on 6 of Soussis's 21 rows and rejected it; the other 13
        rows start on the gutter and are the same evidence.

        Accepted only when a quarter of the rows agree, so a single-column block
        (which most records use) yields None and is read straight down."""
        rail = min(line.get("x0", 0) for line in lines)
        votes = Counter()
        seen = {}
        for line in lines:
            candidates = list(self._wide_gaps(line))
            x0 = line.get("x0", 0)
            if x0 > rail + 20:
                candidates.append(x0)
            for x in candidates:
                bucket = round(x / 4) * 4
                votes[bucket] += 1
                seen.setdefault(bucket, []).append(x)
        if not votes:
            return None
        bucket, hits = votes.most_common(1)[0]
        if hits < max(2, len(lines) // 4):
            return None
        # The bucket only gathers the votes; the CUT has to fall on the column's
        # true left edge. Using the rounded bucket put the boundary 1.4pt inside
        # the first glyph, so every row lost its opening letter to the label
        # ('For Debtor-Appellant Julia F. J' / 'effrey L. Herzberg').
        return min(seen[bucket]) - 0.5

    @staticmethod
    def _wide_gaps(line, min_gap=8.0):
        """The x where each wide intra-line gap ends — candidate column starts."""
        chars = [c for c in (line.get("chars") or ()) if (c.get("text") or "").strip()]
        chars.sort(key=lambda char: char.get("x0", 0))
        out = []
        for prev, nxt in zip(chars, chars[1:]):
            if nxt.get("x0", 0) - prev.get("x1", 0) >= min_gap:
                out.append(nxt.get("x0", 0))
        return out

    def _cut_at(self, line, boundary):
        """(left_of_boundary, right_of_boundary) for one row's text."""
        left, right = [], []
        for char in line.get("chars") or ():
            (left if char.get("x0", 0) < boundary else right).append(char)
        return (
            " ".join(self.line_plain_text({"chars": left}).split()).strip(),
            " ".join(self.line_plain_text({"chars": right}).split()).strip(),
        )

    # ---------------------------------------------------- engraved ladder
    def _read_engraved_ladder(self):
        """Dissect a published-opinion headmatter — the 'engraved ladder'.

        Four short drawn rules, centered on the page axis, rung the page into
        zones, and everything between them is CENTERED:

            24-1510                              running head
            Adidas America, Inc. v. Thom …        …and its short case name
            United States Court of Appeals        engraved masthead
            for the Second Circuit
            ─────────────────                    rule 1
            August Term 2025                     the term…
            Argued: October 28, 2025              …and the sitting dates
            Decided: April 29, 2026
            No. 24-1510                          the docket
            ─────────────────                    rule 2
            ADIDAS AMERICA, INC., ADIDAS AG,      caption: parties at 10.6pt
                Plaintiffs-Appellants,            …statuses italic at 13pt
            v.                                   …the hinge
            THOM BROWNE, INC.,
                Defendant-Appellee.
            ─────────────────                    rule 3
            On Appeal from the United States …    the origin: court…
            for the Southern District of New York
            No. 21-cv-5615                        …its docket…
            Jed S. Rakoff, Judge.                 …and the trial judge
            ─────────────────                    rule 4
            Before: CABRANES, PARK, and ROBINSON, Circuit Judges.
            <the court's own case summary>        left, wrapping to page 2
            ADAM H. CHARNES, Kilpatrick …         counsel, indented to 180

        The ladder is the style's LOOK, not its spine — the group draws its
        rules at four different widths, one record draws the same rule twice
        0.9pt apart, one has its footnote separator caught among them, two draw
        none at all, and one puts its term block above the first rule. Counting
        rungs therefore mis-zoned six of nine records (the term block landed in
        the caption). So the sections are found by their own LANDMARKS, in the
        fixed order the style prints them, with geometry — italic, size, rail —
        settling what a landmark cannot."""
        lines = self._hm_lines()
        if not lines:
            return None
        crit = {}
        banner, panel, counsel, statuses = [], [], [], []
        origin, summary = [], []
        case = {
            "docket": None,
            "caption": [],
            "prior_history": None,
            "sides": ([], []),
            "side": 0,
        }
        # (x0, row) for every caption row, so the caption can be reproduced with
        # the indentation the court printed it at — the status labels and the
        # hinge are set well in from the party names, and that offset is part of
        # how the caption reads.
        rows = []
        state = "head"
        counsel_open = False

        for index, line in enumerate(lines):
            text = " ".join(self.line_plain_text(line).split()).strip()
            if not text:
                continue
            if self._is_underscore_rule(text):
                # A typed rule CLOSES the section it ends. Numbered paper rules
                # its caption top and bottom, and rules the origin off from the
                # dates below it — without closing here the caption (or the
                # origin) stayed open and collected everything that followed:
                # schneiderman's prior history ran on into 'ARGUED: MAY 5, 2025
                # DECIDED: APRIL 6, 2026'.
                if state == "caption" and case["caption"]:
                    state = "tail"
                elif state == "origin" and origin:
                    state = "tail"
                continue
            x0 = line.get("x0", 0)
            italic = self._line_all_italic(line)
            low = text.lower()
            # Classify on the plain text, store the marked-up text — the
            # caption's inline emphasis is part of what it says.
            rich = " ".join(self.paragraph_text([line]).split()).strip()

            # ---- landmarks that move the walk on, wherever they appear ----
            if index == 0 and self._running_head_docket(text):
                crit["head_docket"] = self._running_head_docket(text)
                continue
            if index == 1 and crit.get("head_docket"):
                crit["short_case_name"] = text
                continue
            # The masthead is identified by its FACE, not its wording. It is set
            # in the engraved Old English the style is named for, and it runs to
            # three lines as often as two ('In the' / 'United States Court of
            # Appeals' / 'for the Second Circuit'). Testing the wording left 'In
            # the' unrecognised, and that one stray line dropped the walk into
            # the caption, which then swallowed the term, the dates, the docket
            # and the origin (russell came back with no docket and a case name
            # made of the masthead).
            if state == "head" and (
                self._line_is_masthead(line) or self._is_court_banner(text)
            ):
                banner.append(text)
                continue
            if state in ("head", "front") and self._is_term_row(low):
                crit["term"] = text
                state = "front"
                continue
            # The sitting dates may share one row, and that row may be
            # parenthesised ('(Argued: May 16, 2024 Decided: March 12, 2026)').
            # The shared splitter finds every label on the row and reads each to
            # the next, which a single split on the first colon cannot.
            # Tested in ANY state, because the dates do not always sit above the
            # caption: barrett prints them BELOW the origin ('__________' / 'On
            # Appeal from the United States District Court …' / '__________' /
            # 'ARGUED: SEPTEMBER 11, 2023' / 'DECIDED: APRIL 9, 2026'). Gated to
            # the front, they fell through to the tail, where an ALL-CAPS row
            # reads as a counsel entry — so the dates opened the counsel block
            # and the summary and the real counsel were appended to it.
            # A labelled date is unmistakable on its own: a known label, a colon
            # and a date, on a short row.
            dates = self._split_labelled_dates(text)
            if dates:
                for key, value in dates.items():
                    crit[f"date_{key}"] = value
                if state in ("head", "front"):
                    state = "front"
                continue
            # The APPELLATE docket stands alone before the caption; the district
            # court's own docket looks the same but comes after the origin
            # opener, so the state — not the shape — tells them apart.
            if state in ("head", "front") and self._is_bare_docket(text):
                case["docket"] = self._docket_label(text)
                state = "front"
                continue
            # THE ORIGIN IS STATED ONCE, AND ABOVE THE PANEL. The court's own
            # summary opens with the very same words ('Appeal from a judgment of
            # the United States District Court for the Northern District of New
            # York (Hurd, J.), convicting defendant-appellant of …'), so testing
            # the wording alone re-opened the origin after the roster and swept
            # the summary AND the counsel block into the prior history.
            # The bound is the PANEL, not the tail. pence's summary repeats the
            # origin's words below the roster, so the origin must not re-open
            # there — but barrett and schneiderman legitimately state the origin
            # after the caption's closing rule, which is already the tail. What
            # separates them is the roster: everything the court says about where
            # the case came from is printed above it.
            if not origin and not panel and self._is_origin_opener(low):
                state = "origin"
                origin.append(text)
                continue
            # The panel label may be LETTER-SPACED for emphasis ('B e f o r e:'),
            # which no prefix test on the printed text can match — so the spaces
            # come out before it is compared. Left unmatched, the whole roster
            # was read as the caption's last party.
            if "".join(low.split()).startswith("before") and (
                "judge" in low or ":" in text
            ):
                crit["panel_line"] = text
                roster = text.split(":", 1)[1].strip() if ":" in text else text
                panel.extend(self._roster_names(roster))
                # The roster is not necessarily finished on this line. It can be
                # absent altogether ('Before:' / 'JACOBS, CABRANES, and LOHIER,
                # Circuit Judges.'), or wrap mid-title ('… and RAGGI and PARK,
                # Circuit' / 'Judges.'), or continue into a DESIGNATED district
                # judge ('… Circuit Judges, and' / 'MATSUMOTO, District
                # Judge.*'). So it stays open until a bench title closes it —
                # otherwise the remainder was read as the summary's first line.
                state = "tail" if self._roster_closed(text) else "panel"
                continue

            if state == "panel":
                crit["panel_line"] = f"{crit['panel_line']} {text}".strip()
                panel.extend(self._roster_names(text))
                if self._roster_closed(text):
                    state = "tail"
                continue

            if state == "origin":
                origin.append(text)
                continue

            # NOTHING ABOVE THE MASTHEAD IS CAPTION. The running head sits up
            # there, and when its docket line is dropped as furniture the italic
            # case name beside it is the first row the reader sees — read as a
            # party, it opened the caption before the masthead and swallowed the
            # term, the dates and the docket into the first party's name.
            if state == "head" and not banner:
                if not crit.get("short_case_name"):
                    crit["short_case_name"] = text
                continue
            # The caption opens on POSITIVE evidence — a party name in caps or an
            # italic status label. Falling into it on any unrecognised line meant
            # one stray row above the caption (a masthead fragment, a
            # parenthesised date line) captured the whole rest of the headmatter.
            if state in ("head", "front"):
                # A party row need not be caps THROUGHOUT — the name is, but the
                # descriptor that follows it is not ('ARTHUR PROVENCHER,
                # individually and on behalf of all similarly situated
                # individuals,'). Requiring the whole row skipped every appellant
                # in provencher, so the caption only opened at the italic status
                # row below the hinge and the case name lost its left side.
                if not (italic or self._is_caps(text) or self._opens_caps(text)):
                    continue
                state = "caption"

            if state == "caption":
                # The hinge is set as bare 'v.' on most records but dressed in
                # em dashes on others ('— v. —'), so the rules are stripped off
                # before the row is read.
                # The hinge is 'v.' on most records, dressed in em dashes on
                # others ('— v. —'), and spelled out on the rest ('- against -').
                bare = text.strip().strip("—–-").strip().rstrip(".").strip().lower()
                if bare in ("v", "vs", "against", "versus"):
                    # The hinge is KEPT in the caption. ``case_name`` is a
                    # synthesised short form, but ``caption`` is the caption as
                    # printed, and consuming the hinge lost the word the court
                    # actually used ('- against -') along with the break it makes
                    # between the two sides.
                    case["caption"].append(rich)
                    rows.append((line.get("top", 0), rich))
                    case["side"] = 1
                    continue
                if italic:
                    statuses.append(rich)
                    case["caption"].append(rich)
                    rows.append((line.get("top", 0), rich))
                    continue
                side = case["sides"][case["side"]]
                if case["caption"] and not self._closes_party(case["caption"][-1]):
                    case["caption"][-1] = f"{case['caption'][-1]} {rich}"
                    if side:
                        side[-1] = f"{side[-1]} {rich}"
                    else:
                        side.append(rich)
                    # A wrapped party keeps the indent of the row that OPENED it.
                    if rows:
                        rows[-1] = (line.get("top", 0), f"{rows[-1][1]} {rich}")
                    else:
                        rows.append((line.get("top", 0), rich))
                else:
                    case["caption"].append(rich)
                    side.append(rich)
                    rows.append((line.get("top", 0), rich))
                continue

            # ---- past the panel: the court's summary, then counsel ----
            # Counsel is set INDENTED past the body rail, and how far varies by
            # record — adidas 180, goklu 144, against a body at 108. A fixed
            # threshold missed goklu's block entirely and left the whole thing in
            # the summary, so the indent is measured off the document's own rail.
            # The kind test still has to agree: the summary's paragraph first
            # lines are indented that far too, and are told apart by the ALL-CAPS
            # lead attorney a counsel entry opens with.
            counsel_indent = self.body_baseline_x0 + 20
            if counsel_open or (
                x0 >= counsel_indent and self._tail_kind(text) == "counsel"
            ):
                if not counsel_open or self._tail_kind(text) == "counsel":
                    counsel.append(text)
                else:
                    counsel[-1] = f"{counsel[-1]} {text}"
                counsel_open = True
                continue
            summary.append(text)

        if banner:
            crit["court"] = " ".join(banner)
        if panel:
            crit["panel"] = panel
        if origin:
            self._claim_origin(case, origin)
        name = self._case_name(case)
        if name:
            case["case_name"] = name
        # The ladder sets its caption CENTERED; numbered paper sets the same
        # sections flush left. The style knows which, so it says so.
        block = self._caption_block(rows)
        if block:
            case["caption_text"] = block
        del case["sides"], case["side"]
        if case["caption"] or case["docket"]:
            crit["cases"] = [case]
        if summary:
            crit["summary"] = " ".join(summary)
        if counsel:
            crit["counsel"] = "\n\n".join(counsel)
        if statuses:
            crit["party_status"] = statuses
        return crit or None

    @staticmethod
    def _roster_closed(text) -> bool:
        """True when this row ENDS the panel roster.

        The roster closes on the bench title that names the office, terminated by
        a period — which a footnote mark may follow ('District Judge.*')."""
        bare = text.rstrip().rstrip("*†‡∗0123456789").rstrip()
        return "judge" in text.lower() and bare.endswith(".")

    def _roster_names(self, roster):
        """The judges named in a 'Before: …, Circuit Judges.' roster.

        The shared splitter returns the roster's connectives and bench words
        alongside the names ('LIVINGSTON', 'RAGGI', 'PARK', 'Circuit'), so the
        panel came back with a judge called Circuit and another called and."""
        out = []
        candidates = []
        for name in self._panel_names(roster):
            # Two judges may be joined by 'and' inside one candidate ('LEVAL AND
            # BIANCO'), which came back as a single judge of that name.
            parts = name.replace(" AND ", "|").replace(" and ", "|").split("|")
            candidates.extend(parts)
        for name in candidates:
            bare = name.strip().rstrip(",.").strip().rstrip("*†‡∗").strip(" .,")
            if not bare:
                continue
            words = [w.strip(" .,").lower() for w in bare.split()]
            # A bench TITLE is not a judge, whether it arrives alone ('Circuit')
            # or as the whole phrase ('District Judge.†' — a designated judge's
            # title, which came back as a panel member of its own).
            if any(word in _BENCH_WORDS for word in words):
                continue
            if words and words[0] in ("and", "&", "circuit", "district", "senior"):
                continue
            out.append(bare)
        return out

    @classmethod
    def _opens_with_footnote_mark(cls, text) -> bool:
        """A row that opens with a caption footnote's reference mark.

        Stars and daggers only: '§' and '¶' open ordinary statutory prose."""
        head = text.lstrip()
        if not head or head[0] not in cls._CAPTION_MARKS:
            return False
        # A marker stands apart from the note's first word; a party name opening
        # with a symbol would not.
        return len(head) > 1 and head[1] in " \t"

    @staticmethod
    def _line_is_engraved(line) -> bool:
        """Set in the engraved masthead face."""
        return any(
            "OldEnglish" in (char.get("fontname") or "")
            for char in line.get("chars") or ()
        )

    # The masthead is set at DISPLAY size — well above the 13pt body — whether or
    # not it is engraved. Reading it by size rather than by face catches the
    # fragment that carries no court name of its own ('In the'), which otherwise
    # went unrecognised and, before the head guard, derailed the whole walk.
    masthead_min_size = 16.0

    def _line_is_masthead(self, line) -> bool:
        if self._line_is_engraved(line):
            return True
        size, _, _ = self.line_meta(line)
        return bool(size) and size >= self.masthead_min_size

    @staticmethod
    def _is_term_row(low) -> bool:
        """'August Term 2025' / 'September Term, 2024' — the sitting term."""
        return "term" in low and any(
            token.strip(",.").isdigit() and len(token.strip(",.")) == 4
            for token in low.split()
        )


    # The role a consolidated appeal's docket carries: lead, consolidated,
    # cross-appeal, or amicus.
    _DOCKET_TAGS = ("L", "C", "CON", "XAP", "AP", "X", "CV", "PR")

    def _consolidated_docket(self, text):
        """'23-263 (CON)' if the row is nothing but dockets and role tags."""
        tokens = text.replace(";", " ").split()
        if not tokens:
            return ""
        seen = False
        for token in tokens:
            bare = token.strip("();,")
            if self._is_docket_token(token) or self._is_docket_token(bare):
                seen = True
                continue
            if bare.upper() in self._DOCKET_TAGS:
                continue
            return ""
        return " ".join(tokens).strip(" ;,") if seen else ""

    @staticmethod
    def _docket_label(text) -> str:
        """The docket under ONE label. CA2 writes 'No. 24-1510' on one record and
        'Docket No. 25-487-cv' on the next; prefixing 'No.' blindly produced
        'No. Docket No. 25-487-cv'."""
        bare = text.strip()
        if bare.lower().startswith("docket "):
            bare = bare[7:].strip()
        # 'Nos.' as well as 'No.' — a consolidated appeal pluralises the label,
        # and prefixing produced 'No. Nos. 21-2737(L), 24-274(CON)'.
        return bare if bare.lower().startswith(("no.", "nos.")) else f"No. {bare}"

    def _is_bare_docket(self, text) -> bool:
        """A docket standing alone on its own row ('No. 24-1510').

        The label varies — 'No. 24-1510', 'Docket No. 25-487-cv', or the bare
        number — so it is stripped before the tokens are tested."""
        bare = text.strip()
        if bare.lower().startswith("docket "):
            bare = bare[7:].strip()
        for label in ("nos.", "no."):
            if bare.lower().startswith(label):
                bare = bare[len(label):].strip()
                break
        if not bare:
            return False
        # A CONSOLIDATED docket row lists several, each with its role tag
        # ('Docket Nos. 23-7370 (L), 23-7463 (XAP), 23-7614 (XAP)'), so it runs
        # well past the three tokens a single docket needs.
        if self._consolidated_docket(bare.replace(",", " ")):
            return True
        if len(bare.split()) > 3:
            return False
        return self._is_docket_text(bare) or all(
            self._is_docket_token(token) for token in bare.replace(";", " ").split()
        )

    @staticmethod
    def _is_origin_opener(low) -> bool:
        """The row that opens the origin statement."""
        return low.startswith(
            (
                "appeal from",
                "appeals from",
                "on appeal from",
                "cross-appeal from",
                "cross-appeals from",
                "petition for review",
                "petitions for review",
                "on petition for review",
                "on petitions for review",
                "appeal from a judgment",
                "on remand from",
                "review of",
            )
        )

    @staticmethod
    def _claim_origin(case, rows):
        """Split the origin zone into the court, its docket, and the judge.

        'On Appeal from the United States District Court / for the Southern
        District of New York / No. 21-cv-5615 / Jed S. Rakoff, Judge.' — the
        court's name wraps, then its own docket, then who tried it.

        The docket and the judge are not always on rows of their own — the group
        packs both onto one ('No. 23-cv-2583, Lewis J. Liman, Judge.') or breaks
        the judge's title onto the next ('No. 20-cv-184, Geoffrey W. Crawford,' /
        'District Judge.'). So a docket row is cut at its first comma and
        whatever follows joins the judge, and a row that is nothing but a bench
        title attaches to the judge above it."""
        court, docket, judge = [], None, []
        for row in rows:
            low = row.lower()
            if low.startswith("no.") or "-cv-" in low or "-cr-" in low or "-md-" in low:
                head, sep, tail = row.partition(",")
                docket = head.strip() if sep else row.strip()
                if tail.strip():
                    judge.append(tail.strip())
                continue
            bare = low.rstrip(".").strip()
            if bare in ("judge", "district judge", "chief judge", "senior judge",
                        "chief district judge", "senior district judge", "j",
                        "magistrate judge", "bankruptcy judge"):
                judge.append(row)
                continue
            if bare.endswith(("judge", "judges", "j")):
                judge.append(row)
                continue
            court.append(row)
        if court:
            case["prior_history"] = " ".join(court)
            case["lower_court"] = " ".join(court)
        if docket:
            case["lower_docket"] = docket
        if judge:
            case["lower_judge"] = " ".join(judge)

    @staticmethod
    def _case_name(case):
        """The case name, built from the party names either side of 'v.'.

        Reads off the caption's own hinge rather than joining every row: the
        rows include the italic status labels, so a wholesale join produces
        'AMANDA BROOKS, Plaintiff-Appellant, BRIGHT HORIZONS …' instead of a
        name."""
        left, right = case.get("sides", ([], []))
        joined = [" ".join(side).strip().rstrip(",").strip() for side in (left, right)]
        left_name, right_name = joined
        if left_name and right_name:
            return f"{left_name} v. {right_name}"
        return left_name or right_name or ""

    def _caption_rail(self, lines):
        """The left rail of the caption band — the column the party names hold.

        The band opens at the first typed rule and closes at the next. Within it
        the italic status labels and the centered versus row are indented off the
        rail, so the rail is the minimum x0 among the rows that are neither."""
        band, seen_rule = [], False
        for line in lines:
            text = " ".join(self.line_plain_text(line).split()).strip()
            if self._is_underscore_rule(text):
                if seen_rule:
                    break
                seen_rule = True
                continue
            if not seen_rule or not text:
                continue
            if self._line_all_italic(line):
                continue
            first = text.split()[0].rstrip(".").lower()
            if first in ("v", "vs"):
                continue
            band.append(line.get("x0", 0))
        if band:
            return min(band)
        return min((line.get("x0", 0) for line in lines), default=0)

    @staticmethod
    def _merge_in_re(cases):
        """Fold an 'IN RE:' heading into the appeal caption beneath it.

        A bankruptcy appeal is ruled into TWO caption blocks — the estate the
        case is brought in ('IN RE: JULIA F. SOUSSIS,' / 'Debtor.') and then the
        appeal itself ('JULIA F. SOUSSIS,' / 'Debtor-Appellant,' / 'v. 25-1561' /
        the trustees). They are one case, not two: the heading carries no docket
        of its own and names the same debtor."""
        out = []
        for case in cases:
            first = (case["caption"][0] if case["caption"] else "").upper()
            heading = first.startswith(("IN RE", "IN THE MATTER OF"))
            if heading and not case["docket"] and case is not cases[-1]:
                out.append(case)
                continue
            if out and not out[-1]["docket"]:
                prior = out.pop()
                head = (prior["caption"][0] if prior["caption"] else "").upper()
                if head.startswith(("IN RE", "IN THE MATTER OF")):
                    # The heading joins the caption ROWS (it is printed there)
                    # but not the name sides: the debtor is already named on the
                    # appellant side, so folding it in would read 'IN RE: JULIA
                    # F. SOUSSIS, JULIA F. SOUSSIS v. …'.
                    case["caption"] = prior["caption"] + case["caption"]
                    case["rows"] = prior["rows"] + case["rows"]
                else:
                    out.append(prior)
            out.append(case)
        return out

    # The party a counsel entry acts for. Used to recognise the label that opens
    # the entry — CA2 sets that label in its own narrow COLUMN beside the
    # attorney text, and pdfplumber merges the two columns onto one line, so the
    # colon that closes the label can land on the next physical line:
    #
    #   'For Debtor-Appellant Julia F.   Jeffrey L. Herzberg, Jeffrey'
    #   'Soussis:                        Herzberg, PC, Hauppauge, NY.'
    #
    # Requiring the colon therefore missed the entry entirely, and the whole
    # counsel block was read as a third case in the caption.
    _PARTY_ROLES = (
        "appellant", "appellee", "petitioner", "respondent", "debtor",
        "trustee", "plaintiff", "defendant", "amicus", "amici", "intervenor",
        "appellants", "appellees", "petitioners", "respondents", "creditor",
        "movant", "cross-appellant", "cross-appellee",
    )

    @classmethod
    def _counsel_label(cls, text) -> bool:
        """'For Plaintiff-Appellant:' — a counsel entry announces its party."""
        head = text.strip()
        if head[:4].lower() != "for ":
            return False
        if ":" in head[:60]:
            return True
        low = head[:90].lower()
        return any(role in low for role in cls._PARTY_ROLES)

    def _versus_docket(self, line, text, rail):
        """The docket off a centered versus row ('v. 25-1830-cv'), or None.

        Returns '' when the row is a bare 'v.' with no docket beside it (the
        centered captions stack the two), so the caller still knows the row was
        the versus row and not a party."""
        bare = text.rstrip(".").strip()
        if bare.lower() in ("v", "vs", "-v-", "- v. -", "- v -"):
            return ""
        first = text.split()[0].rstrip(".").lower() if text.split() else ""
        if first not in ("v", "vs"):
            return None
        if line.get("x0", 0) <= rail + 6:
            return None
        tail = text.split(None, 1)[1].strip() if len(text.split(None, 1)) > 1 else ""
        if not tail:
            return ""
        # The versus row may already carry the 'No.' ('v. No. 25-2417-cv').
        return tail if tail.lower().startswith("no.") else f"No. {tail}"

    @classmethod
    def _closes_party(cls, text) -> bool:
        """True when a caption row ends a party name rather than wrapping.

        Tested on the row's TEXT, with any inline markup taken off first: the
        caption rows are stored marked up, so a status label arrives as
        '<em>Defendant-Appellant-Cross-Appellee,</em>' and ends — as far as a
        punctuation test is concerned — in '>'. Every italic row therefore read
        as unfinished and swallowed the row beneath it.

        A HINGE row closes too: it separates the sides, so what follows it starts
        a new party rather than continuing 'against'."""
        plain = cls._strip_tags(text)
        if cls._is_hinge(plain):
            return True
        head = plain.split(None, 1)[0] if plain.split() else ""
        if cls._is_hinge(head):
            return True
        return plain.endswith((",", ".", ";"))

    @staticmethod
    def _caption_block(rows) -> str:
        """The caption as PRINTED — one row per line, its real breaks kept.

        A caption is not a sentence and not a flat list. Its rows come out in
        document order, each on its own line, and where the page leaves a gap
        materially wider than the caption's own row pitch a BLANK line is
        emitted: that gap is how a consolidated record separates one case's
        parties from the next (petersen stacks two, with nothing drawn between
        them but space). No indentation is invented — the rows are set flush, so
        the separator is the only thing the whitespace has to say.

        ``case_name`` remains the synthesised short form beside it."""
        if not rows:
            return ""
        gaps = sorted(b - a for (a, _x), (b, _y) in zip(rows, rows[1:]))
        pitch = gaps[len(gaps) // 2] if gaps else 0
        out = [rows[0][1]]
        for (prev_top, _prev), (top, row) in zip(rows, rows[1:]):
            if pitch and (top - prev_top) > pitch * 1.3:
                out.append("")
            out.append(row)
        return "\n".join(out)

    @staticmethod
    def _strip_tags(text) -> str:
        """``text`` with inline markup removed (no regex — see CLAUDE.md)."""
        out, depth = [], 0
        for char in text:
            if char == "<":
                depth += 1
            elif char == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(char)
        return "".join(out).strip()

    @staticmethod
    def _is_hinge(text) -> bool:
        """The caption's versus row, however the court sets it."""
        bare = text.strip().strip("—–-").strip().rstrip(".").strip().lower()
        return bare in ("v", "vs", "against", "versus")

    def _origin_row(self, text):
        """CA2 stacks the tribunal being reviewed above its own banner:

            BIA                  <- the Board of Immigration Appeals
            Straus, IJ           <- the immigration judge
            A209 866 562/563     <- the alien registration number

        A summary order prints no 'On Appeal from' line at all, so this block
        is the ONLY statement of where the case came from."""
        bare = " ".join(text.split())
        if len(bare) > 40:
            return None
        if bare in ("BIA", "NAC", "AC"):
            return ("lower_court", bare)
        if bare.endswith(", IJ") or bare.endswith(" IJ"):
            return ("lower_judge", bare)
        head = bare.split()
        if head and head[0].startswith("A") and head[0][1:].isdigit():
            return ("lower_docket", bare)
        return None

    def _running_head_docket(self, text):
        """CA2 heads page 1 with '<docket> <short case name>' — '24-301
        Alvarenga Vides v. Blanche', '25-2417-cv Alsonidar v. Mullin',
        '23-258 (L); 23-354 (L) Havlish v. Taliban'. On a summary order that
        head is the only complete statement of the docket, so it is read
        rather than discarded with the rest of the furniture. Consolidated
        appeals list every docket, each optionally tagged '(L)' for lead."""
        taken = []
        for token in text.split():
            bare = token.strip("();,")
            if self._is_docket_token(token) or bare in ("L", "XAP", "CON", "AP"):
                taken.append(token)
                continue
            if taken and token.endswith(";"):
                taken.append(token)
                continue
            break
        joined = " ".join(taken).strip(" ;,")
        return f"No. {joined}" if joined else None

    def _tail_kind(self, text):
        """CA2 prints a CASE SUMMARY between the roster and the appearances,
        so the two have to be told apart. An appearance announces itself: the
        attorney's name is set in caps ('ADAM H. CHARNES, Kilpatrick Townsend
        ...'), or the block is headed by the party it acts for ('FOR
        PETITIONERS:'). Everything else there is the summary."""
        body = text.strip()
        if body.upper().startswith("FOR ") and ":" in body[:48]:
            return "counsel"
        run = []
        for token in body.replace(",", " ").split():
            letters = [c for c in token if c.isalpha()]
            if letters and all(c.isupper() for c in letters):
                run.append(token)
            else:
                break
        return "counsel" if len(run) >= 2 else "summary"
    criteria_lift_publication = True
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0

    footnote_font_size = 12
    opinion_font_size_= 13
    # pagenum_font_size = 12 or 13
    foonote_divider_width = 144.0
    footnote_divider_style = "rect"
    # footnote_divider_x0 = 108.0,  86.4
    
    # Full opinion, foonotes size 12, 144 width,  108 x0 page number size 12 font PalatinoLinotype-Roman



    # Summary Order #1 
    #      H   top= 698.1 x0=  72.0 x1= 216.0 bot= 698.8 w= 144.0 h=  0.7 (24% pw, top 88%)
    #   x top= 729.1 x0= 302.8 x1= 309.3 sz=13.0 C   PalatinoLinotype-Roman   | 2
#     top= 707.9 x0=  72.0 x1= 449.7 sz=12.0 L   PalatinoLinotype-Roman   | * The Clerk of Court is directed to amend the caption as set forth above.

    # PalatinoLinotype-Roman or TimesNewRomanPSMT

    # Summary order 2 with page lines alvarenga_vides_v._blanche



    # CA2 documents come in distinct STYLES, and each style dictates its own
    # extraction. Two independent axes:
    #   * summary-order vs opinion — a summary order opens with the convening
    #     recital ('At a stated term of the United States Court of Appeals …')
    #     under a centered 'SUMMARY ORDER' heading and a 'PRESENT: <judges>'
    #     panel; an opinion has a normal '<NAME>, Circuit Judge:' byline.
    #   * numbered paper or not — a left-margin line-number gutter.
    # ``document_style`` reports one of: 'opinion', 'opinion_numbered',
    # 'summary_order', 'summary_order_numbered'.
    def document_style(self, page) -> str:
        text = (page.extract_text() or "").lower()
        is_summary = "at a stated term" in text or (
            "summary order" in text and "rulings by summary order" in text
        )
        base = "summary_order" if is_summary else "opinion"
        numbered = self._linenum_gutter_x(page) is not None
        return base + ("_numbered" if numbered else "")

    def extract(self, pdf_path):
        """Detect the document style up front so the style-specific hooks below
        (per-curiam start for summary orders) can branch on it."""
        self._style = "opinion"
        self._engraved = False
        self._hm_rules = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.pages:
                    self._style = self.document_style(pdf.pages[0])
                    # The engraved masthead is set in Old English — the one
                    # face CA2 uses nowhere else, and the signature of the
                    # published-opinion 'engraved ladder' headmatter style.
                    self._engraved = any(
                        "OldEnglish" in (char.get("fontname") or "")
                        for char in pdf.pages[0].chars
                    )
        except Exception:
            pass
        self._measure_body_template(pdf_path)
        return super().extract(pdf_path)

    def _measure_body_template(self, pdf_path):
        """Measure CA2's varying body rail and double-space leading."""
        x0s = Counter()
        page_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    lines = self.page_lines(page)
                    usable = [
                        line
                        for line in lines
                        if 75 < line.get("top", 0) < page.height - 75
                        and line.get("x0", 0) < page.width * 0.42
                        and line.get("x1", 0) > page.width * 0.55
                    ]
                    x0s.update(round(line["x0"]) for line in usable)
                    page_rows.append(usable)
        except Exception:
            return
        if not x0s:
            return
        baseline = float(x0s.most_common(1)[0][0])
        gaps = Counter()
        for lines in page_rows:
            ordered = sorted(lines, key=lambda line: line["top"])
            for above, below in zip(ordered, ordered[1:]):
                gap = below["top"] - above["top"]
                if (
                    abs(above["x0"] - baseline) <= 4
                    and abs(below["x0"] - baseline) <= 4
                    and 14 <= gap <= 42
                ):
                    gaps[round(gap, 1)] += 1
        self.body_baseline_x0 = baseline
        if gaps:
            leading = gaps.most_common(1)[0][0]
            self.gap_single_max = max(self.gap_tight_max + 1, leading - 7)
            self.gap_double_max = leading + 8

    # A stapled CA2 decision does not set every writing to the same measure. In
    # an en banc denial the clerk's order is SINGLE-spaced (17.5pt leading,
    # 35pt between paragraphs) while each separate writing that follows is
    # DOUBLE-spaced (35pt leading) — so one document-wide gap band cannot serve
    # both: 35pt means 'new paragraph' in the order and 'same paragraph' in the
    # dissent. Reading the document's single modal lead made every line of the
    # double-spaced writings its own paragraph (Sullivan's dissent came back as
    # 222 one-line blocks). Leading is therefore measured PER PAGE, which is
    # the unit a writing actually changes on — each begins on a fresh page.
    #
    # Page 1 keeps the document bands: a caption's rows are spaced like body
    # leading, so a page-local band there merges the whole caption into one row.
    def segment_lines(self, lines, page_width) -> list:
        lead = self._page_lead(lines) if self._page_number(lines) > 1 else None
        if not lead:
            return super().segment_lines(lines, page_width)
        geom = getattr(self, "_doc_geom", None)
        saved = (self.gap_single_max, self.gap_double_max)
        saved_lead = geom.get("lead") if geom else None
        self.gap_single_max = max(self.gap_tight_max + 1, lead - 7)
        self.gap_double_max = lead + 8
        if geom is not None:
            geom["lead"] = lead
        try:
            return super().segment_lines(lines, page_width)
        finally:
            self.gap_single_max, self.gap_double_max = saved
            if geom is not None:
                geom["lead"] = saved_lead

    @staticmethod
    def _page_number(lines) -> int:
        for line in lines:
            pno = line.get("page_number")
            if pno is None:
                for char in line.get("chars") or ():
                    pno = char.get("page_number")
                    break
            if pno:
                return pno
        return 1

    def _page_lead(self, lines):
        """This page's own BODY leading, or None if not well determined.

        Measured between vertically consecutive lines that share the page's
        LEFTMOST rail — a wrapped continuation returns to that rail, so those
        gaps are the body's true leading. Two things make the restriction
        necessary, and a plain page-wide mode gets both wrong:

        * A MIXED page. waldman page 7 carries the single-spaced amici counsel
          block (17.5pt, indented to x0=216) above the double-spaced opinion
          body (35pt at x0=72). The counsel lines outnumber the body lines, so
          the mode was 17.5 and every line of the opinion's first paragraph
          became its own paragraph — while page 8, which is pure body, read
          correctly. Counsel is indented; the body is not.

        * FOOTNOTES, which sit on the body rail but lead tighter than it and can
          outnumber the body lines on a page. So among the rail's gaps we take
          the LARGEST that recurs, not the commonest: body text is set no
          tighter than its own footnotes, and a paragraph's internal leading is
          what has to be recovered here.
        """
        rows = sorted(
            (line["top"], line.get("x0", 0))
            for line in lines
            if (line.get("text") or "").strip()
        )
        if not rows:
            return None
        rail = min(x0 for _top, x0 in rows)
        gaps = Counter()
        for (top_a, x0_a), (top_b, x0_b) in zip(rows, rows[1:]):
            gap = top_b - top_a
            if not 12 <= gap <= 60:
                continue
            if abs(x0_a - rail) > 2 or abs(x0_b - rail) > 2:
                continue
            gaps[round(gap * 2) / 2] += 1
        recurring = [lead for lead, hits in gaps.items() if hits >= 3]
        return max(recurring) if recurring else None

    def prepare_document(self, pdf):
        """Enable the continuation-page header filter only when present.

        Many Second Circuit opinions begin body text around y=76 on pages 2+
        and have no running docket header. The circuit base assumes the
        opposite and drops those lines. A repeated ``No.``/``Case No.`` line
        on continuation pages is the positive signal that the reservation is
        actually needed.
        """
        self._drop_page2_header = False
        self._ca2_notice_furniture = []
        headers = []
        for page in pdf.pages[1:]:
            for line in page.extract_text_lines():
                if line.get("top", 0) >= self.page2_header_cutoff:
                    break
                text = " ".join((line.get("text") or "").split()).lower()
                if text.startswith(("no. ", "case no. ", "docket no. ")):
                    headers.append(text)
                    break
        self._drop_page2_header = len(headers) >= 2 and len(set(headers)) == 1
        self._ca2_head_texts = self._learn_running_head(pdf)

    # CA2 heads every page with the docket over the short case name
    # ('23-258 (L); 23-354 (L)' / 'Havlish v. Taliban; Aliganga v. Taliban').
    # Neither position nor type size identifies it across the corpus: the band
    # sits anywhere from y=40 to y=98, and the head is 9pt against 12pt body in
    # one filing but 12pt against 13pt body in the next — and in a numbered
    # opinion it is the same 12pt as the body. What is invariant is REPETITION:
    # the same two strings head page after page. Learn them, then drop them as
    # furniture. Left in place they tacked the head onto the last paragraph of
    # every writing ('… recognize foreign governments. 23-258 (L); 23-354 (L)
    # Havlish v. Taliban …').
    def _learn_running_head(self, pdf):
        """The set of texts that head two or more pages."""
        seen = Counter()
        for page in pdf.pages:
            taken = 0
            for line in sorted(
                page.extract_text_lines(), key=lambda ln: ln.get("top", 0)
            ):
                text = " ".join((line.get("text") or "").split())
                if not text:
                    continue
                seen[text] += 1
                taken += 1
                if taken >= 2:
                    break
        return {text for text, hits in seen.items() if hits >= 2}

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        heads = getattr(self, "_ca2_head_texts", None)
        if not heads:
            return lines
        kept = []
        for index, line in enumerate(lines):
            text = " ".join((line.get("text") or "").split())
            # Only the head BAND — the opening rows of the page — can be the
            # running head; an identical string deeper in the page is content.
            if index < 2 and text in heads:
                self._record_dropped(text)
                continue
            kept.append(line)
        return kept

    def _sweep_residual(self, doc, source_pages):
        if getattr(self, "_ca2_notice_furniture", None):
            doc.dropped = list(doc.dropped) + self._ca2_notice_furniture
        super()._sweep_residual(doc, source_pages)

    def filter_margins(self, obj):
        if (
            obj.get("page_number", 1) > 1
            and obj.get("top", 0) < self.page2_header_cutoff
            and not getattr(self, "_drop_page2_header", False)
        ):
            return BaseExtractor.filter_margins(self, obj)
        return super().filter_margins(obj)

    # ------------------------------------------------------------- summary order
    def find_authors(self, all_segments) -> list:
        """A summary order is per curiam with NO byline of its own; force the
        body-opener locator rather than byline detection, which otherwise
        latches onto a false byline ('by the Court, …') and starts the opinion
        mid-text.

        But the per-curiam opener is not necessarily the ONLY writing. An en
        banc denial carries the same 'At a stated term' recital as a summary
        order, and its per-curiam order ('the petition for rehearing en banc is
        hereby DENIED') is followed by the separate writings it enumerates,
        each opening with a real byline of its own:

            NARDINI, Circuit Judge, joined by LOHIER, Circuit Judge,
                concurring in the denial of rehearing en banc:
            SULLIVAN, Circuit Judge, joined by LIVINGSTON, Chief Judge, …
            MENASHI, Circuit Judge, dissenting from the denial …
            JOSÉ A. CABRANES AND GUIDO CALABRESI, Circuit Judges:

        Returning only the per-curiam start swept all of them into one
        293-block 'majority', losing every author and kind. So the per-curiam
        opener anchors the FIRST writing and byline detection still runs over
        everything after it. Bylines above the opener stay ignored — that is
        where the panel roster and the trial judge live."""
        if not getattr(self, "_style", "").startswith("summary_order"):
            return super().find_authors(all_segments)
        self._pc_starts = set()
        start = self._summary_order_body_start(all_segments)
        starts = []
        if start is not None:
            self._pc_starts.add(start)
            starts.append(start)
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if not seg or (start is not None and i <= start):
                continue
            # The order ENUMERATES its separate writings in its own body
            # ('Steven J. Menashi, Circuit Judge, dissents by opinion from the
            # denial of rehearing en banc.'), and that sentence has the exact
            # form of a byline — name, bench title, kind. Read as one, it
            # opened a phantom writing and split the order in half.
            # The two are told apart by their TERMINATOR: a writing's byline
            # introduces the text that follows it and closes with a COLON
            # ('MENASHI, Circuit Judge, dissenting … en banc:'); the
            # enumeration is a finished sentence and closes with a period.
            split = self._byline_split(seg[0])
            if split is None or not split[0].rstrip().endswith(":"):
                continue
            starts.append(i)
        # Drop a byline with no body before the next one (the same guard the
        # circuit base applies): a bench name on a line of its own is not a
        # writing unless prose follows it.
        out = []
        for n, i in enumerate(starts):
            end = starts[n + 1] if n + 1 < len(starts) else len(all_segments)
            if i in self._pc_starts or self._opinion_has_body(all_segments, i, end):
                out.append(i)
        return out

    # A separate writing in an en banc denial is signed in a form the shared
    # byline grammar cannot read. Three things defeat it, often at once:
    #
    #   JOSÉ A. CABRANES AND GUIDO CALABRESI, Circuit Judges:
    #   MERRIAM and KAHN, Circuit Judges, writing jointly, joined by
    #       ROBINSON and PÉREZ, Circuit Judges, concurring …:
    #   CHIN, Senior Circuit Judge, in support of the denial of rehearing en banc:
    #
    # the title is PLURAL when two judges sign (which the grammar reads as a
    # 'Before …' panel roster and rejects); the signers are joined by 'and',
    # overrunning its five-token name budget; and the kind clause can name
    # further judges, so the title is not the last thing on the line.
    #
    # What every one of them does have is CA2's own invariant: a writing's
    # byline opens with the signers' surnames in CAPS and closes with a COLON
    # (the roster it would be confused with closes with a period, and CA2's
    # roster is headed 'Present:', never a name). Recognise that, and the
    # writings stop collapsing into the order above them.
    _BENCH_TITLES = ("Circuit Judge", "District Judge", "Chief Judge", "Judge")

    def _byline_split(self, line):
        split = super()._byline_split(line)
        if split is not None:
            return split
        text = (line.get("text") or "").strip()
        return (text, "") if self._signer_byline(text) else None

    def parse_author_line(self, text):
        """Parse a signers' byline the shared grammar cannot, and type it.

        The kind is read from the byline's own words. A writing that names no
        kind at all ('JOSÉ A. CABRANES AND GUIDO CALABRESI, Circuit Judges:')
        is the STATEMENT the order says it is — 'filed a statement with respect
        to the denial of rehearing en banc' — never the opinion of the court,
        which here is the per-curiam order."""
        parsed = super().parse_author_line(text)
        if parsed is not None:
            return parsed
        signers = self._signer_byline((text or "").strip())
        if not signers:
            return None
        low = text.lower()
        kind = "statement"
        for word in ("dissenting", "dissent", "concurring", "concur", "in support"):
            if word in low:
                kind = "dissent" if word.startswith("dissent") else (
                    "concurring" if word.startswith("concur") else "statement"
                )
                break
        return signers, "Circuit Judges", kind

    def _signer_byline(self, text):
        """The signers named at the head of a separate writing's byline, or ''.

        Requires CA2's two invariants — a CAPS surname head and a terminating
        colon — plus a bench title somewhere after the names, so an ordinary
        sentence ending in a colon can never qualify."""
        if not text.endswith(":") or "," not in text:
            return ""
        head, _, rest = text[:-1].partition(",")
        if not any(title in rest for title in self._BENCH_TITLES):
            return ""
        return head.strip() if self._caps_signers(head) else ""

    @staticmethod
    def _caps_signers(head) -> bool:
        """True if ``head`` is one or more CAPS surnames joined by 'and'.

        CAPS is the form CA2 reserves for the judge who SIGNS, as against the
        title-case names that appear inside a kind clause ('joined by Debra Ann
        Livingston, Chief Judge') — so it is what separates a byline from a
        sentence about one."""
        chunks = head.replace(" AND ", "|").replace(" and ", "|").split("|")
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk or not _is_name(chunk):
                return False
            letters = [c for c in chunk if c.isalpha()]
            if not letters or not all(c.isupper() for c in letters):
                return False
        return bool(chunks)

    # A signers' byline routinely runs past the measure and wraps — onto two
    # lines for a joint signature, three when the kind clause names the judges
    # who join it:
    #
    #   MENASHI, Circuit Judge, joined by PARK, Circuit Judge, and joined
    #   by LIVINGSTON, Chief Judge, except as to Part II.E.1, dissenting from
    #   the denial of rehearing en banc:
    #
    # The terminating colon then sits on the LAST line, so the byline never
    # parses and the whole writing folds into the order above it (carroll came
    # back as one 201-block per curiam). Fold forward until the colon closes the
    # byline — the accumulated text must itself parse as one, so prose can never
    # be swallowed.
    def _fold_writing_bylines(self, lines):
        out, index = [], 0
        while index < len(lines):
            line = lines[index]
            text = self.line_plain_text(line).strip()
            folded = None
            if not text.endswith(":") and "," in text:
                if self._caps_signers(text[: text.index(",")]):
                    folded = self._fold_from(lines, index, text)
            if folded is None:
                out.append(line)
                index += 1
                continue
            merged, consumed = folded
            out.append(merged)
            index = consumed
        return out

    def _fold_from(self, lines, index, text):
        """(merged_line, next_index) folding lines[index:] into one byline."""
        line = lines[index]
        chars = list(line.get("chars") or [])
        acc = text
        for j in range(index + 1, min(index + 4, len(lines))):
            nxt = lines[j]
            gap = nxt.get("top", 0) - lines[j - 1].get("top", 0)
            if not 0 < gap <= self.gap_double_max:
                return None
            if nxt.get("x0", 0) > line.get("x0", 0) + 40:
                return None
            if chars:
                space = dict(chars[-1])
                space["text"] = " "
                space["x0"] = space["x1"] = chars[-1].get("x1", 0)
                chars.append(space)
            chars += list(nxt.get("chars") or [])
            acc = f"{acc} {self.line_plain_text(nxt).strip()}"
            if acc.endswith(":"):
                if not self._signer_byline(acc):
                    return None
                merged = self._rebuild_line(line, chars)
                merged["text"] = acc
                return merged, j + 1
        return None

    def normalize_opinion_type(self, kind) -> str:
        """A writing filed 'in support of the denial of rehearing en banc' is a
        concurrence in that denial. Left unmapped it became its own type, colon
        and all ('in-support-of-the-denial-of-rehearing-en-banc:')."""
        if kind:
            k = kind.strip().rstrip(":").strip()
            if "in support of" in k.lower():
                return "concurrence"
            kind = k
        return super().normalize_opinion_type(kind)

    def _percuriam_start(self, all_segments):
        """A summary order is per curiam and has NO byline; its body opens after
        the counsel block (the panel/caption/counsel are all headmatter). The
        base looks for a 'Before … Judges.' roster, but a summary order's panel
        is 'PRESENT: …', so route summary orders to the counsel-block locator."""
        if getattr(self, "_style", "").startswith("summary_order"):
            return self._summary_order_body_start(all_segments)
        return super()._percuriam_start(all_segments)

    # The operative opener of a CA2 summary order's per-curiam body. Everything
    # before it (recital, SUMMARY ORDER heading, PRESENT panel, caption,
    # counsel) is headmatter. Uniform across counseled, pro-se, and consolidated
    # orders — unlike the counsel block, which is absent or unlabeled in some.
    _BODY_OPENERS = (
        "appeal from",
        "appeals from",
        "cross-appeal from",
        "petition for review",
        "petitions for review",
        "on appeal from",
        "on petition for review",
        "following disposition",
        "upon due consideration",
        "on consideration",
    )

    def _summary_order_body_start(self, all_segments):
        """Index of the first body segment of a summary order — the first
        segment opening with the order's operative language ('Appeal from a
        judgment …' / 'UPON DUE CONSIDERATION …')."""
        for j, (_pno, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip().lower()
            if any(t.startswith(o) for o in self._BODY_OPENERS):
                return j
        return None

    def skip_headmatter_segment(self, seg) -> bool:
        """Route CA2's standard summary-order advisory to ``dropped``.

        The advisory is printed as several left-aligned segments, not one
        notice block: the final ``COUNSEL.`` and Rule 25(a)(5) lines otherwise
        fall through the headmatter parser and become apparent unplaced prose.
        """
        text = " ".join(self.line_plain_text(line) for line in seg).strip().lower()
        if getattr(self, "_style", "").startswith("summary_order"):
            if (
                "rulings by summary order" in text
                or text == "counsel."
                or "appellate procedure 25(a)(5)" in text
            ):
                return True
        return super().skip_headmatter_segment(seg)

    # CA2 sets its summary orders (and some opinions) on numbered paper: a left
    # column of sequential line numbers (x0≈44, the body at x0≈86) that, left in
    # place, pdfplumber merges onto each line ('10 PER CURIAM:', '8 DAVID JOHN
    # CAMPBELL,') — breaking byline, caption, and heading detection. There is no
    # margin rule, so the gutter is found by CONTENT: a far-left column of bare
    # integers. Gated on detection, so un-numbered filings are untouched.
    def page_lines(self, page):
        if getattr(self, "_ca2_notice_furniture", None) is not None and page.page_number == 1:
            for line in page.extract_text_lines():
                text = " ".join((line.get("text") or "").split())
                if "Appellate Procedure 25(a)(5)" in text and text not in self._ca2_notice_furniture:
                    self._ca2_notice_furniture.append(text)
        gx = self._linenum_gutter_x(page)
        if gx is not None:
            gutter_start = 0.0
            if page.page_number == 1:
                # Summary-order advisories precede the numbered caption/body
                # on page 1. Filtering the whole page clips their first
                # letters because the advisory itself starts at x≈45, just
                # like the real gutter. Begin filtering at the first line
                # whose text actually carries a gutter number.
                for line in page.extract_text_lines():
                    chars = [c for c in line.get("chars", []) if c.get("text", "").strip()]
                    if chars and chars[0].get("text", "").isdigit() and chars[0].get("x0", 99) < 65:
                        gutter_start = line.get("top", 0)
                        break
            page = page.filter(
                lambda c: c.get("top", 0) < gutter_start
                or c.get("x0", 0) >= gx
            )
        lines = super().page_lines(page)
        # A separate writing can wrap its byline after "and":
        # ``CABRANES, Circuit Judge, concurring in the judgment and`` /
        # ``opinion of the Court:``.  Join those two physical lines so the
        # federal byline grammar sees the complete kind and terminator.
        out, index = [], 0
        while index < len(lines):
            line = lines[index]
            text = self.line_plain_text(line).strip()
            if (
                index + 1 < len(lines)
                and "Circuit Judge," in text
                and text.lower().endswith(" and")
            ):
                nxt = lines[index + 1]
                tail = self.line_plain_text(nxt).strip()
                if tail.lower().startswith("opinion of the court"):
                    merged = dict(line)
                    merged["chars"] = (line.get("chars") or []) + (nxt.get("chars") or [])
                    merged["text"] = f"{text} {tail}"
                    merged["x1"] = max(line.get("x1", 0), nxt.get("x1", 0))
                    merged["bottom"] = max(
                        line.get("bottom", line.get("top", 0)),
                        nxt.get("bottom", nxt.get("top", 0)),
                    )
                    out.append(merged)
                    index += 2
                    continue
            out.append(line)
            index += 1
        return self._fold_writing_bylines(out)

    def find_footnote_separator(self, page):
        """CA2 uses two related footnote-rule indents.

        Full-width prose pages anchor the ~144pt rule at x≈108; pages whose
        main text is already inset anchor a ~110pt rule at x≈144.  Require
        footnote-sized text below the rule so an underline/caption shelf cannot
        become a separator.
        """
        # The rail is read off THIS PAGE, not the document. A stapled decision
        # sets each writing to its own measure — in an en banc denial the lead
        # dissent runs at x0=72 while the rest of the document runs at x0=108 —
        # so anchoring on the document-wide baseline found no separator on the
        # dissent's pages at all, and every one of its footnotes was swallowed
        # into the body as prose.
        rail = self._page_rail(page)
        rails = {rail, rail + 36, self.body_baseline_x0, self.body_baseline_x0 + 36}
        candidates = []
        # Some chambers FILL the rule as a path rather than stroking a rect, and
        # pdfplumber returns those in ``page.curves``. provencher carries no
        # thin rect on any of its twelve pages — its separator is a 143.9pt
        # curve sitting on the page's own measured rail — so a rect-only scan
        # found nothing and all of its footnotes shipped as body prose.
        for rect in list(page.rects) + list(getattr(page, "curves", None) or []):
            width = rect.get("x1", 0) - rect.get("x0", 0)
            if not (
                rect.get("height", 0) < 2
                and 100 <= width <= 155
                and any(abs(rect.get("x0", 0) - r) <= 5 for r in rails)
                and rect.get("top", 0) > page.height * 0.30
            ):
                continue
            below = [
                char
                for char in page.chars
                if rect["top"] + 2 <= char.get("top", 0) <= rect["top"] + 55
                and (char.get("text") or "").strip()
            ]
            small = (
                bool(below)
                and sum(char.get("size", 99) <= 12.5 for char in below)
                >= len(below) * 0.7
            )
            # A FLAT 12.5pt IS THIS COURT'S USUAL BODY SIZE SMUGGLED IN AS A
            # CONSTANT. provencher sets the whole document — body and notes
            # alike — at 13.0pt and raises only the label digit to 8.0pt, so
            # every character under a real separator measured 'not small' and
            # the rule was thrown away. The raised label is the corroboration
            # that survives a court whose notes are body-sized; it is the same
            # test base step 2 uses, and a caption shelf or an underline has no
            # label under it either way.
            if small or self._labelled_note_below(page, rect["top"]):
                candidates.append(rect)
        top = min(candidates, key=lambda rect: rect["top"])["top"] if candidates else None
        # NUMBERED PAPER DRAWS NO SEPARATOR. campbell keys its caption footnote
        # to the party it qualifies ('Defendants-Appellees.*') and prints the
        # note at the foot of page 1 with nothing ruled above it — so the
        # pipeline saw no footnote region at all, and the note's lines arrived in
        # the headmatter as if they were caption and summary. The page still says
        # where the note begins: a row that opens with the reference MARK, set
        # off by a gap wider than the page's own leading. Make that the
        # separator, and the note becomes a footnote like any other.
        if top is None:
            top = self._marked_footnote_top(page)
        # Page 1's separator is also the floor of the HEADMATTER. Below it sits
        # the caption's own footnote — CA2's '* The Clerk of Court is
        # respectfully directed to amend the official case caption …' — which is
        # a footnote, not a headmatter row, and was being read into the summary.
        if page.page_number == 1:
            self._hm_footnote_top = top
        return top

    # CA2 keys its caption footnote with a star, and sets that star in two ways
    # the shared label reader does not expect: full SIZE rather than
    # superscripted (campbell), and with the ASTERISK OPERATOR '∗' (U+2217)
    # rather than a plain asterisk (alvarenga). Both came back labelled '?'.
    FOOTNOTE_LABEL_CHARS = set("0123456789*†‡§¶∗⁎﹡＊")
    # The marks CA2 keys a CAPTION footnote with — stars and daggers, in the
    # several glyphs the corpus uses for them.
    _CAPTION_MARKS = frozenset("*†‡∗⁎﹡＊")

    def detect_footnote_label(self, line):
        label = super().detect_footnote_label(line)
        if label and label != "?":
            return label
        # A full-size mark standing at the head of a footnote-zone line, set off
        # from the note's first word, is that note's label.
        chars = [c for c in (line.get("chars") or ()) if (c.get("text") or "").strip()]
        if not chars:
            return label
        # STAR FAMILY ONLY. '§' and '¶' are label characters, but full size at
        # the head of a line they are ordinary legal prose ('§ 1226(a) allows
        # for release on bond'), and accepting them invented a footnote labelled
        # '§' in the middle of cunha's majority. A caption footnote is always
        # keyed with a star or a dagger.
        head = chars[0].get("text") or ""
        if head not in self._CAPTION_MARKS:
            return label
        text = " ".join(self.line_plain_text(line).split())
        return head if len(text) > 1 and text[1:2] in (" ", "\t") else label

    def _marked_footnote_top(self, page):
        """Top of an unruled footnote block, or None.

        The block opens with a reference mark, sits in the lower half of the
        page, and is separated from the text above it by more than that page's
        own leading — the three things that make it a note rather than a
        paragraph that happens to start with a symbol."""
        lines = sorted(page.extract_text_lines(), key=lambda ln: ln.get("top", 0))
        lead = self._page_lead(lines) or 0
        saw_dinkus = False
        for prev, line in zip(lines, lines[1:]):
            if line.get("top", 0) < page.height * 0.45:
                continue
            gap = line.get("top", 0) - prev.get("top", 0)
            if not saw_dinkus and lead and gap <= lead * 1.4:
                continue
            text = " ".join((line.get("text") or "").split())
            # A line that is NOTHING BUT marks is the '* * *' section dinkus
            # CA2 closes an opinion with, not a note opener — hampton,
            # xinuos and schneiderman each grew a trailing '*' note holding
            # the dinkus and the closing paragraph beneath it. But the
            # dinkus still testifies that what follows is SET APART: in
            # farrington the real '* Judge Park took no part ...' note sits
            # directly under it, closer than the leading test allows, and
            # skipping the dinkus outright lost that note. So the dinkus is
            # never the opener, and the first mark-opening line after it
            # need not re-prove its own whitespace.
            if text and set(text) <= (set(self._CAPTION_MARKS) | {" "}):
                saw_dinkus = True
                continue
            if self._opens_with_footnote_mark(text):
                return line.get("top", 0) - 1.0
        return None

    def _page_rail(self, page):
        """The left rail of this page's own body text.

        The LEFTMOST recurring x0 among its full-measure lines. Nothing in a
        writing is set left of its rail — first lines indent past it, quotations
        indent further, and footnotes sit on it — so the leftmost column that
        recurs is the rail.

        It used to be the MODAL x0, on the reasoning that wrapped continuations
        all return to the rail. They do, but so do a block quotation's, and on a
        page the quotation dominates the mode is the QUOTATION's indent:
        Salters p5 measured 108 on a document railed at 72, which put the 144pt
        footnote rule at x0=72 outside every rail candidate. No separator was
        found, and the majority's footnote 1 was delivered as body prose with
        its <footnotemark> still attached.

        Recurrence is what makes 'leftmost' safe — a single outdented stray
        cannot move the rail."""
        x0s = Counter()
        for line in page.extract_text_lines():
            if line.get("x1", 0) - line.get("x0", 0) < page.width * 0.45:
                continue
            x0s[round(line.get("x0", 0))] += 1
        if not x0s:
            return self.body_baseline_x0
        recurring = [x for x, hits in x0s.items() if hits >= 2]
        return float(min(recurring) if recurring else x0s.most_common(1)[0][0])

    @staticmethod
    def _linenum_gutter_x(page):
        """X just right of a left-margin line-number gutter, or None. The gutter
        is a vertical column of >=5 bare digit glyphs clustered at the far-left
        margin (x0 < 75). Cluster around the modal left edge so a stray body
        digit further right doesn't defeat detection (two-digit numbers span
        ~1.5 glyph widths, hence the 12pt window)."""
        digits = [
            c for c in page.chars if c.get("text", "").isdigit() and c.get("x0", 0) < 75
        ]
        if len(digits) >= 5:
            mode = Counter(round(c["x0"]) for c in digits).most_common(1)[0][0]
        else:
            mode = 999
        # Ordinary CA2 body text starts at x≈72. A sentence beginning with a
        # digit can therefore create a convincing-looking cluster of digits at
        # the body margin, but a real numbered-paper gutter is materially
        # farther left (≈44–48pt). Do not clip the first character of normal
        # prose merely because several paragraphs start with citations.
        if mode < 65:
            col = [c for c in digits if abs(c["x0"] - mode) <= 12]
            if len(col) >= 5:
                return max(c["x1"] for c in col) + 2

        # Some later CA2 writings restart line numbering immediately beside
        # an inset body column (numbers at x≈79/84, prose at x≈108), rather
        # than using the far-left x≈44 gutter present on the lead writing.
        # Identify the column by a long consecutive run of number-only words.
        words = [
            w
            for w in page.extract_words()
            if (w.get("text") or "").isdigit()
            and int(w["text"]) <= 40
            and w.get("x0", 999) < 95
            and w.get("x1", 999) < 105
        ]
        if len(words) < 8:
            return None
        words.sort(key=lambda word: word["top"])
        values = [int(word["text"]) for word in words]
        consecutive = sum(1 for a, b in zip(values, values[1:]) if b == a + 1)
        if consecutive < 6:
            return None
        return max(word["x1"] for word in words) + 4
