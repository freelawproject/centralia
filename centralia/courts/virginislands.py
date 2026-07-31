"""Supreme Court of the Virgin Islands.

Six of the ten fixtures are SCANS (no text layer at all) and are reported as
non-digital; the four born-digital slip opinions share one template:

    For Publication                                     (bold, top-left)
    IN THE SUPREME COURT OF THE VIRGIN ISLANDS           (bold 14pt, centered)
    PARTY,                    )  S. Ct. Civ. No. 2025-0034
        Appellant,            )  Re: Super. Ct. Civ. No. 343/2017 (STX)
        v.                    )
    PARTY.                    )
    ------------------------- (a half rule closing the caption)
    On Appeal from the Superior Court of the Virgin Islands   (centered)
    Considered: … / Filed: …                                 (centered)
    Cite as: 2026 VI 3                                       (centered)
    BEFORE: RHYS S. HODGE, Chief Justice; …                   (panel roster)
    APPEARANCES: …                                            (counsel)
    OPINION OF THE COURT                                     (bold 14pt, centered)
    HODGE, Chief Justice.                                    (bold byline)
    ¶ 1  … double-spaced body at x0=72 …

So the caption is a ')' glyph rail (the Parenthetical Box) and the byline is
the ALL-CAPS surname + spelled-out bench title of the ``StateSupreme`` family.
What needed describing is this court's own furniture and typography:

* a FOUR-line running head in the top margin of every page after the first
  (italic short case name + cite / 'S. Ct. Civ. No. …' / 'Opinion of the
  Court' / 'Page 3 of 24'), set at 10pt where the body is 12pt;
* footnotes set at BODY size under a 144pt rule at the body rail, so the
  shared 'smaller text below the rule' discriminator can never fire — every
  footnote in the volume was being lost;
* a DOUBLE-spaced body (27.6pt leading), which puts every ordinary
  single-spaced quotation and bulleted list into the 'notice' band;
* a two-part sign-off — 'BY THE COURT: /s/ …' over the clerk's 'ATTEST: …'
  attestation — which is one signature block, not body.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# The running head's third row names the writing whose pages these are.
_RUNNING_HEAD_ROWS = (
    "s. ct. civ. no.",
    "s. ct. crim. no.",
    "s. ct. bhc. no.",
    "s. ct. misc. no.",
    "opinion of the court",
    "page ",
    "concurring opinion",
    "dissenting opinion",
)
# The clerk's attestation that closes the last page. Structurally it is a
# stack of short bold lines under a bold 'ATTEST:' lead, in the body column,
# after the court's own conformed signature — so the lead line is the anchor.
_ATTEST_LEAD = "attest:"
_COURT_LEAD = "by the court:"


class VirginIslandsSupreme(StateSupreme):
    court_id = "virginislands"
    court_label = "Supreme Court of the Virgin Islands."
    body_baseline_x0 = 72.0
    # Double-spaced at ~27.6pt; quotations and bullet lists are single-spaced
    # at ~13.8pt. The default bands already sort those two apart (13.8 <
    # gap_tight_max, 27.6 < gap_double_max), so only the 'notice' verdict on
    # the quotations needs correcting — see ``classify_segment``.
    #
    # ``StateSupreme`` already sets ``drop_notice_in_body = False``; keep it,
    # because a single-spaced run this court sets that is NOT a quotation (the
    # numbered mediation-participant list carried at the body rail) must still
    # come back as body rather than vanish.

    # Nothing on page 1 is small print: the smallest type there is the 9.5pt
    # 'APPEARANCES:' label, which is a real headmatter heading.
    notice_max_size = None
    split_line_stacks = True

    def matches_expected_layout(self, pdf) -> bool:
        """Page 1 names the court in its banner. The scans have no text layer
        at all, so this also keeps them from claiming the digital template."""
        if not pdf.pages:
            return False
        text = " ".join(
            (line.get("text") or "")
            for line in pdf.pages[0].extract_text_lines()
        ).lower()
        return "supreme court of the virgin islands" in text

    # ------------------------------------------------------------- furniture
    def extract(self, pdf_path: str):
        self._vi_furniture = []
        self._vi_para_no = 0
        doc = super().extract(pdf_path)
        self._lift_signoff(doc)
        return doc

    def _sweep_residual(self, doc, source_pages) -> None:
        """Flush the running heads onto the document BEFORE the completeness
        sweep. Appending them after ``extract`` returns would land them there
        after the sweep had already read the sections, so every head row would
        be reported unplaced while sitting in the Removed box."""
        extra = list(dict.fromkeys(getattr(self, "_vi_furniture", []) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def page_lines(self, page):
        """Route the four-row running head to ``dropped``.

        It is identified by TYPE SIZE plus the top margin: the head is set at
        10pt where the body and every heading are 12pt or 14pt, and it sits
        above top=90 where the body starts at 95. Position alone would be
        wrong — page 1's caption carries a 10pt right-hand column ('Re: Super.
        Ct. Civ. No. 343/2017 (STX)') well below the band, and the 9.5pt
        'APPEARANCES:' label is real headmatter further down still. The rows
        are confirmed by their fixed vocabulary or, for the italic short case
        name that leads the block, by sitting directly above such a row.
        """
        lines = super().page_lines(page)
        if page.page_number == 1:
            return lines
        head, kept = [], []
        for line in lines:
            size, _font, _bold = self.line_meta(line)
            if line.get("top", 0) < 90 and size <= 10.5:
                head.append(line)
            else:
                kept.append(line)
        if not head:
            return lines
        # Only a block that actually says what it is counts as the head; a
        # stray small line on its own stays in the body.
        texts = [self.line_plain_text(l).strip() for l in head]
        if not any(t.lower().startswith(_RUNNING_HEAD_ROWS) for t in texts):
            return lines
        for t in texts:
            if t:
                self._vi_furniture.append(t)
        return kept

    # ------------------------------------------------------------- footnotes
    def find_footnote_separator(self, page):
        """This court sets its footnotes at BODY size (12pt; only the label
        digit is raised), so the shared discriminator — footnote-sized text
        directly below the rule — can never fire and the whole zone reads as
        body or is lost. The rule itself is unmistakable: exactly one 144pt
        (2-inch) thin rule at the body rail per footnoted page.

        The other rules the template draws are all elsewhere — the caption's
        closing shelf is 266pt wide, the conformed-signature rule is also
        144pt but set out in the right-hand column at x0≈396, and the '/s/'
        underlines are 74–99pt — so the width plus the left edge is enough and
        no page-position fence is needed. That matters: a footnote-heavy sheet
        pushes the rule well above the half-page mark (ocean_pest p.13 draws
        it at 322 on a 792pt sheet).
        """
        return self.footnote_sep_fixed_left_rule(page, width=144.0)

    # ----------------------------------------------------------- blockquotes
    def classify_segment(self, seg) -> str:
        """Promote an indented single-spaced run to a block quote.

        The body is DOUBLE-spaced at ~27.6pt, so a quotation's ordinary single
        spacing (~13.8pt) lands under ``gap_tight_max`` and classifies as a
        'notice'. The family's both-margins test cannot catch these: this
        court indents a quotation only ONE step (x0=89 or 90 against a body
        rail of 72 — half of ``para_indent_min``), and its bulleted lists are
        indented on the left alone and run to the full body measure. With a
        double-spaced body the left indent plus the tight leading is already
        conclusive, so the right margin carries no signal and isn't consulted.
        """
        kind = super().classify_segment(seg)
        if kind != "notice" or len(seg) < 2:
            return kind
        width = getattr(self, "_page1_width", None) or 612.0
        x0s = [line["x0"] for line in seg]
        edge = min(x0s)
        # Indented in from the body rail, but not out in the right-hand
        # column (a signature block is not a quotation).
        if not self.body_baseline_x0 + 12 <= edge <= width * 0.4:
            return kind
        # A consistent flush-left edge: >=2 lines share it. Rejects centered
        # or ragged short runs, which are also indented.
        if sum(1 for x in x0s if abs(x - edge) <= 3) < 2:
            return kind
        return "blockquote"

    # -------------------------------------------------------- paragraphing
    def split_body_paragraphs(self, seg) -> list:
        """Cut the body at its own paragraph markers, and keep two stacked
        headings apart.

        This court numbers every paragraph ('¶ 12') and sets the marker AT the
        body rail with no first-line indent, so the shared indent-based
        paragraph splitter has nothing to see and consecutive numbered
        paragraphs were coming out welded into one block ('… (V.I. 2015)
        (citations omitted). ¶ 18 The three collateral-order factors …') — 42
        such run-ons across the four fixtures. The marker is the structure
        here, so split on it.

        Second pass: its section heads are centered and bold, one level under
        the next ('II. DISCUSSION' over 'A. Appellate Jurisdiction'). A
        centered run is normally a heading that WRAPPED — one heading, per
        CLAUDE.md 7 — so the shared stack-splitter deliberately leaves it
        joined. A line that stops less than half way across the measure cannot
        have wrapped, though, so a short centered line ends its heading.
        """
        groups = super().split_body_paragraphs(seg)
        out = []
        for grp in groups:
            for run in self._split_at_para_markers(grp):
                out.extend(self._split_short_centered(run))
        return out

    def _para_marker_number(self, line, rail):
        """The number of a '¶ N' paragraph marker standing at the body rail, or
        None.

        Two things wear this shape, and only the counter below tells them
        apart. The opinion's own markers run 1, 2, 3 … in order. A citation to
        a numbered paragraph of ANOTHER opinion ('… 2023 VI 12, ¶ 27
        (citations omitted)') is normally mid-line and excluded by the
        line-start test — but when the citation happens to wrap exactly at the
        pilcrow it lands at the rail looking identical ('¶ 18; Lowery v.
        Federal Exp. Corp., 426 F.3d 817 …'), and splitting there cuts a
        sentence in half.

        Two signals separate them. A marker's number is followed by SPACE and
        nothing else — a citation's is followed by its punctuation ('¶ 18;',
        '¶ 28.'). And the opinion's own markers only ever count UP, so a
        pilcrow naming a number already passed ('¶ 6 (citing Stiles v. Yob …',
        met after ¶ 7) is a citation.
        """
        if abs(line.get("x0", 0) - rail) > 3:
            return None
        text = self.line_plain_text(line).lstrip()
        if text[:1] != "¶":
            return None
        rest = text[1:].lstrip()
        digits = ""
        for ch in rest:
            if not ch.isdigit():
                break
            digits += ch
        if not digits:
            return None
        tail = rest[len(digits) :]
        if tail and not tail[:1].isspace():
            return None  # '¶ 18;' / '¶ 28.' — a citation, not a marker
        return int(digits)

    def _accept_para_marker(self, line, rail) -> bool:
        num = self._para_marker_number(line, rail)
        if num is None or num <= getattr(self, "_vi_para_no", 0):
            return False
        self._vi_para_no = num
        return True

    def _split_at_para_markers(self, grp) -> list:
        if not grp:
            return [grp]
        rail = min(l.get("x0", 0) for l in grp)
        # The group's own first line may itself open a paragraph; it cannot
        # start a new run, but it must still advance the counter.
        self._accept_para_marker(grp[0], rail)
        runs = [[grp[0]]]
        for line in grp[1:]:
            if self._accept_para_marker(line, rail):
                runs.append([line])
            else:
                runs[-1].append(line)
        return runs

    def _split_short_centered(self, grp) -> list:
        if len(grp) < 2:
            return [grp]
        width = getattr(self, "_page1_width", None) or 612.0
        measure = width - 2 * self.body_baseline_x0
        if not all(self.line_alignment(l, width) == "C" for l in grp):
            return [grp]
        runs = [[grp[0]]]
        for line in grp[1:]:
            prev = runs[-1][-1]
            if (prev["x1"] - prev["x0"]) < measure * 0.5:
                runs.append([line])
            else:
                runs[-1].append(line)
        return runs

    def _begins_paragraph_block(self, lines) -> bool:
        """A '¶ N' marker opens a paragraph, so a page that starts with one is
        not a wrapped continuation of the paragraph that ended the last."""
        if not lines:
            return False
        text = self.line_plain_text(lines[0]).lstrip()
        return text[:1] == "¶" and text[1:].lstrip()[:1].isdigit()

    # --------------------------------------------------------------- bylines
    def find_authors(self, all_segments) -> list:
        """Keep only bylines that fall BELOW the court's writing label.

        Every writing in this template is announced by a centered, fully bold
        label set two points larger than the body ('OPINION OF THE COURT',
        'CONCURRING OPINION', 'DISSENTING OPINION'); the author byline is the
        next thing on the page. Above that label there is nothing but
        headmatter — and the headmatter contains a byline look-alike, because
        the panel roster wraps and its second line can begin with a whole
        justice ('BEFORE: RHYS S. HODGE, Chief Justice; MARIA M. CABRET,
        Associate Justice; and / IVE ARLINGTON SWAN, Associate Justice.'). The
        family's 'before ' prefix test only sees the FIRST line, so the
        continuation was being read as the opinion author and the counsel
        block below it as that opinion's body (erbey).

        Using the label as the fence is structural and needs no knowledge of
        which justices sit: anything above it cannot be an author. When a
        document carries no such label (an order), nothing is filtered.
        """
        found = super().find_authors(all_segments)
        label = self._writing_label_index(all_segments)
        if label is None:
            return found
        return [i for i in found if i > label]

    def _writing_label_index(self, all_segments):
        """Index of the first centered bold over-size writing label, or None."""
        width = getattr(self, "_page1_width", None) or 612.0
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if len(seg) != 1:
                continue
            line = seg[0]
            size, _font, _bold = self.line_meta(line)
            if size < 13.0 or not self._line_all_bold(line):
                continue
            if self.line_alignment(line, width) != "C":
                continue
            text = self.line_plain_text(line).strip()
            if text and text == text.upper() and "OPINION" in text:
                return i
        return None

    # -------------------------------------------------------------- sign-off
    def _lift_signoff(self, doc) -> None:
        """Lift the two-part sign-off off the last opinion into
        ``doc.signature``.

        The court signs at the right margin — 'BY THE COURT:' over a
        conformed '/s/ Rhys S. Hodge', his printed name and his title — and
        the clerk attests below it at the body rail ('ATTEST: / DALILA
        PATTON, ESQ. / Clerk of the Court / By: /s/ … / Deputy Clerk II /
        Dated: …'). None of that is opinion text; it is the signature block,
        and the model keeps it read-only.

        Anchored on the 'BY THE COURT:' lead, which opens the block in all
        four fixtures, and confirmed by a conformed '/s/' inside the run so an
        ordinary sentence mentioning the phrase can never trigger the lift.
        """
        if not doc.opinions or doc.signature:
            return
        blocks = doc.opinions[-1].blocks
        start = None
        for i, b in enumerate(blocks):
            if self._plain_text(str(b.text or "")).lower().startswith(_COURT_LEAD):
                start = i
        if start is None:
            return
        run = blocks[start:]
        plain = [self._plain_text(str(b.text or "")) for b in run]
        if not any("/s/" in t for t in plain):
            return
        if not any(t.lower().startswith(_ATTEST_LEAD) for t in plain):
            return
        doc.opinions[-1].blocks = blocks[:start]
        doc.signature = [t for t in plain if t]

    @staticmethod
    def _plain_text(html: str) -> str:
        """Drop inline markup from a rendered block. Done with a depth counter
        rather than a pattern — per-court files stay regex-free."""
        out, depth = [], 0
        for ch in html:
            if ch == "<":
                depth += 1
            elif ch == ">":
                if depth:
                    depth -= 1
            elif not depth:
                out.append(ch)
        return "".join(out).strip()
