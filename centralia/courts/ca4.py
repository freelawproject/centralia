"""United States Court of Appeals for the Fourth Circuit."""

from __future__ import annotations
from ._circuit import (
    FederalCircuitBase,
    _HISTORY_OPENERS,
    _STATUS_WORDS,
    _is_typed_rule,
    _plain,
)


class FourthCircuit(FederalCircuitBase):
    court_id = "ca4"
    court_label = "United States Court of Appeals for the Fourth Circuit."
    circuit_phrase = "fourth circuit"

    # Headmatter criteria: PUBLISHED / UNPUBLISHED flag above the banner; drawn dividers.
    parse_criteria_enabled = True
    criteria_lift_publication = True
    gap_tight_max = 12.0
    gap_single_max = 20.0
    gap_double_max = 36.0
    page2_header_cutoff = 30.0


    # ------------------------------------------------------------------ #
    # CA4 reads its OWN headmatter.                                      #
    # ------------------------------------------------------------------ #
    # The shared walk reads a headmatter row by row because most circuits
    # put more than one thing in a band. CA4 does not: it rules off every
    # section and puts exactly one thing in each —
    #
    #     PUBLISHED
    #     ----------------------------------------------------------------
    #     UNITED STATES COURT OF APPEALS FOR THE FOURTH CIRCUIT
    #     ----------------------------------------------------------------
    #     No. 25-1448
    #     ----------------------------------------------------------------
    #     AMERICAN ACCEPTANCE CORPORATION OF SC, ...
    #              Plaintiff - Appellant,
    #         v.
    #     JOHN GIETZ; SHERIFF BRYAN KOON, ...
    #              Defendants - Appellees.
    #     ----------------------------------------------------------------
    #     Appeal from the United States District Court for the District of
    #     South Carolina, at Columbia.  Mary G. Lewis, District Judge.
    #     ----------------------------------------------------------------
    #     Argued:  October 23, 2025          Decided:  May 12, 2026
    #     ----------------------------------------------------------------
    #     Before BENJAMIN, Circuit Judge, FLOYD, Senior Circuit Judge, and
    #     Patricia Tolliver GILES, United States District Judge ...
    #     ----------------------------------------------------------------
    #     Affirmed by published opinion.  Judge Giles wrote the opinion, in
    #     which Judge Benjamin and Judge Floyd joined.
    #     ----------------------------------------------------------------
    #     ARGUED:  Joseph Studemeyer, STUDEMEYER LAW FIRM, P.C., ...
    #
    # So the band IS the unit of meaning here, and reading it as one asks a
    # much simpler question — what is this band? — than reading its rows and
    # hoping the state machine is in the right state when each arrives. It is
    # also the whole point of doing it here: nothing another circuit needs can
    # move CA4's answer, and nothing CA4 needs has to be argued for in a file
    # eleven other circuits share.
    #
    # A consolidated record repeats docket-then-caption and states the origin,
    # the dates and the roster ONCE at the end, for all of them.

    def parse_criteria(self, doc):
        """Read CA4's headmatter with CA4's own vocabulary.

        Row by row rather than band by band: the rules are a helpful grouping
        but not a reliable one — most records fence every section, and some
        (the immigration petitions) draw no rule at all between the origin,
        the dates, the roster, the disposition and the appearances. What IS
        reliable is what each row says about itself, because CA4 never says
        two things one way:

            'No. 25-1448'                     the docket, opening a case
            'Appeal from the ...'             the origin
            'Argued:  ... Decided:  ...'      the dates
            'Before BENJAMIN, Circuit Judge'  the roster
            '... by published opinion. ...'   the disposition
            'ARGUED:' / 'ON BRIEF:'           the appearances, to the end

        Once any of those has been seen the caption is finished, so a later
        roll of names is amici belonging to the case it follows — not a new
        case, and not a title.
        """
        if not self.parse_criteria_enabled:
            return
        crit = {}
        cases = []
        banner, panel_parts, disposition = [], [], []
        dates, publication, counsel_at = {}, None, None
        lifted, tail_started, roster_open = {}, False, False

        rows = [
            (i, t)
            for i, r in enumerate(doc.summary)
            # The rules are the walls between sections, not content. Left in,
            # they arrived as rows in their own right and were filed into
            # whichever field was open — '__DIVIDER__' at the head of a case
            # name.
            if not (
                _is_typed_rule(r)
                or (isinstance(r, str) and _plain(r).strip() == self.HEADMATTER_DIVIDER)
            )
            for t in self._zone_texts([r])
            if t.strip()
        ]
        for i, text in rows:
            low = " ".join(text.lower().split())

            if counsel_at is not None:
                continue                      # everything below is counsel

            if publication is None:
                flag = self._publication_flag(text)
                if flag:
                    publication = flag
                    continue
                flag, rest = self._split_publication(text)
                if flag and rest and self._is_court_banner(rest):
                    publication, lifted[text] = flag, rest
                    text = rest
                    low = " ".join(text.lower().split())

            if not banner and self._is_court_banner(text):
                banner.append(text)
                continue

            if roster_open:
                panel_parts.append(text)
                roster_open = not self._roster_closes(" ".join(panel_parts))
                continue

            if self._is_docket_text(text):
                docket, rest = self._split_docket(text)
                case = {"docket": docket, "caption": [], "prior_history": None}
                cases.append(case)
                if rest:
                    case["caption"].append(rest)
                tail_started = False
                continue

            # THE DISPOSITION IS TESTED BEFORE THE ORIGIN. Its opening words
            # are the outcome, and those can be the same words an origin line
            # opens with ('Petition for review granted; order vacated and
            # remanded by published opinion. Judge Novak wrote ...'). Read as
            # the origin it replaced the tribunal the case actually came from.
            if self._is_disposition(text):
                disposition.append(text)
                tail_started = True
                continue

            if low.startswith(_HISTORY_OPENERS):
                if not cases:
                    cases.append(
                        {"docket": None, "caption": [], "prior_history": None}
                    )
                forum, lower, judge = self._split_lower_docket(text)
                cases[-1]["prior_history"] = forum
                if lower:
                    cases[-1]["lower_docket"] = lower
                if judge:
                    cases[-1]["lower_judge"] = judge
                tail_started = True
                continue

            labelled = self._split_labelled_dates(text)
            if labelled:
                dates.update(labelled)
                tail_started = True
                continue

            if text.startswith("Before"):
                panel_parts.append(text)
                roster_open = not self._roster_closes(text)
                tail_started = True
                continue

            if self._tail_kind(text) == "counsel":
                counsel_at = i
                tail_started = True
                continue

            # EVERYTHING BETWEEN THE DOCKET AND THE ORIGIN IS THE CAPTION.
            # Not only the rows that look like parties: the 'v.' between them
            # says nothing for itself, and the wrapped second half of a long
            # respondent list looks like prose. CA4 puts nothing else in that
            # span, so testing each row's appearance dropped pieces of the
            # case name it was supposed to be reading.
            if not tail_started and cases:
                cases[-1]["caption"].append(text)
                continue
            # Below the origin, anything unrecognised — the unpublished-
            # opinions notice, a caption footnote — is left out rather than
            # filed under the nearest field.

        for case in cases:
            case["case_name"] = " ".join(case["caption"])

        # ONE ORIGIN FOR ALL OF THEM: a consolidated CA4 record repeats
        # docket-and-caption and then states the court appealed from once,
        # below the last of them, for every case in the record.
        if len(cases) > 1:
            for key in ("prior_history", "lower_court", "lower_docket",
                        "lower_judge"):
                stated = next((c.get(key) for c in cases if c.get(key)), None)
                if stated:
                    for case in cases:
                        if not case.get(key):
                            case[key] = stated

        # BEFORE the publication lift rewrites ``doc.summary`` — the counsel
        # slice is an index into the rows as they were read, and dropping the
        # flag's row shifts every index below it by one.
        counsel = self._counsel_from(doc.summary, counsel_at)
        if publication:
            crit["publication"] = publication
            doc.summary = [
                lifted.get(_plain(r).strip(), r)
                for r in doc.summary
                if not (isinstance(r, str) and _plain(r).strip() == publication)
            ]
        if banner:
            crit["court"] = " ".join(banner)
        if cases:
            crit["cases"] = cases
        if panel_parts:
            crit["panel_line"] = " ".join(panel_parts)
            crit["panel"] = self._panel_names(crit["panel_line"])
        if disposition:
            crit["disposition"] = " ".join(disposition)
        if counsel:
            crit["counsel"] = counsel
        for key, value in dates.items():
            crit[f"date_{key}"] = value
        self._publish_criteria(doc, crit)

    @staticmethod
    def _roster_closes(text):
        """CA4 ends its roster on the bench word, or on the designation clause
        a visiting judge carries. Until then it is still running — the roster
        wraps over three rows when a district judge sits by designation."""
        return text.rstrip(".:;, ").lower().endswith(
            ("judge", "judges", "designation")
        )

    def _counsel_from(self, rows, start):
        """The appearances verbatim from their opener down, spacing intact.

        CA4 sets them last and wraps them over many rows, only the first of
        which announces itself. The blank rows inside separate one side from
        the other, so they are kept; the notice the court sometimes prints
        under them ('Unpublished opinions are not binding precedent in this
        circuit.') is not an appearance and is dropped off the end."""
        if start is None:
            return None
        out = []
        for row in rows[start:]:
            if isinstance(row, dict):
                continue
            text = _plain(row).rstrip()
            if _is_typed_rule(row) or text.strip() == self.HEADMATTER_DIVIDER:
                continue
            if not text.strip():
                if out and out[-1]:
                    out.append("")
                continue
            if "not binding precedent" in text.lower():
                break
            out.append(text)
        while out and not out[-1]:
            out.pop()
        return "\n".join(out) or None

    def _tail_kind(self, text):
        """CA4 ANNOUNCES ITS APPEARANCES AND NOTHING ELSE DOES.

        The band opens with the court's own bold label — 'ARGUED:' or 'ON
        BRIEF:' — and runs to the next rule. A row that opens neither is not
        counsel, whatever it looks like: the disposition names judges, the
        origin line names the trial judge and the town, and read as
        appearances they filled the field with things nobody appeared for.
        """
        head = " ".join(text.split()).upper()
        if head.startswith(("ARGUED:", "ARGUED :", "ON BRIEF:", "ON BRIEF :")):
            return "counsel"
        return "summary"

    def _is_disposition(self, text):
        """'Affirmed by published opinion. Judge Benjamin wrote the opinion, in
        which Judge Agee and Judge Richardson joined.'

        CA4 states what it did in a band of its own between the roster and the
        appearances, always in the same form: the outcome, then 'by
        published/unpublished ... opinion', then who wrote and who joined."""
        low = " ".join(text.split()).lower()
        return "by published " in low or "by unpublished " in low

    @staticmethod
    def _panel_names(text):
        """CA4 seats district judges by designation and says so in the roster
        ('... and Patricia Tolliver GILES, United States District Judge for
        the Eastern District of Virginia, sitting by designation.'). The
        designation clause names no judge, so the roster ends where it
        begins."""
        flat = " ".join(text.split())
        at = flat.lower().find("sitting by")
        if at > 0:
            flat = flat[:at].rstrip(" ,")
        return FourthCircuit.__mro__[1]._panel_names(flat)

    def _byline_split(self, line):
        """CA4 opinion bylines are ALL-CAPS ('GREGORY, Chief Judge:', 'PATRICIA
        TOLLIVER GILES, District Judge:'). A title-case name is the trial judge
        named in the lower-court history line ('... at Columbia. Mary G. Lewis,
        District Judge.'), which must stay in the headmatter, not open the
        opinion. So a byline whose name carries any lowercase letter is rejected
        (PER CURIAM / BY THE COURT pass through)."""
        r = super()._byline_split(line)
        if r is None:
            return None
        up = r[0].upper()
        if up.startswith(("PER CURIAM", "BY THE COURT")):
            return r
        name = r[0].split(",", 1)[0]
        letters = [c for c in name if c.isalpha()]
        if not letters or all(c.isupper() for c in letters):
            return r
        # A DISTRICT JUDGE SITTING BY DESIGNATION IS PRINTED IN FULL, with only
        # the surname capitalised — 'David J. NOVAK, United States District
        # Judge for the Eastern District of Virginia, sitting by designation:',
        # 'Patricia Tolliver GILES, ...'. That IS the court's byline form, so
        # rejecting every name carrying a lowercase letter lost the whole
        # majority opinion on those records. The trial judge named in the
        # history line ('Mary G. Lewis, District Judge.') has no capitalised
        # surname and is still rejected.
        surname = name.split()[-1].strip(".,")
        tail = [c for c in surname if c.isalpha()]
        if len(tail) >= 2 and all(c.isupper() for c in tail):
            return r
        return None
