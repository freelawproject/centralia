"""United States Court of Appeals for the Seventh Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase, _plain


class SeventhCircuit(FederalCircuitBase):
    court_id = "ca7"
    court_label = "United States Court of Appeals for the Seventh Circuit."
    circuit_phrase = "seventh circuit"

    # Headmatter criteria: typed rules; docket and case name share one zone.
    parse_criteria_enabled = True

    banner_zone_gates_blanks = False

    @staticmethod
    def _panel_names(text):
        """CA7's order form gives each judge a row and a bench title of their
        own ('FRANK H. EASTERBROOK, Circuit Judge' / 'CANDACE
        JACKSON-AKIWUMI, Circuit Judge' / 'NANCY L. MALDONADO, Circuit
        Judge'). Split on the court's commas, every fragment after the first
        carries the title of the judge BEFORE it, so only one name survived.

        Where the title repeats, the title is the separator: each judge is the
        text between one title and the last comma before the next. The
        ordinary roster form, with one title closing the whole list ('Before
        ROVNER, BRENNAN, and KOLAR, Circuit Judges.'), is unchanged — it is
        read by the family splitter as before."""
        titles = [
            i
            for i, tok in enumerate(text.split())
            if tok.strip(".,;:").lower() in ("judge", "judges")
        ]
        if len(titles) < 2:
            return FederalCircuitBase._panel_names(text)
        names, tokens, start = [], text.split(), 0
        for at in titles:
            piece = " ".join(tokens[start:at]).strip()
            for opener in ("Before:", "Before"):
                if piece.startswith(opener):
                    piece = piece[len(opener):].strip()
            # The bench title follows the judge's own comma; everything after
            # the last one is the title's qualifiers ('Senior Circuit').
            cut = piece.rfind(",")
            name = (piece[:cut] if cut > 0 else piece).strip(" ,")
            if name:
                names.append(name)
            start = at + 1
        return names

    def _court_name(self, rows):
        """'United States Court of Appeals' + 'For the Seventh Circuit'.

        CA7 sets the two over separate rows in different faces, with the
        courthouse's address run onto the second ('For the Seventh Circuit
        Chicago, Illinois 60604'). The family reader takes the first row alone
        and stops, so the circuit went unrecorded; the address is not part of
        the court's name and is left in the raw headmatter."""
        for row in rows:
            if not isinstance(row, str):
                continue
            text = _plain(row).strip()
            low = text.lower()
            at = low.find(self.circuit_phrase)
            if at >= 0:
                return text[: at + len(self.circuit_phrase)].strip()
        return None

    def parse_criteria_court(self, doc, crit):
        name = self._court_name(doc.summary)
        if not name or not crit.get("court"):
            return
        # ...only where the family reader has not already read the circuit
        # into it. Where the court's name arrives on ONE row, appending
        # repeated it ('... For the Seventh Circuit For the Seventh Circuit').
        if self.circuit_phrase in crit["court"].lower():
            return
        crit["court"] = f"{crit['court']} {name}".strip()


    def parse_criteria(self, doc):
        """The shared walk, then CA7's two-column caption read as two things.

        The order form holds the caption in columns with nothing drawn between
        them: the parties on the left, and on the right the court the case
        came from, its docket numbers and the district judge. Flattened into
        one roll of text the origin was read as more parties, so the case name
        ran on into the district it was appealed from."""
        super().parse_criteria(doc)
        crit = doc.criteria or {}
        self.parse_criteria_court(doc, crit)
        cases = crit.get("cases") or []
        if not cases:
            self._publish_criteria(doc, crit)
            return
        block = next(
            (
                r
                for r in doc.summary
                if isinstance(r, dict) and r.get("__caption__") and r.get("right")
            ),
            None,
        )
        if block is None:
            return
        left = [_plain(c).strip() for c in block.get("left") or []]
        right = [_plain(c).strip() for c in block.get("right") or []]
        left = [t for t in left if t]
        right = " ".join(t for t in right if t)
        if not left or not right:
            return
        case = cases[0]
        case["caption"] = left
        case["case_name"] = " ".join(left)
        forum, lower, judge = self._split_lower_docket(right)
        case["prior_history"] = forum or right
        if lower:
            case["lower_docket"] = lower
        if judge:
            case["lower_judge"] = judge
        self._publish_criteria(doc, doc.criteria)

    def find_caption_divider(self, page):
        """CA7's order form holds its caption in two columns with NOTHING
        drawn between them — the parties on the left, the court appealed from
        on the right:

            CLOSE ARMSTRONG, LLC, et al.,     Appeal from the United States
                 Plaintiffs-Appellants,       District Court for the Northern
                                              District of Indiana ...
                v.
                                              Nos. 3:18-cv-00270 & 3:18-cv-00494
            TRUNKLINE GAS COMPANY, LLC,
                 Defendant-Appellee.          Damon R. Leichty,
                                              District Judge.

        Clustered as ordinary lines the two columns merge onto one baseline
        and the case name comes out interleaved with the district it came
        from ('CLOSE ARMSTRONG, LLC, et al., Appeal from the United States
        District Plaintiffs-Appellants, Court for ...').

        There is no rule to find, so the gutter is MEASURED: inside the band
        between the docket and the order's title, take the widest column of
        the page that no character occupies. Never invented — if no such
        column exists, or the band is not there, this is not a two-column
        caption and nothing is split."""
        drawn = super().find_caption_divider(page)
        if drawn is not None or page.page_number != 1:
            return drawn
        lines = page.extract_text_lines()
        title = docket = None
        for ln in lines:
            text = (ln.get("text") or "").strip()
            if docket is None and text.startswith(("No. ", "Nos. ")):
                docket = ln
            if "".join(text.split()).upper().startswith("ORDER") and len(text) < 40:
                title = ln
                break
        if title is None or docket is None or docket["top"] >= title["top"]:
            return None
        top, bottom = docket["bottom"] + 1, title["top"] - 1
        # WITHOUT THE SPACE GLYPHS. CA7 draws them explicitly, right across
        # the gutter, so measured with them in place the band has no empty
        # column anywhere and no two-column caption is ever found.
        band = [
            c
            for c in page.chars
            if top <= c["top"] <= bottom and (c.get("text") or "").strip()
        ]
        if not band:
            return None
        # A GUTTER IS EMPTY ON EVERY ROW. Measured as one union over the whole
        # band it disappears — the left column's longest line and the right
        # column's lines together tile the width, leaving no gap anywhere. So
        # each row is measured on its own and the empty columns intersected.
        rows = {}
        for c in band:
            rows.setdefault(round(c["top"] / 3.0), []).append(c)
        left = min(c["x0"] for c in band)
        right = max(c["x1"] for c in band)
        empty = [(left, right)]
        for chars in rows.values():
            spans = sorted((c["x0"], c["x1"]) for c in chars)
            holes, reach = [], spans[0][1]
            if spans[0][0] > left:
                holes.append((left, spans[0][0]))
            for x0, x1 in spans:
                if x0 > reach:
                    holes.append((reach, x0))
                reach = max(reach, x1)
            if reach < right:
                holes.append((reach, right))
            empty = [
                (max(a0, b0), min(a1, b1))
                for a0, a1 in empty
                for b0, b1 in holes
                if min(a1, b1) - max(a0, b0) > 0
            ]
            if not empty:
                return None
        gap_at, gap_w = None, 0.0
        for x0, x1 in empty:
            if x1 - x0 > gap_w:
                gap_w, gap_at = x1 - x0, (x0 + x1) / 2.0
        # A GUTTER, NOT AN INDENT. It has to be wider than the deepest indent
        # the caption itself uses, and it has to have text on both sides of it
        # — otherwise what was found is the left margin of a single column.
        if gap_at is None or gap_w < 12.0:
            return None
        if gap_at - left < 60.0 or right - gap_at < 60.0:
            return None
        return gap_at, top, bottom

    def _percuriam_start(self, all_segments):
        """An unsigned CA7 order opens at its TITLE, not below the roster.

        The order form prints the roster first and the case's own particulars
        after it — the docket, then a two-column block with the parties on the
        left and the court appealed from on the right — and only then the
        court's writing:

            NANCY L. MALDONADO, Circuit Judge
            No. 24-1630
            CLOSE ARMSTRONG, LLC, et al.,   Appeal from the United States ...
                 Plaintiffs-Appellants,     Court for the Northern District ...
            O R D E R
            All members of the panel have voted to deny the petition ...

        Opening the opinion at the first segment below the roster took the
        docket and the whole caption into the body with it. The court sets the
        title LETTER-SPACED ('O R D E R'), which is why the shared
        order-heading fallback did not see it either."""
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip()
            if "".join(text.split()).upper().startswith("ORDER") and len(text) < 40:
                return i
        return super()._percuriam_start(all_segments)

    def _panel_segment(self, all_segments):
        """CA7's ORDER form sets one judge per row, and the roster is all of
        them.

            Before
            FRANK H. EASTERBROOK, Circuit Judge
            CANDACE JACKSON-AKIWUMI, Circuit Judge
            NANCY L. MALDONADO, Circuit Judge

        Each row closes on its own bench title, so the shared reader took the
        first as the whole roster — and the third then answered the byline
        grammar and opened an opinion, cutting the headmatter off above the
        docket, the caption and the order itself.

        What separates a roster row from a byline here is the court's own
        punctuation: it TERMINATES a byline ('ROVNER, Circuit Judge.') and
        does not terminate a roster row. So the roster runs on for as long as
        the rows are unterminated."""
        panel = super()._panel_segment(all_segments)
        if panel is None:
            return None
        while panel + 1 < len(all_segments):
            nxt = all_segments[panel + 1][1]
            if not nxt:
                break
            text = " ".join(
                self.line_plain_text(l).strip() for l in nxt
            ).strip()
            if text.endswith((".", ":", ";")):
                break
            if not text.rstrip().lower().endswith(("judge", "judges")):
                break
            panel += 1
        return panel

    body_baseline_x0 = 144.0
    # A rehearing order sets its quoted amendment right down to y≈735, past the
    # shared 725 cutoff, which took a line of the quote with it. CA7 prints its
    # folio in the running HEAD, so there is no bottom furniture to protect —
    # nothing else in the corpus sits below 720.
    margin_bottom = 750.0
    gap_tight_max = 10.0
    gap_single_max = 14.0
    gap_double_max = 24.0

    # CA7's running header is a docket line with the folio at one end —
    # 'No. 24-2806 3' / 'Nos. 25-2878 & 25-2879 3' / 'No. 24-1630 Page 2' — and
    # it is set at two very different heights: top~104 in the bound measure
    # (body below it) and top~40-76 in the slip measure (body at ~72-108). A
    # blanket y cutoff cannot separate the two: at 95pt it left the bound header
    # in the body AND ate the first body lines of the slip pages. Identify the
    # header by its FORM instead (``is_docket_line``) and let the base sweep the
    # contiguous run at the top of the page; ``_drop_running_header`` records it.
    page2_header_cutoff = 30.0
    running_header_docket = True
    running_header_max_top = 110.0

    def is_docket_line(self, text) -> bool:
        toks = (text or "").split()
        if len(toks) < 2:
            return False
        if toks[0] in ("No.", "Nos."):
            # A trailing folio, bare ('… 24-2806 3') or labelled ('… Page 2').
            if toks[-1].isdigit():
                toks = toks[:-1]
                if toks and toks[-1].lower() == "page":
                    toks = toks[:-1]
        elif toks[0].isdigit() and len(toks) > 2 and toks[1] in ("No.", "Nos."):
            toks = toks[1:]  # a leading folio ('2 No. 24-2806')
        else:
            return False
        dockets = [t for t in toks[1:] if t not in ("&", "and")]
        if not dockets:
            return False
        return all(
            t.count("-") == 1 and all(p.isdigit() for p in t.strip(",;").split("-"))
            for t in dockets
        )

    def find_footnote_separator(self, page):
        return self._sep_at(page, 140, 150)
