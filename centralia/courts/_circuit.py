"""U.S. Courts of Appeals — shared base for the numbered circuits + D.C. + Fed.

Ported from the proven ca1 ``circuit`` reference, re-expressed without regex.
Each circuit is its own subclass in its own file (ca1.py … cafc.py) with its
own column/gap/footnote tuning — circuits are non-monolithic.

Page-1 layout: centered banner 'United States Court of Appeals' / 'For the Nth
Circuit'; left docket 'No. 25-1160'; centered ALL-CAPS party block with role
lines; centered history 'APPEAL FROM THE UNITED STATES DISTRICT COURT ...';
bracketed trial-judge line; panel intro 'Before <judges>, Circuit Judges.';
attorneys; centered date. The opinion body opens INLINE with the author —
'AFRAME, Circuit Judge. This is an appeal...' (period form) or 'PAN, Circuit
Judge: ...' / 'Edith Brown Clement, Circuit Judge:' (colon form) or
'PER CURIAM. ...'. Federal bylines are NOT reliably bold, so detection is by
FORM: a name, a singular bench title (Circuit/District/Chief/Senior Judge),
then a '.'/':' terminator. The 'Before ... Judges.' roster (plural) is excluded.
"""

from __future__ import annotations

from typing import Optional

from ..base import _BENCH_WORDS
from ..models import Block
from .generic import GenericExtractor, _is_name

_BENCH = ("Judge", "Justice")

# The KINDS of document a circuit titles on its own front page. Closed list: a
# title has to name one of these, which is what keeps a leftover caps row (a
# counsel roll, an orphaned caption line, a bare attorney name) out of the field.
_DOC_TITLE_WORDS = (
    "judgment", "order", "opinion", "errata", "mandate", "notice", "decision",
    "rehearing", "petition", "per curiam", "summary", "memorandum", "dismissal",
    "certificate", "appealability", "remand", "correction", "amended",
    "nonprecedential", "precedential", "published", "publication",
)
# Lines whose leading word is a headmatter label, never the author.
_NON_AUTHOR = (
    "FILED",
    "OPINION",
    "SUMMARY",
    "COUNSEL",
    "NOTICE",
    "CERTIFIED",
    "PUBLISH",
    "DO NOT PUBLISH",
    "AMENDED",
    "RECOMMENDED",
    "UNITED STATES",
    "BEFORE ",
    "APPEAL FROM",
)


def _plain(text) -> str:
    """Markup-free text of a rendered row or block. A scanner rather than a
    pattern: this file stays regex-free."""
    out, depth = [], 0
    for ch in str(text or ""):
        if ch == "<":
            depth += 1
        elif ch == ">":
            if depth:
                depth -= 1
        elif not depth:
            out.append(ch)
    plain = "".join(out)
    # The rendered row carries HTML entities; the criteria are data, not
    # markup, so a firm named 'BAIRD & BAIRD' must not read as 'BAIRD &amp;
    # BAIRD' in the parsed panel.
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'")):
        if ent in plain:
            plain = plain.replace(ent, ch)
    return plain


def _is_typed_rule(text) -> bool:
    """A rule the page TYPES rather than draws ('___________')."""
    bare = _plain(text).strip()
    return bool(bare) and set(bare) <= set("_-—–= *")


def _is_writing_banner(text) -> bool:
    """The centred all-caps banner CA6 sets between two typed rules to announce
    the writing that follows ('OPINION', 'DISSENT', 'CONCURRENCE / DISSENT').

    Recognised by SHAPE, not by a list of names: short, every letter upper
    case, and no sentence punctuation. A list had to spell each variant and
    duly missed 'CONCURRENCE / DISSENT', which sets spaces around the slash on
    part of the corpus and closes it up on the rest."""
    bare = " ".join(_plain(text).split())
    if not bare or len(bare) > 40:
        return False
    # A STRUCTURAL MARKER IS NOT A BANNER. '__DIVIDER__' answers the shape test
    # exactly — short, no sentence punctuation, every letter upper case — so it
    # was being rehomed into the opinion and rendered as '<h3>__DIVIDER__</h3>'
    # at the head of the majority (ca1). Markers and typed rules are layout.
    if bare.startswith("__") or _is_typed_rule(bare):
        return False
    if any(ch in bare for ch in ".,;:"):
        return False
    letters = [ch for ch in bare if ch.isalpha()]
    return bool(letters) and all(ch.isupper() for ch in letters)


def _page_of(ln) -> int:
    chars = ln.get("chars") or [{}]
    return chars[0].get("page_number", 1) or 1


def _key(obj) -> str:
    """Whitespace-insensitive text key, for lining an emitted headmatter row
    back up with the source line it came from."""
    return "".join(str(obj.get("text") or "").split())


def _plain_cell(cell) -> str:
    text = cell.get("h", "") if isinstance(cell, dict) else cell
    return _plain(text)


def _merge_cell(a, b):
    """Append cell ``b``'s text to cell ``a``, keeping ``a``'s shape."""
    def text_of(c):
        return str(c.get("h", "") if isinstance(c, dict) else c).strip()

    joined = (text_of(a) + " " + text_of(b)).strip()
    if isinstance(a, dict):
        out = dict(a)
        out["h"] = joined
        return out
    return joined


# ---------------------------------------------------------------------------
# HEADMATTER CRITERIA — the vocabulary the circuits actually print.
# Plain string prefixes, not regex (project rule): these are phrases, and a
# phrase list is readable where a pattern would not be.
# ---------------------------------------------------------------------------
_HISTORY_OPENERS = (
    "appeal from", "appeals from", "on appeal from",
    "petition for review", "petitions for review",
    "on petition for review", "on petitions for review",
    "review of", "on remand from", "appeal of",
    # A mandamus record comes from a court too, and names it the same way, as
    # does an application for leave to appeal ('Application for Certificate of
    # Appealability from the United States District Court for the Northern
    # District of Texas USDC No. 4:09-CV-160').
    "on petition for writ", "petition for writ",
    # ...and the court may set an article in it ('Petition for a Writ of
    # Mandamus'), which no prefix without one will match.
    "on petition for a writ", "petition for a writ",
    "application for certificate", "application for leave",
)
# Markers that open the LOWER court's own docket inside a history row.
_LOWER_DOCKET_MARKERS = ("D.C. Docket No", "Agency No", "USDC No", "D.C. No")
# How a caption zone announces itself.
_STATUS_WORDS = (
    "appellant", "appellee", "petitioner", "respondent", "plaintiff",
    "defendant", "debtor", "intervenor", "amicus", "versus",
    "movant", "applicant", "claimant",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# HOW AN APPEARANCE ANNOUNCES ITSELF. Counsel is claimed by POSITIVE match on
# these, never as a catch-all for whatever else is in the headmatter — used as
# a dumping ground it swallowed case summaries, caption notes and clerk's
# instructions alike. A court whose convention differs overrides ``_tail_kind``.
_COUNSEL_MARKERS = (
    "argued the cause", "argued for", "argued on behalf",
    "on the brief", "on the briefs", "on brief", "on briefs",
    "counsel for", "attorney for", "attorneys for", "pro se",
    "for appellant", "for appellants", "for appellee", "for appellees",
    "for petitioner", "for petitioners", "for respondent", "for respondents",
    "for plaintiff", "for plaintiffs", "for defendant", "for defendants",
    "for amicus", "for amici", "for intervenor", "for intervenors",
    "for the appellant", "for the appellee", "for the petitioner",
    "for the respondent", "for movant", "for the government",
)
# ...or by a heading that names the party the block acts for.
_COUNSEL_OPENERS = ("argued:", "on brief:", "on the brief:", "counsel:")
# The labels a circuit puts in front of a date. Longest first so 'Argued and
# Submitted' wins over 'Submitted'.
_DATE_LABELS = (
    "argued and submitted", "submitted on briefs", "decided and filed",
    "argued", "submitted", "reargued", "decided", "filed", "entered",
)
# A publication flag is a SHORT ALL-CAPS row that says so. Matched on the stem
# so PUBLISH / PUBLISHED / UNPUBLISHED / FOR PUBLICATION / NOT FOR PUBLICATION
# and NONPRECEDENTIAL all read alike without spelling each variant.
_PUBLICATION_STEMS = ("publish", "publication", "precedential")
_MONTHS = (
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
)


class FederalCircuitBase(GenericExtractor):
    # Federal bodies are ~1.5-spaced. Per-circuit subclasses override these.
    gap_tight_max = 10.0
    gap_single_max = 22.0
    gap_double_max = 32.0
    body_baseline_x0 = 72.0
    circuit_phrase = ""

    author_titles = (
        "Chief Circuit Judge",
        "Senior Circuit Judge",
        "Circuit Judge",
        "District Judge",
        "Chief Judge",
        "Senior Judge",
        "Judge",
        "Circuit Justice",
        "Justice",
    )

    # Pages 2+ open with a centered 'No. <docket>' running header at top~75;
    # drop content above this. Subclasses with no such header lower it.
    page2_header_cutoff = 95.0

    # The clerk's e-filing stamp on page 1 (the top-right 'FILED / <court> /
    # <date> / <clerk name> / Clerk of Court' block) is furniture, not headmatter.
    # A circuit identifies it by FONT + SIZE: the stamp is set in a bold face at a
    # size the centered court banner does not use, so a (font, size) match drops
    # the stamp while leaving the banner — and splits the one line that merges
    # the banner's 'FOR THE TENTH CIRCUIT' (size 13) with the stamp's 'Clerk of
    # Court' (size 12). Left None on circuits not yet tuned (no drop). The match
    # is on the font-name SUFFIX so subset prefixes ('YRKGHW+...') still match.
    efile_stamp_font = None
    efile_stamp_size = None

    # The RUNNING HEAD on continuation pages ('No. 25-1802 Ross v. Robinson …
    # Page 2' on CA6, '2 USA V. SANCHEZ' on CA9) is identified furniture, so it
    # belongs in ``dropped`` — not deleted by ``page2_header_cutoff``, which is a
    # blanket y bound that also eats the first real line of the page whenever a
    # circuit's head sits higher than the family default assumes.
    #
    # A circuit opts in by naming the band the head occupies (and, if its type is
    # distinctively small, the maximum size). ``page2_header_cutoff`` can then be
    # dropped to the page edge, so the only thing removed above the body is the
    # head itself — and it is recorded. Left None = off (the family default
    # cutoff still applies, unchanged for every circuit that does not opt in).
    running_head_max_top = None
    running_head_max_size = None  # None = any size within the band
    running_head_first_page = 2  # 1 where the head is printed on page 1 too

    def extract(self, pdf_path):
        self._furniture_dropped = []
        self._furniture_merged = None
        doc = super().extract(pdf_path)
        self._merge_furniture(doc)
        doc = self._rehome_writing_banners(doc)
        # Dissect the headmatter LAST, once the rows are final — the banner
        # rehoming above still moves rows in and out of the summary. Runs for
        # every circuit that sets ``parse_criteria_enabled``; the method is a
        # no-op otherwise, so a court opts in with one flag and no override.
        self.parse_criteria(doc)
        return doc

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Restore the front matter's own grouping and spacing."""
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        return self._join_tight_rows(result, headmatter_segs)

    def _rehome_writing_banners(self, doc):
        """Move a writing banner onto the writing it introduces.

        'DISSENT' is set at the head of the dissent, but it is the LAST thing
        on the majority's final page, so it was closing the majority instead of
        opening the dissent — the banner rendered above the majority's own
        footnotes, and then the dissent began again underneath it. The same
        applies to 'CONCURRENCE' between writings and to the 'OPINION' banner
        that trails the headmatter."""
        banner_of = _is_writing_banner

        for index, opinion in enumerate(doc.opinions):
            while opinion.blocks and banner_of(opinion.blocks[-1].text):
                block = opinion.blocks.pop()
                if index + 1 < len(doc.opinions):
                    doc.opinions[index + 1].blocks.insert(0, block)
        # The majority's own banner closes the headmatter for the same reason.
        if doc.opinions and doc.summary:
            trailing = []
            while doc.summary:
                row = doc.summary[-1]
                if isinstance(row, dict):
                    break
                bare = _plain(row).strip()
                if not bare or bare == "__DIVIDER__" or _is_typed_rule(row):
                    trailing.append(doc.summary.pop())
                    continue
                if banner_of(row) and (
                    any(_is_typed_rule(t) for t in trailing) or not trailing
                ):
                    # A banner is either FLANKED by typed rules, or it is the
                    # LAST content row of the headmatter — a banner in that
                    # position introduces the opinion by definition. 'COUNSEL'
                    # matches the all-caps shape too but is never last: its own
                    # block always follows it.
                    trailing.append(doc.summary.pop())
                    break
                break
            else:
                trailing = []
            if any(banner_of(r) for r in trailing):
                # The banner and the RULES THAT FLANK IT are one unit — the
                # page draws rule / OPINION / rule to open the writing — so
                # the whole run moves together. This branch used to insert the
                # banner alone and discard the rest, which lost rules the page
                # really drew; putting them back in the headmatter instead
                # would leave it ending on two orphan rules. Blank rows are
                # spacing against the headmatter above and do not travel.
                kept = []
                for row in trailing:  # reversed order: rebuilding downward
                    if not _plain(row).strip():
                        continue
                    if banner_of(row):
                        doc.opinions[0].blocks.insert(
                            0, Block(kind="heading", text=str(row))
                        )
                    elif _is_typed_rule(row):
                        # A rule the page TYPED is literal text and reads the
                        # same inside the opinion.
                        doc.opinions[0].blocks.insert(
                            0, Block(kind="p", text=str(row))
                        )
                    else:
                        # '__DIVIDER__' marks a rule the page DREW. It is a
                        # headmatter marker with no meaning inside an opinion —
                        # moved there it rendered as the literal text
                        # '<p>__DIVIDER__</p>' (ca3) — so it stays put.
                        kept.append(row)
                doc.summary.extend(reversed(kept))
            else:
                doc.summary.extend(reversed(trailing))
        return doc

    def _join_column(self, cells, headmatter_segs, side):
        """Fold a party name that wraps back into ONE caption cell.

        A caption column is not a list of lines, it is a list of parties and
        their status labels. 'ELIZABETH K. KERWIN, Regional Director Seventh /
        Region of the National Labor Relations Board on / behalf of National
        Labor Relations Board,' is a single party set over three lines and was
        coming out as three cells.

        The party runs flush at the column's own left edge; the status label
        under it ('Petitioner-Appellee,') is indented and italic. So the same
        test as the rows above: flush and single-spaced continues the unit,
        indented starts a new one."""
        from collections import Counter

        lines = sorted(
            (
                ln
                for seg in headmatter_segs
                for ln in seg
                if ln.get("_caption_col") == side and (ln.get("text") or "").strip()
            ),
            key=lambda ln: ln.get("top", 0),
        )
        if len(lines) < 2 or len(cells) < 2:
            return cells
        edge = Counter(round(ln.get("x0", 0)) for ln in lines).most_common(1)[0][0]
        sizes = [self.line_meta(ln)[0] for ln in lines if self.line_meta(ln)[0]]
        tight = (Counter(sizes).most_common(1)[0][0] if sizes else 12) * 1.4

        # Cells and lines run in the same order once the blanks are set aside.
        filled = [i for i, c in enumerate(cells) if _plain_cell(c).strip()]
        if len(filled) != len(lines):
            return cells
        drop = set()
        for pos in range(1, len(lines)):
            prev, cur = lines[pos - 1], lines[pos]
            flush = round(cur.get("x0", 0)) <= edge + 4
            gap = cur.get("top", 0) - prev.get("top", 0)
            if flush and 0 < gap <= tight:
                target = filled[pos - 1]
                while target in drop:
                    target -= 1
                cells[target] = _merge_cell(cells[target], cells[filled[pos]])
                drop.add(filled[pos])
        return [c for i, c in enumerate(cells) if i not in drop]

    def _join_tight_rows(self, result, headmatter_segs):
        """Join headmatter rows the page sets as ONE unit.

        CA6's front matter is a sequence of groups separated by a full blank
        line: the lower court and its docket/trial-judge line are one unit, the
        panel roster is one unit however many lines it wraps to, and each date
        stands alone. Single leading (≈13.8pt at 12pt type) means the same
        unit; a real gap runs 18–26.

        The base already merges tight runs, but only while the alignment holds.
        The lower-court pair flips from 'L' to 'C' between its two lines — the
        docket line is narrow enough to read as centered — so the run broke
        there and the unit came out as two rows."""
        rows = result.get("summary", [])
        lines = [
            ln
            for seg in headmatter_segs
            for ln in seg
            if (ln.get("text") or "").strip()
        ]
        if len(lines) < 2 or not rows:
            return result
        # Measure against the document's own TYPE SIZE, not its gap frequency.
        # Single leading runs about 1.15x the size and a real separation about
        # 2x, so 1.4x splits them with room on both sides (13.8 and 15.7 join;
        # 17.9 and 25.5 do not). The modal GAP fails here: in a document whose
        # front matter is mostly separated rows the commonest gap IS the double
        # leading, which made the threshold swallow the dates and the panel
        # line into the lower-court row.
        from collections import Counter

        sizes = [
            round(self.line_meta(ln)[0], 1)
            for ln in lines
            if self.line_meta(ln)[0]
        ]
        if not sizes:
            return result
        size = Counter(sizes).most_common(1)[0][0]

        # LEADING IS MEASURED PER FACE, not once per document. A page mixes
        # faces — a 20pt Old English banner over 13pt Palatino dates over an
        # 11.5pt caption — and each sets its own single leading, so one
        # document-wide threshold either splits the banner or runs the dates
        # together. For each face, the smallest gap that recurs between its own
        # consecutive lines IS its single leading.
        def face(ln):
            metric = self.line_meta(ln)
            return (metric[1], round(metric[0], 1))

        by_face = {}
        # A TYPED RULE IS NOT TYPE. It is set in whatever face is to hand — CA11
        # draws '____________________' in the same 14pt Dante as the party
        # names — but it is a divider, so the space around it is a component
        # separation, not leading. Measuring it made 33.8pt the "single
        # leading" of the caption face, which put the blank threshold at 54pt
        # and suppressed every real blank in the caption.
        run = sorted(
            (ln for ln in lines if not _is_typed_rule(self.line_plain_text(ln))),
            key=lambda ln: (_page_of(ln), ln.get("top", 0)),
        )
        for a, b in zip(run, run[1:]):
            if face(a) != face(b) or _page_of(a) != _page_of(b):
                continue
            gap = round(b.get("top", 0) - a.get("top", 0), 1)
            if 0 < gap < 60:
                by_face.setdefault(face(b), []).append(gap)
        leading = {
            f: Counter(g).most_common(1)[0][0] for f, g in by_face.items() if g
        }

        def bounds(a, b):
            """(tight, blank) for this pair, from the face they share."""
            lead = leading.get(face(b)) or leading.get(face(a))
            if lead is None:
                metric = max(self.line_meta(a)[0] or size, self.line_meta(b)[0] or size)
                lead = metric * 1.2
            return lead * 1.25, lead * 1.6

        page_of = _page_of
        joinable, spaced = {}, set()
        ordered = sorted(lines, key=lambda ln: (page_of(ln), ln.get("top", 0)))
        # The FIRST LINE INDENT is what opens a new paragraph, and it survives
        # a page break where the vertical gap does not: the counsel block runs
        # flush at the body margin and the attribution that follows it is
        # indented, whether they sit on the same page or not.
        margins = Counter(round(ln.get("x0", 0)) for ln in ordered)
        body_x0 = margins.most_common(1)[0][0] if margins else 0
        for a, b in zip(ordered, ordered[1:]):
            # An indent only means "new paragraph" for a line set FLUSH to a
            # margin. A centred line's x0 is a function of how long it is — the
            # lower court and its docket line centre at 116 and 173 against a
            # body margin of 72 — so reading that as an indent split the unit
            # in two. Centred lines are judged on the gap alone.
            centred = self.line_alignment(b, 612) == "C"
            indented = not centred and round(b.get("x0", 0)) > body_x0 + 6
            if page_of(b) != page_of(a):
                # A paragraph interrupted by the page ending is still one
                # paragraph. Ordering by ``top`` alone put page 2's first line
                # ABOVE page 1's last, so the gap between them was meaningless
                # and the counsel block came out as two rows.
                # A paragraph that really continues over the break does NOT
                # end in a full stop. Requiring that stopped a completed
                # caption row being welded to the next page's running header
                # ('Defendant.' + '2 Opinion of the Court 24-13309'), which
                # also destroyed the header — ca11 recognises it on its own
                # line but not once merged, so it never reached the Removed
                # box and rode into the caption instead.
                closed = _plain(a.get("text") or "").rstrip().endswith((".", ":", ";"))
                if not indented and not closed:
                    joinable[_key(b)] = _key(a)
                else:
                    # A new paragraph that happens to open the next page still
                    # needs its blank line: the vertical gap is meaningless
                    # across the break, so the indent alone has to carry both
                    # the split AND the spacing.
                    spaced.add(_key(b))
                continue
            gap = b.get("top", 0) - a.get("top", 0)
            tight, blank = bounds(a, b)
            # A change of face IS the component boundary — the banner, the
            # dates and the caption are set in different types, and no gap
            # threshold has to decide between them.
            if face(a) != face(b):
                if gap >= blank:
                    spaced.add(_key(b))
                continue
            # OPPOSITE MARGINS cannot be one unit. CA11 pins the status labels
            # to the right margin and opens the next party at the left, in the
            # same italic face at single leading, so the gap test welded
            # 'Cross-Appellee,' to 'versus'. Only the L/R flip is decisive:
            # an L-to-C flip is the case this method exists to JOIN (a docket
            # line short enough to read as centred under its lower court), and
            # a centred line's x0 is a function of its length, not its margin.
            if {
                self.line_alignment(a, 612),
                self.line_alignment(b, 612),
            } == {"L", "R"}:
                if gap >= blank:
                    spaced.add(_key(b))
                continue
            if indented:
                # A new paragraph, however tight the leading above it.
                if gap >= blank:
                    spaced.add(_key(b))
                continue
            if 0 < gap <= tight:
                joinable[_key(b)] = _key(a)
            elif gap >= blank:
                spaced.add(_key(b))

        def is_rule(text):
            """A typed rule ('_________________') or a marker row. It separates
            components and must never be joined to one — joining swallowed the
            rule into the heading below it ('_________________ COUNSEL') and
            absorbed whole rows such as the panel line."""
            bare = _plain(text).strip()
            return not bare or bare.startswith("__") or _is_typed_rule(text)

        line_keys = sorted(
            (_key(ln) for ln in ordered), key=len, reverse=True
        )
        out, prev_key, prev_index = [], None, None
        # Everything below the first row may take a blank. The gate used to be
        # "only after a __caption__ block", which was a ca6 patch to stop a
        # blank splitting the court banner — but courts that keep their parties
        # as flat rows (ca1, ca2) never build a caption block at all, so the
        # gate silently disabled spacing for the whole court.
        opened = not self.banner_zone_gates_blanks
        for row in rows:
            if isinstance(row, dict) and row.get("__caption__"):
                opened = True
            if not isinstance(row, str) or not row.strip() or is_rule(row):
                if isinstance(row, str) and _plain(row).strip():
                    opened = True          # a divider closes the banner zone
                out.append(row)
                prev_key = prev_index = None
                continue
            key = _key({"text": _plain(row)})
            # A row is usually SEVERAL source lines (the base merged them), so
            # its own key matches no single line. Identify the row by the line
            # its text starts with, and remember the line it ends with, so a
            # multi-line row can still be joined to the one before it.
            first_key = next(
                (k for k in line_keys if k and key.startswith(k)), key
            )
            last_key = next(
                (k for k in line_keys if k and key.endswith(k)), key
            )
            if (
                prev_index is not None
                and joinable.get(first_key) == prev_key
                and isinstance(out[prev_index], str)
            ):
                out[prev_index] = out[prev_index].rstrip() + " " + row.lstrip()
                prev_key = last_key
                continue
            # The page sets a blank line here; keep it so the groups read apart.
            # Not in the BANNER ZONE above the first divider or caption: the
            # court's name is routinely set in two different sizes ('UNITED
            # STATES COURT OF APPEALS' at 15pt over 'FOR THE SIXTH CIRCUIT' at
            # 11.5pt), so the face test reads it as two components and a blank
            # would cut the court's name in half.
            if opened and first_key in spaced and out and out[-1] != "":
                out.append("")
            out.append(row)
            prev_index, prev_key = len(out) - 1, last_key
        result["summary"] = out
        return result


    # ==================================================================
    # HEADMATTER CRITERIA
    # ==================================================================
    # Every circuit rules its headmatter into ZONES and prints the same kinds
    # of thing in them — court, docket, case caption, prior history, panel,
    # counsel, date. The zones repeat where two appeals are heard together, so
    # docket/caption/history are grouped into a CASE rather than flattened.
    #
    # What differs between circuits is which zones are present, whether the
    # walls are typed rules or drawn dividers, and whether a zone carries one
    # field or several — not the vocabulary. So the walk lives here and a court
    # overrides only its deltas.
    parse_criteria_enabled = False
    # Does this court print the 'Counsel for Appellant' label BELOW the names
    # it labels (CA3)? Then a labelled row claims the unrecorded rows above it.
    counsel_label_trails = False
    # Does this court print a case summary ahead of the opinion? Only CA2 does,
    # so only CA2 records one; elsewhere the field stays absent rather than
    # collecting prose that happened not to match anything else.
    criteria_has_summary = False
    # Lift the publication flag OUT of the rendered headmatter (CA11 prints
    # 'FOR PUBLICATION' above the caption, where it is a flag, not caption
    # text). Only safe because the criteria panel renders it — see audit.
    criteria_lift_publication = False
    # Does the court set its own name over two rows in two different sizes?
    # Then no blank may be kept until the banner zone closes, or the name is
    # cut in half. CA7 sets its name, its city and everything below it with
    # real space between each — and draws no rule and builds no caption block
    # above them, so the zone never closed and the whole headmatter came out
    # with its vertical rhythm flattened.
    banner_zone_gates_blanks = True
    # Does this court set the document's own title in the headmatter (CA10's
    # ruled 'ORDER DENYING CERTIFICATE OF APPEALABILITY' band)? Where it does
    # not, the slot must stay shut: CA4 sets an amici roll in its own ruled
    # band inside the caption, which answers the same test and was published
    # as the title instead of joining the case name it belongs to.
    criteria_has_title = True
    # Does a counsel band run from its opener to the next rule (CA4 announces
    # the appearances with 'ARGUED:' / 'ON BRIEF:' and rules the band off)?
    # Then every row inside it is counsel, however little the row says for
    # itself — and nothing outside such a band ever is.
    counsel_runs_to_rule = False
    # Do the history/dates/panel below a consolidated caption belong to EVERY
    # case (CA4 states them once for all of them)? Off elsewhere, where each
    # case carries its own.
    criteria_shared_tail = False
    # Does this court run the roster onto the end of another row, or the
    # origin onto the end of the caption's last row? See the two split hooks.
    roster_can_share_row = False
    history_can_share_row = False

    def _zones(self, rows):
        """Split headmatter rows into the zones the page rules them into.

        A typed rule and a drawn ``__DIVIDER__`` are both walls; blank rows are
        spacing and never open a zone."""
        zones, cur = [], []
        for row in rows:
            if isinstance(row, dict):
                cur.append(row)
                continue
            bare = _plain(row).strip()
            if not bare:
                continue
            if _is_typed_rule(row) or bare == self.HEADMATTER_DIVIDER:
                if cur:
                    zones.append(cur)
                    cur = []
                continue
            cur.append(row)
        if cur:
            zones.append(cur)
        return zones

    @staticmethod
    def _zone_texts(zone):
        out = []
        for row in zone:
            if isinstance(row, dict):
                for side in ("left", "right"):
                    for cell in row.get(side) or []:
                        text = _plain(cell).strip()
                        if text:
                            out.append(text)
                continue
            text = _plain(row).strip()
            if text:
                out.append(text)
        return out

    # How this court opens its panel roster. CA2 prints 'PRESENT:' on a summary
    # order where every other circuit prints 'Before'.
    panel_openers = ("before", "present:", "present ")

    @classmethod
    def _is_docket_text(cls, text):
        """A docket row.

        Usually 'No. 25-1448' / 'Nos. 24-2990 and 24-3198'. The Federal Circuit
        prints the number BARE on its own row ('2025-1317'), so a row that is
        nothing but a docket token counts too."""
        if text.startswith(("No. ", "Nos. ", "No ", "Nos ")):
            return True
        # CA6 says 'Case No. 25-3102' — the same row with the word in front of
        # it. Without this the docket went unread on every record that used it.
        if text.startswith(("Case No", "Case Nos")):
            return True
        tokens = text.split()
        if not tokens or len(tokens) > 3:
            return False
        return all(cls._is_docket_token(t) for t in tokens)

    @staticmethod
    def _docket_core(token):
        """The token stripped to its numeric body, or None.

        CA2 appends the case type to its docket ('25-2417-cv', '24-1510-ag'),
        so the trailing alpha part comes off before the digit test — without
        it the docket printed inside CA2's caption row was never recognised."""
        core = token.strip(",;.()")
        if not core or not any(ch.isdigit() for ch in core):
            return None
        parts = core.split("-")
        while parts and parts[-1].isalpha():
            parts.pop()
        if not parts:
            return None
        body = "".join(parts).replace("/", "").replace(";", "")
        if not body.isdigit():
            return None
        return core if ("-" in core or "/" in core) else None

    @classmethod
    def _is_docket_token(cls, token):
        return cls._docket_core(token) is not None

    def _is_court_banner(self, text):
        """A row that names the court itself.

        The banner is set in caps on several circuits, so the party-roll test
        below would claim it — and on CA2's summary order, where the caption
        opens with a bare roll of names, that put 'UNITED STATES COURT OF
        APPEALS FOR THE SECOND CIRCUIT' at the head of the case name."""
        low = " ".join(text.lower().split())
        # A BANNER IS A NAME, NOT A SENTENCE. CA2's convening preamble ('At a
        # stated term of the United States Court of Appeals for the Second
        # Circuit, held at the Thurgood Marshall United States Courthouse...')
        # names the court inside a paragraph, and matching on the phrase alone
        # pulled the whole paragraph into the court field.
        if len(low) > 80:
            return False
        if "court of appeals" in low:
            return True
        phrase = (self.circuit_phrase or "").lower()
        return bool(phrase) and low.endswith(phrase)

    @staticmethod
    def _is_title_text(text) -> bool:
        """True when a caps row can be the DOCUMENT'S OWN TITLE.

        The caps test alone cannot tell a title from a roll of names, so any caps
        row left loose after the caption became one: cafc filed a counsel roll
        ('JOHNSON BILDERBECK, ANDREW GISH, CONOR MCDONOUGH.') and an orphaned
        caption row ('TINECO INTELLIGENT TECHNOLOGY CO., LTD., …') as titles.

        A title NAMES A KIND of document and is a phrase — 'JUDGMENT', 'ORDER
        DENYING CERTIFICATE OF APPEALABILITY', 'ON PETITIONS FOR REHEARING'. A
        roll of names is a LIST, and a list carries commas. So the comma is the
        discriminator, and it also keeps a title short by construction.

        A LONE name carries no comma either ('MICHELLE W. KLANCNIK.'), and is
        told apart by its INITIAL: a middle initial belongs to a person and never
        appears in the name of a document.

        A bare name can survive both of those ('KATHERINE MICHELLE SMITH.'), so
        the last requirement is positive: a title has to name a KIND of document.
        That vocabulary is small and closed, and demanding it is what stops the
        field being filled by whatever caps row happened to be left over."""
        if "," in text or len(text.split()) > 12:
            return False
        for token in text.split():
            if len(token) == 2 and token[0].isalpha() and token[1] == ".":
                return False
        low = text.lower()
        return any(word in low for word in _DOC_TITLE_WORDS)

    @staticmethod
    def _is_party_text(text):
        """A caption row that names PARTIES rather than describing them.

        The courts set party names in caps and everything around them in
        ordinary case, so the ratio settles it where a status word is absent:
        CA2's summary order opens its caption with a bare roll of names
        ('SALWA AHMED ALSONIDAR, ERJUWAN LUFT ALI ALSONIDAR, ...') that carries
        no 'Plaintiff'/'Appellant' of its own, while the counsel block below it
        starts in caps and then falls into prose ('FOR PLAINTIFFS-APPELLANTS:
        JULIE A. GOLDBERG, Goldberg & Associates, P.C., Melvindale')."""
        letters = [c for c in text if c.isalpha()]
        # 'JOHN BAL' is seven letters. An eight-letter floor read it as prose
        # and filed the plaintiff under counsel, where he then appeared twice.
        if len(letters) < 6:
            return False
        upper = sum(1 for c in letters if c.isupper())
        return upper / len(letters) >= 0.85

    @classmethod
    def _split_publication(cls, text):
        """(flag, rest) when the flag is printed ON the banner row.

        CA10 sets 'PUBLISH' and the court's name on the same line, and the
        headmatter grouping keeps them as one row — so the whole-row test never
        fires and the flag was recorded on only the handful of files where the
        two happened to stay apart."""
        tokens = text.split()
        for i, token in enumerate(tokens[:3]):
            if any(stem in token.lower() for stem in _PUBLICATION_STEMS):
                rest = " ".join(tokens[i + 1 :]).strip()
                return " ".join(tokens[: i + 1]), (rest or None)
        return None, text

    @classmethod
    def _split_caption_dockets(cls, text):
        """(caption text, docket text) for a caption row carrying dockets.

        A consolidated record prints its member numbers down the caption's own
        'v.' column, tagged with their role:

            v. 23-258 (L)
            23-263 (CON)
            23-444 (CON)

        Those are docket numbers, not parties, and left in place they run
        through the middle of the case name."""
        tokens = text.split()
        kept, dockets = [], []
        for token in tokens:
            bare = token.strip("();,")
            if cls._is_docket_token(token):
                dockets.append(token)
            elif dockets and bare.upper() in ("L", "CON", "XAP", "AP"):
                dockets[-1] = f"{dockets[-1]} {token}"
            else:
                kept.append(token)
        return " ".join(kept).strip(), " ".join(dockets).strip()

    @classmethod
    def _publication_flag(cls, text):
        """The publication flag, if this row is one.

        By STEM, not by a list of spellings: PUBLISH (CA10), PUBLISHED /
        UNPUBLISHED (CA4), FOR PUBLICATION / NOT FOR PUBLICATION (CA11) and
        NONPRECEDENTIAL all share a stem, and every one of them is a short
        all-caps row that says nothing else."""
        bare = " ".join(text.split())
        if not bare or len(bare.split()) > 4:
            return None
        letters = [c for c in bare if c.isalpha()]
        if not letters or not all(c.isupper() for c in letters):
            return None
        low = bare.lower()
        return bare if any(stem in low for stem in _PUBLICATION_STEMS) else None

    @classmethod
    def _split_labelled_dates(cls, text, want_tail=False):
        """{'argued': 'October 28, 2025', 'decided': 'April 29, 2026'}.

        A circuit runs its dates together on one row under their own labels —
        'Argued: October 28, 2025 Decided: April 29, 2026', 'Submitted:
        January 13, 2026 Filed: May 18, 2026', 'ARGUED SEPTEMBER 17, 2025 —
        DECIDED MAY 1, 2026'. Find each label, then read to the next one."""
        # A DATE ROW IS NOT A PARAGRAPH. Every one of these labels is an
        # ordinary English word, and 'filed' inside prose ('...the petition he
        # filed on November 12, 2018, asserts that...') was being read as the
        # filing date of the case. A row that carries dates is short.
        if len(text) > 160:
            return ({}, "") if want_tail else {}
        low = text.lower()
        found = []
        for label in _DATE_LABELS:
            start = 0
            while True:
                at = low.find(label, start)
                if at < 0:
                    break
                # A label must start a word, not sit inside one...
                after = low[at + len(label) : at + len(label) + 1]
                # ...and it must not be a BRACKETED MARKER. CA3 tags the
                # advocate who argued inside the appearance itself ('Christian
                # T. Haugsby [ARGUED] Carlo D. Marchioli'); read as a date
                # label it took the rest of the row for its value.
                if (at == 0 or not low[at - 1].isalnum()) and after not in ("]", ")"):
                    found.append((at, label))
                start = at + len(label)
        if not found:
            return ({}, "") if want_tail else {}
        # LONGEST LABEL WINS AT THE SAME POSITION. 'Argued and Submitted' and
        # 'Argued' both start at 0, and taking the short one left the date
        # under 'submitted' with 'and' recorded as the argued date.
        found.sort(key=lambda pair: (pair[0], -len(pair[1])))
        # Drop a label that is contained in a longer one starting at the same
        # place ('submitted' inside 'argued and submitted').
        picked = []
        for at, label in found:
            if picked and at < picked[-1][0] + len(picked[-1][1]):
                continue
            picked.append((at, label))
        out = {}
        tail = ""
        for i, (at, label) in enumerate(picked):
            end = picked[i + 1][0] if i + 1 < len(picked) else len(text)
            seg = text[at + len(label) : end]
            # Tokens WITH their offsets, so what the date does not use can be
            # handed back to the caller instead of being swallowed.
            toks, j = [], 0
            while j < len(seg):
                if seg[j].isspace() or seg[j] in ":—–-,;.()[]":
                    j += 1
                    continue
                k = j
                while k < len(seg) and not seg[k].isspace():
                    k += 1
                toks.append((seg[j:k], j, k))
                j = k
            if not toks:
                continue
            words = [t[0].strip(".,;:()[]").lower() for t in toks]
            # A MONTH IS A WORD, NOT A SUBSTRING. 'Carlo D. Marchioli' contains
            # 'march', which passed a plain `in` test and published a counsel
            # name as the date argued. Read the value's own tokens.
            month_at = next((n for n, w in enumerate(words) if w in _MONTHS), None)
            if month_at is None:
                # No month name: only a short numeric run is a date
                # ('5/12/26'), never a sentence.
                digits = sum(c.isdigit() for t in toks for c in t[0])
                if len(toks) > 3 or digits < 4:
                    continue
                start, stop = 0, len(toks)
            else:
                # A DATE VALUE BEGINS WITH ITS DATE. CA3 states the authority
                # for deciding on the briefs between the label and the day
                # ('Submitted Pursuant to Third Circuit L.A.R. 34.1(a) on
                # February 3, 2025'); kept whole, the field read as a sentence.
                # Cut to the month — unless a bare number precedes it, which is
                # the day of a '3 February 2025'.
                start = month_at
                if month_at and words[month_at - 1].isdigit():
                    start = month_at - 1
                # ...AND IT ENDS AT ITS YEAR. CA3 runs the filing date and the
                # first appearance together on one row ('(Opinion filed: April
                # 28, 2026) Joel S. Sansone (Argued) Law Offices of Joel
                # Sansone ...'), and a value read to the end of the row
                # published the whole counsel block as the date filed.
                stop = len(toks)
                for n in range(start, min(len(toks), start + 4)):
                    if sum(c.isdigit() for c in toks[n][0]) == 4:
                        stop = n + 1
                        break
            value = seg[toks[start][1] : toks[stop - 1][2]].strip(" :—–-,;.()[]")
            if not value:
                continue
            out[label.replace(" ", "_")] = value
            rest = seg[toks[stop - 1][2] :].strip(" :—–-,;.()[]\t")
            tail = rest if i == len(picked) - 1 else ""
        return (out, tail) if want_tail else out

    @classmethod
    def _is_date_text(cls, text):
        """A bare filing/decision date row ('May 16, 2026')."""
        tokens = text.replace(",", " ").split()
        if not (2 <= len(tokens) <= 4):
            return False
        return (
            tokens[0].lower() in _MONTHS
            and tokens[-1].isdigit()
            and len(tokens[-1]) == 4
        )

    @classmethod
    def _zone_kind(cls, texts, first=False):
        """What a zone IS, from the shape of its own rows.

        Read per zone rather than by position: a consolidated appeal repeats
        the docket/caption/history group, and a court that omits a zone would
        otherwise shift every later zone's meaning by one."""
        if not texts:
            return None
        head = texts[0]
        low = head.lower().strip()
        # CA1 sets 'Before' alone on its own row above the roster, CA11 runs
        # the roster straight on, CA2 uses 'PRESENT:' — accept all of them.
        if any(low == o.strip() or low.startswith(o) for o in cls.panel_openers):
            return "panel"
        if low.startswith(_HISTORY_OPENERS):
            return "history"
        if cls._is_docket_text(head):
            return "docket"
        if all(cls._is_date_text(t) or cls._split_labelled_dates(t) for t in texts):
            return "date"
        joined = " ".join(texts).lower()
        if any(word in joined for word in _STATUS_WORDS):
            return "caption"
        if first:
            return "banner"
        return "counsel"

    @classmethod
    def _split_docket(cls, text):
        """('No. 23-1638', everything printed after it on the same row).

        The docket shares its row with whatever the court sets beside it, and
        the headmatter grouping (correctly) keeps them together: CA1 runs the
        case name straight on ('No. 23-1638 JUAN M. CRESPO-MORALES,
        Petitioner, ...'), CA11 an argument-calendar marker. A docket token is
        digits joined by hyphens or slashes ('24-13309', '18-8010/8013/8018');
        the first token that is not one ends the docket. What the remainder IS
        gets decided by the caller — it is not one fixed field."""
        tokens = text.split()
        if not tokens:
            return text, None
        # 'Case No. 25-3102' — the label runs to two words, not one.
        lead = 2 if tokens[0].lower() == "case" and len(tokens) > 1 else 1
        taken, rest, cut = tokens[:lead], tokens[lead:], 0
        for i, token in enumerate(rest):
            if cls._is_docket_token(token):
                taken.append(token)
                cut = i + 1
                continue
            # A CONSOLIDATED DOCKET IS STILL ONE DOCKET. CA3 joins them with a
            # conjunction ('Nos. 24-2990 and 24-3198'), and stopping at the
            # word dropped every docket after the first.
            if token.lower() in ("and", "&") and i + 1 < len(rest) and (
                cls._is_docket_token(rest[i + 1])
            ):
                taken.append(token)
                cut = i + 1
                continue
            break
        extra = " ".join(rest[cut:]).strip()
        return " ".join(taken).strip(), (extra or None)

    @staticmethod
    def _split_lower_docket(text):
        """(forum, lower docket, lower judge).

        The history line runs three different things together, and they are
        NOT the same field: the forum appealed from, that court's own docket
        number, and the judge who sat. CA1 prints the judge in brackets
        ('[Hon. Melissa R. DuBose, U.S. District Judge]') and no docket; CA11
        prints the docket ('D.C. Docket No. 1:22-cv-00776-VMC') and no judge.
        Take the bracketed judge out first, then read the docket from what is
        left, so a court that prints both still lands each in its own field."""
        judge = None
        open_at = text.find("[Hon.")
        if open_at >= 0:
            close_at = text.find("]", open_at)
            if close_at > open_at:
                judge = text[open_at : close_at + 1].strip()
                text = (text[:open_at] + " " + text[close_at + 1 :]).strip()
            else:
                judge = text[open_at:].strip()
                text = text[:open_at].strip()
        docket = None
        best = None
        for marker in _LOWER_DOCKET_MARKERS:
            at = text.find(marker)
            if at > 0 and (best is None or at < best):
                best = at
        if best is not None:
            docket = text[best:].strip()
            # The court parenthesises it — '(D.C. No. 1:24-CV-00001-GPG-STV)' —
            # and the opening bracket sits before the marker, so only the
            # closing one rides along.
            if docket.endswith(")") and docket.count("(") < docket.count(")"):
                docket = docket[:-1].strip()
            text = text[:best]
        return text.strip().rstrip(".").strip(), docket, judge

    @classmethod
    def _split_trailing_dates(cls, text):
        """(roster text, dates dict) — the dates a roster row carries after it.

        CA3 runs them straight on: 'Before: RESTREPO, MCKEE AND AMBRO, Circuit
        Judges Argued Nov. 10, 2025; Decided May 19, 2026'. Left in place they
        go through the name split and come back as extra judges ('Decided June
        11'), and the dates themselves are never recorded."""
        low = text.lower()
        best = None
        for label in _DATE_LABELS:
            at = low.find(label)
            # ...only a label that OPENS a word, and only after the bench title
            # that closes the roster.
            if at > 0 and (not low[at - 1].isalnum()):
                if best is None or at < best:
                    best = at
        if best is None:
            return text, {}
        # THE LABEL CAN SIT INSIDE A PARENTHESIS. CA3 closes the roster row
        # with '(Opinion filed: June 10, 2026)'; cutting at 'filed' left
        # '(Opinion' hanging on the end of the roster.
        head = text[:best]
        if head.count("(") > head.count(")"):
            best = head.rfind("(")
        dates = cls._split_labelled_dates(text[best:])
        if not dates:
            return text, {}
        return text[:best].rstrip(" ,;:."), dates

    @staticmethod
    def _panel_names(text):
        """The judges named in a 'Before ...' roster.

        Split on the punctuation the court itself uses, then keep the
        fragments that are NOT titles. Casing is not the signal: CA11 sets its
        judges in caps ('WILLIAM PRYOR, Chief Judge, ABUDU, Circuit Judge')
        and CA1 in title case ('Barron, Chief Judge, Aframe and Dunlap,
        Circuit Judges'), and both read correctly this way."""
        body = text.strip()
        for opener in ("before:", "before", "present:", "present"):
            if body.lower().startswith(opener):
                body = body[len(opener):]
                break
        names = []
        for chunk in body.replace(";", ",").split(","):
            piece = chunk.strip().strip(".*: ").strip()
            if not piece:
                continue
            if any(w in piece.lower().split() for w in _TITLE_WORDS):
                continue          # 'Chief Judge' / 'Circuit Judges.'
            for part in piece.replace(" and ", "|").split("|"):
                name = part.strip().strip(".*: ").strip()
                # The conjunction leads the LAST name when the court sets an
                # Oxford comma ('LUCK, LAGOA, and DUBINA'), so the comma split
                # hands back 'and DUBINA' with nothing to split on.
                if name.lower().startswith("and "):
                    name = name[4:].strip()
                if not name or not any(c.isalpha() for c in name):
                    continue
                # 'RAYMOND J. LOHIER, JR.' splits on its own comma; the suffix
                # is part of the judge's name, not another judge.
                if names and name.rstrip(".").upper() in (
                    "JR", "SR", "II", "III", "IV"
                ):
                    names[-1] = f"{names[-1]}, {name}"
                    continue
                names.append(name)
        return names

    def _origin_row(self, text):
        """(field, value) when a banner-zone row names the tribunal below.

        Off by default. A court that annotates page 1 with the body it is
        reviewing (CA2 stacks 'BIA' / 'Straus, IJ' / 'A209 866 562/563' above
        the banner) implements this — those rows are the origin of the appeal,
        not part of the court's own name."""
        return None

    def _split_embedded_roster(self, text):
        """(before-roster text, roster text) — or (text, None).

        Off unless ``roster_can_share_row``. A court that fences its roster in
        a band of its own never needs this; the ones that do not run something
        else onto the front of the roster's line — CA3 the submission
        authority ('Submitted Pursuant to Third Circuit L.A.R. 34.1(a) on June
        5, 2026 Before: BIBAS, ...'), CA5 the rehearing label ('ON PETITIONS
        FOR REHEARING Before Southwick, Duncan, and Engelhardt, Circuit
        Judges.'). Unsplit, the whole row read as one thing and the roster was
        never seen."""
        if not self.roster_can_share_row:
            return text, None
        low = text.lower()
        for marker in ("before:", "before "):
            at = low.find(marker)
            if at <= 0:
                continue
            tail = text[at:].strip()
            # A ROSTER, NOT A SENTENCE THAT STARTS WITH THE WORD. Body prose
            # says it constantly ('Before S.B. 4 took effect, Las Americas
            # Immigrant Advocacy Center ... sued'), and split blindly the
            # whole opinion was read as one enormous panel. What follows the
            # marker has to LOOK like a roster: short, and closing on the
            # bench word the court ends it with.
            if len(tail) > 250:
                continue
            # ...testing the roster WITHOUT the dates it may carry after its
            # bench word ('Before: RESTREPO, MCKEE AND AMBRO, Circuit Judges
            # Argued Nov. 10, 2025; Decided May 19, 2026'). Those are split off
            # downstream; requiring the raw row to end on the bench word
            # rejected every roster that stated them.
            bare, _dates = self._split_trailing_dates(tail)
            bare = bare.rstrip(".:;,*†‡∗ ").lower()
            # A roster closes on its bench word — or is left open mid-name
            # because the court wrapped it ('... and FREEMAN,'), which body
            # prose starting with 'Before' never is. Accept the wrap only
            # where the row ENDS on the break, with no sentence after it.
            if not bare.endswith(("judge", "judges")) and not (
                tail.rstrip().endswith(",") and len(tail) < 120
            ):
                continue
            return text[:at].strip(), tail
        return text, None

    def _is_disposition(self, text):
        """Is this row the court's statement of what it did with the appeal?

        Off by default: most circuits state the disposition in the opinion
        itself, and a row that merely names a judge is not one. CA4 sets it in
        its own ruled band and implements this."""
        return False

    def _split_embedded_history(self, text):
        """(caption tail, appeal-from block) — or (text, None).

        Off unless ``history_can_share_row``. Where a court does not fence the
        origin, it arrives on the end of the caption's last row — CA3
        ('Appellant On Appeal from the United States District Court for the
        Western District of Pennsylvania ...'), CA5 ('Defendants—Appellants,
        Appeal from the United States District Court for the Western District
        of Texas USDC Nos. ...'). Both were left unrecorded.

        Split only where the head is SHORT — a status word, not a sentence.
        Body prose says 'on appeal from' in the middle of an argument, and
        reading that as this case's origin published the wrong court."""
        if not self.history_can_share_row:
            return text, None
        low = text.lower()
        best = None
        for opener in _HISTORY_OPENERS:
            at = low.find(opener)
            if at > 0 and not low[at - 1].isalnum() and at <= 40:
                if best is None or at < best:
                    best = at
        if best is None:
            return text, None
        return text[:best].strip(" ,;"), text[best:].strip()

    def _claim_history(self, text, cur):
        """File one appeal-from row into the open case, opening one if there
        is none. Reads the forum, the lower docket and the lower judge out of
        it, which are printed inline as often as on rows of their own."""
        if cur is None:
            cur = {"docket": None, "caption": [], "prior_history": None}
        forum, lower, judge = self._split_lower_docket(text)
        # A COURT CAN STATE ITS ORIGIN TWICE. CA5 gives the appeal below and
        # then the remand above it ('Appeal from the United States District
        # Court for the Southern District of Mississippi USDC No. 3:21-CV-636'
        # ... 'ON REMAND FROM THE SUPREME COURT OF THE UNITED STATES'), and
        # replacing the first with the second lost the court appealed from.
        # ...but ONLY where the one already recorded is unfinished. CA5 breaks a
        # remand over two bands and the first half ends on its preposition
        # ('... USDC No. 3:21-CV-636' / 'ON REMAND FROM' / 'THE SUPREME COURT
        # OF THE UNITED STATES'), which is a continuation. A SECOND COMPLETE
        # origin is not: CA9 consolidates two appeals of the same case, each
        # with its own court and its own district judge, and joining them
        # produced one sentence naming two judges — 'Paul G. Rosenblatt,
        # District Judge, Presiding Appeal from the United States District
        # Court for the District of Arizona John Joseph Tuchi, District Judge,
        # Presiding'. That origin belongs to the other case, not this one.
        # The test is on the INCOMING line: a fragment continues what is open
        # ('ON REMAND FROM'), a complete origin is a statement of its own.
        continues = (forum or "").rstrip(" .,").lower().endswith(
            (" from", " of", " for", " the", " in", " to", " by")
        )
        if cur.get("prior_history") and forum:
            forum = (
                (cur["prior_history"] + " " + forum).strip()
                if continues
                else cur["prior_history"]
            )
        cur["prior_history"] = forum or cur.get("prior_history")
        if lower:
            cur["lower_docket"] = lower
        if judge:
            cur["lower_judge"] = judge
        return cur

    def _running_head_docket(self, text):
        """The docket carried by a page-1 running head, or None.

        Off by default: most circuits print no such head. A court that does
        (CA2) implements this, because the head is often the ONLY place the
        docket appears in full on a summary order."""
        return None

    def _tail_kind(self, text):
        """What a prose row AFTER the caption is: 'counsel' or 'summary'.

        Counsel has to be RECOGNISED, not assumed. Treating this position as
        'whatever is left must be counsel' is what made the field a dumping
        ground — a case summary, a note about the caption and a clerk's
        instruction all landed in it. An appearance says what it is: it argues,
        it is on the brief, or it acts for a named party.

        A court whose appearances read differently overrides this (CA2 heads
        each block with the party and sets the attorney in caps)."""
        low = " ".join(text.lower().split())
        if any(low.startswith(o) for o in _COUNSEL_OPENERS):
            return "counsel"
        if low.upper().startswith("FOR ") and ":" in low[:48]:
            return "counsel"
        return "counsel" if any(m in low for m in _COUNSEL_MARKERS) else "summary"

    def _counsel_span(self, doc, counsel_idx, counsel_parts, claimed, override=None):
        """The appearances as ONE block of source rows, spacing intact.

        ``counsel_idx`` are the rows the walk positively identified as
        counsel. The block is everything between the first and the last of
        them — a court does not print its caption in the middle of its
        appearances — which recovers the rows that announce nothing about
        themselves (a firm's name, a street address) and keeps the empty rows
        that separate one side's entry from the other's.

        A row another field already published is skipped, so nothing is
        reported twice."""
        if not counsel_idx:
            return counsel_parts
        lo, hi = min(counsel_idx), max(counsel_idx)
        span = []
        for i in range(lo, hi + 1):
            row = doc.summary[i]
            if isinstance(row, dict):
                continue
            if _is_typed_rule(row) or row == self.HEADMATTER_DIVIDER:
                continue
            text = (override or {}).get(i) or _plain(row).rstrip()
            if not text.strip():
                span.append("")             # the wall between two entries
                continue
            if text.strip() in claimed and i not in counsel_idx:
                continue
            span.append(text)
        # No leading blank, and never two in a row: the rhythm is what carries
        # meaning, not the exact number of empty rows the court left.
        out = []
        for line in span:
            if not line and (not out or not out[-1]):
                continue
            out.append(line)
        return out

    def parse_criteria(self, doc):
        """Dissect the headmatter into ``doc.criteria`` and the flat fields.

        Read ROW BY ROW, not zone by zone. The rules a court draws are a
        helpful grouping but they are not the unit of meaning: CA2 puts its
        term/date line and its docket inside ONE ruled zone, CADC puts dates,
        docket and caption together, and CA9 draws no rules at all — so a
        whole-zone verdict is wrong wherever a zone carries more than one kind
        of thing, and impossible where there are no zones.

        A row that answers to nothing continues whatever section is open, which
        is how a wrapped party name or the second line of a roster stays with
        its own field."""
        if not self.parse_criteria_enabled:
            return
        crit = {}
        cases, cur, banner = [], None, []
        panel_parts, counsel_parts, summary_parts = [], [], []
        tail_state = None
        dates, filed, publication = {}, None, None
        head_docket = None
        origin_fields = {}
        title = None
        lifted_rows = {}
        state = "banner"
        seen_panel = seen_caption = seen_rule = False
        # Has another section come between the caption and here? A caption can
        # resume across a rule (CA4 rules off its amici roll, CA2 its second
        # caption) but never across a DIFFERENT section: once the origin or the
        # dates have been stated, what follows in caps is something else.
        # ...which only means anything once a caption HAS been seen. CADC sets
        # its dates ABOVE the parties ('No. 26-5034 September Term, 2025' /
        # '1:25-cv-03581-UNA' / 'Filed On: June 10, 2026' / 'Timothy R.
        # Petrozzi,'), and closing the caption before it opened left every
        # such record with no case name at all.
        caption_closed = False
        fresh_block = False
        broke_history = False
        unclaimed, unclaimed_idx = [], []
        counsel_idx, counsel_text = [], {}
        counsel_open = False
        disposition_parts = []

        def open_case():
            nonlocal caption_closed
            caption_closed = False
            return {"docket": None, "caption": [], "prior_history": None}

        for idx, row in enumerate(doc.summary):
            if isinstance(row, dict):
                texts = self._zone_texts([row])
                if texts:
                    if cur is None:
                        cur = open_case()
                    for text in texts:
                        if _is_typed_rule(text):
                            continue   # a rule drawn inside a caption column
                        # The caption block's RIGHT column is not caption text.
                        # CA10 stacks three different things there — this
                        # court's docket, the district court's docket, and the
                        # district itself — and all three were being joined
                        # onto the end of the case name.
                        bare = text.strip().strip("()").strip()
                        if self._is_docket_text(text) and not cur["docket"]:
                            docket, rest = self._split_docket(text)
                            cur["docket"] = docket
                            if rest and any(
                                w in rest.lower() for w in _STATUS_WORDS
                            ):
                                cur["caption"].append(rest)
                            continue
                        if any(
                            bare.startswith(m) for m in _LOWER_DOCKET_MARKERS
                        ) and not cur.get("lower_docket"):
                            cur["lower_docket"] = bare
                            continue
                        if (
                            text.strip().startswith("(")
                            and text.strip().endswith(")")
                            and len(bare.split()) <= 4
                            and not cur.get("lower_court")
                        ):
                            # '(E.D. Okla.)' — the court appealed from.
                            cur["lower_court"] = bare
                            continue
                        cur["caption"].append(text)
                    state, seen_caption, seen_rule = "caption", True, True
                continue
            text = _plain(row).strip()
            if not text:
                continue
            # A TYPED RULE WITH SOMETHING STUCK TO IT. CA5's page-1 clerk stamp
            # lands on the end of one ('_____________ Clerk'), and the row then
            # answers neither the rule test nor anything else — so the whole
            # thing was read as the start of the next case's name.
            stripped = text.lstrip("_").strip()
            # ...only where something is left. A row that is ALL underscores is
            # the rule itself, and consuming it here left the section it closes
            # still open.
            if stripped and len(text) - len(text.lstrip("_")) >= 3:
                text = stripped
            # THE CONNECTOR BETWEEN TWO CONSOLIDATED DOCKETS. It names no party
            # and opens no section; read as caption it became a case name.
            if " ".join(text.lower().split()).strip(".:") in (
                "consolidated with", "and consolidated with", "consolidated with:"
            ):
                continue
            if _is_typed_rule(row) or text == self.HEADMATTER_DIVIDER:
                seen_rule = True
                fresh_block = True
                counsel_open = False
                # A wall closes whatever section was running on. It decides
                # nothing by itself, but a caption does not continue across it
                # — CA10 sets the document's title in its own ruled band under
                # the caption, and without this it read as more party names.
                # NOT the docket state: several circuits fence the docket in
                # rules of its own and print the caption directly under it
                # ('_____ / No. 26-10354 / _____ / In re Edward Lee Busby,'),
                # so closing there orphaned the second caption of every
                # consolidated CA5 record.
                if state in ("history", "date", "caption"):
                    if state == "history":
                        broke_history = True
                    state = "loose"
                continue

            low = text.lower()
            if self.criteria_lift_publication and not publication:
                flag = self._publication_flag(text)
                if flag:
                    publication = flag
                    continue
                if state == "banner":
                    flag, rest = self._split_publication(text)
                    if flag and rest and self._is_court_banner(rest):
                        publication = flag
                        lifted_rows[text] = rest
                        text = rest
                        low = text.lower()
            # CA2 LETTER-SPACES its opener ('B e f o r e:'), which matches no
            # prefix at all — so the roster went unrecognised and its judges
            # were read as more caption. Test the space-stripped form too.
            # A court can print the roster part-way along a row, after the
            # submission line (CA3). Split it off before anything else claims
            # the row.
            # ...and only while the roster is still to come. Once it has been
            # read, every later 'Before' is prose.
            # THE COURT'S OWN NAME, WHEREVER IT SITS. Most circuits set it at
            # the very top, so the banner zone alone could claim it — but CA6
            # prints the docket FIRST and the court under it, which opens a
            # case and closes the banner zone before the name arrives. It then
            # answered the party-roll test and became the head of the case
            # name, and the court field stayed empty.
            if (
                not banner
                and self.circuit_phrase
                and self.circuit_phrase in low
                and self._is_court_banner(text)
            ):
                banner.append(text)
                continue
            head_text, embedded = (
                self._split_embedded_roster(text) if not seen_panel
                else (text, None)
            )
            if embedded:
                labelled = self._split_labelled_dates(head_text)
                if labelled:
                    dates.update(labelled)
                elif (
                    self.criteria_has_title
                    and title is None
                    and head_text
                    and self._is_party_text(head_text)
                    and self._is_title_text(head_text)
                ):
                    # CA5 labels the rehearing on the front of the roster's own
                    # row ('ON PETITIONS FOR REHEARING Before Southwick, ...').
                    # That IS the document's title; discarded with the rest of
                    # the head, the record showed none.
                    title = head_text
                elif head_text.lower().startswith(_HISTORY_OPENERS):
                    # THE HEAD OF THE ROW IS NOT ALWAYS A DATE. CA3 runs the
                    # whole appeal-from block and the roster together on one
                    # line ('Appeal from the U.S. District Court, D.N.J.
                    # Magistrate Judge Cathy L. Waldor, No. 2:17-cv-07386
                    # Before: KRAUSE, ...'). Split off the roster and the rest
                    # was dropped, so those records showed no history at all.
                    cur = self._claim_history(head_text, cur)
                panel_parts.append(embedded)
                seen_panel = True
                fresh_block = False
                # ...and it may not be finished. CA3 wraps it onto the next row
                # ('... Before: HARDIMAN, KRAUSE, and FREEMAN,' / 'Circuit
                # Judges'), so the roster stays open until its bench word.
                bare, _d = self._split_trailing_dates(embedded)
                closed = bare.rstrip(".:; ").lower().endswith(
                    ("judge", "judges")
                )
                state = "after_panel" if closed else "panel"
                continue

            tight = "".join(low.split())
            opened = any(
                low == o.strip() or low.startswith(o) or tight.startswith(
                    "".join(o.split())
                )
                for o in self.panel_openers
            )
            if opened:
                # An opener that carries no names of its own ('Before' /
                # 'B e f o r e:' / 'PRESENT:') is a label; keeping it would put
                # its own letters through the name split.
                rest = tight
                for o in self.panel_openers:
                    key = "".join(o.split())
                    if rest.startswith(key):
                        rest = rest[len(key):]
                        break
                if any(c.isalpha() for c in rest):
                    panel_parts.append(text)
                seen_panel = True
                # THE ROSTER ALSO CLOSES ANY OPEN 'a rule may reopen the
                # caption' licence. CA3 rules off its history block ABOVE the
                # roster, so the flag was still set when the appearances
                # arrived and the firm's name ('OPIEL LAW') was read as more
                # parties. Only a rule BELOW the roster opens a second caption.
                fresh_block = False
                # THE ROSTER ENDS AT ITS BENCH TITLE. CA1 sets 'Before' alone
                # and the names on the next row, so the section has to stay
                # open — but only until the title that closes it ('...,
                # Circuit Judges.'), or the whole counsel block that follows
                # continues the roster and reads as fifteen more judges.
                state = (
                    "after_panel"
                    if any(w in low.split() for w in _TITLE_WORDS)
                    or any(low.rstrip(".").endswith(w) for w in _TITLE_WORDS)
                    else "panel"
                )
                continue
            # THE COURT'S OWN STATEMENT OF WHAT IT DID, and it is tested FIRST.
            # CA4 sets it in a ruled band between the roster and the
            # appearances, and its opening words are the outcome, which can be
            # the same words a history line opens with ('Petition for review
            # granted; order vacated and remanded by published opinion. Judge
            # Novak wrote the majority opinion, ...'). Read as history it
            # overwrote the tribunal the case actually came from.
            if self._is_disposition(text):
                disposition_parts.append(text)
                tail_state = "disposition"
                state = "loose"
                continue
            if low.startswith(_HISTORY_OPENERS):
                cur = self._claim_history(text, cur)
                state = "history"
                caption_closed = seen_caption
                continue
            # THE HISTORY CAN START PART-WAY ALONG A ROW. CA3 sets the
            # caption's closing status word and the entire appeal-from block on
            # one line ('Appellant On Appeal from the United States District
            # Court for the Western District of Pennsylvania (District Court
            # No. 2:21-cr-00223-001) District Judge: ...'), so the row answers
            # to no opener and the history went unrecorded.
            head_text, hist = (
                self._split_embedded_history(text) if not seen_panel
                else (text, None)
            )
            if hist:
                if head_text and cur is not None:
                    cur["caption"].append(head_text)
                    seen_caption = True
                cur = self._claim_history(hist, cur)
                state = "history"
                caption_closed = seen_caption
                continue
            if self._is_docket_text(text) and state == "history" and cur is not None:
                # The court appealed FROM lists its own docket numbers under
                # the appeal-from line ('Nos. 2:23-md-03074, 2:22-cv-04709,
                # ...'). Those are not a second appeal — reading them as one
                # opened an empty extra case on every consolidated CA3 record.
                existing = cur.get("lower_docket")
                cur["lower_docket"] = f"{existing} {text}".strip() if existing else text
                continue
            if (
                state == "docket"
                and cur is not None
                and cur.get("docket")
                and not cur.get("caption")
                and self._is_docket_text(text)
            ):
                # A CONSOLIDATED DOCKET LIST WRAPS. CA1 sets 'Nos. 25-1212'
                # and '25-1213' on consecutive rows; read as a second docket
                # the bare row opened an empty extra case, which then took the
                # caption belonging to the first.
                # THE SECOND NUMBER CAN CARRY ITS OWN 'No.' TOO. CA5 stacks
                # them under a connector ('No. 25-11253 / consolidated with /
                # No. 25-11254') and then prints ONE caption for both — so it
                # is one case with two dockets, and opening a second left the
                # first with an empty name. What decides it is whether a
                # caption has arrived yet: where each docket has its own
                # (CA5's busby), the second genuinely opens a new case.
                cur["docket"] = f"{cur['docket']} {text}".strip()
                continue
            if self._is_docket_text(text):
                docket, rest = self._split_docket(text)
                # CAFC prints the caption FIRST and the bare docket after it, so
                # a docket arriving into a case that has none belongs to THAT
                # case; only a docket on top of a docket opens the next one.
                if cur is not None and not cur["docket"]:
                    cur["docket"] = docket
                else:
                    if cur is not None:
                        cases.append(cur)
                    cur = open_case()
                    cur["docket"] = docket
                if rest and any(w in rest.lower() for w in _STATUS_WORDS):
                    cur["caption"].append(rest)
                    seen_caption = True
                state = "docket"
                continue
            labelled, date_tail = self._split_labelled_dates(text, want_tail=True)
            if labelled:
                dates.update(labelled)
                # WHAT FOLLOWS THE DATE ON ITS OWN ROW IS NOT THE DATE. CA3
                # sets the filing date and the first appearance on one line
                # ('(Opinion filed: April 28, 2026) Joel S. Sansone (Argued)
                # Law Offices of Joel Sansone ...'). The date reads to its
                # year; the remainder is offered to the appearances, and if
                # they do not claim it, it is left out rather than filed
                # under whichever field happened to be open.
                if date_tail and self._tail_kind(date_tail) == "counsel":
                    if self.counsel_label_trails and unclaimed:
                        counsel_parts.extend(unclaimed)
                        counsel_idx.extend(unclaimed_idx)
                        unclaimed, unclaimed_idx = [], []
                    counsel_parts.append(date_tail)
                    counsel_idx.append(idx)
                    counsel_text[idx] = date_tail
                    tail_state = "counsel"
                # CA2 runs the term, the dates AND the docket together on one
                # line ('August Term, 2025 (Submitted: ... Decided: ...) Docket
                # No. 25-406'), so the docket has to be read here or the row is
                # consumed as dates and the number never seen.
                at = text.find("Docket No")
                if at >= 0 and cur is not None and not cur.get("docket"):
                    docket, _rest = self._split_docket(text[at + len("Docket "):])
                    if docket.strip().rstrip(".") not in ("No", "Nos"):
                        cur["docket"] = docket
                state = "date"
                caption_closed = seen_caption
                continue
            if self._is_date_text(text):
                filed = text
                state = "date"
                caption_closed = seen_caption
                continue
            # A DOCKET PRINTED INSIDE THE CAPTION. CA2 sets it on the 'v.' row
            # between the parties ('v. No. 25-2417-cv'), which is too short to
            # read as a party roll and so never reached the caption branch.
            # Any row can carry it once a case is open and still lacks one.
            # ...on a CAPTION-LENGTH row only. Body prose cites other cases by
            # number ('submitted in tandem with Campbell v. City of Binghamton,
            # No. 25-409'), and reading that as this case's docket published a
            # number belonging to a different appeal — worse than none at all.
            if cur is not None and not cur["docket"] and len(text) <= 60:
                at = text.find("No. ")
                if at >= 0:
                    docket, _rest = self._split_docket(text[at:])
                    if docket.strip().rstrip(".") not in ("No", "Nos"):
                        cur["docket"] = docket
                        text = (text[:at] + " " + text[at + len(docket):]).strip()
                        if not text:
                            continue
                        low = text.lower()

            # AN OPEN ROSTER CLAIMS ITS OWN CONTINUATION. CA2 sets 'PRESENT:'
            # alone, the judges on the next row and 'Circuit Judges.' on a
            # third — and the judges row is long and all-caps, so the caption
            # test below claimed it and the panel became the case name.
            if state == "panel":
                panel_parts.append(text)
                if any(w in low.split() for w in _TITLE_WORDS) or any(
                    low.rstrip(".").endswith(w) for w in _TITLE_WORDS
                ):
                    state = "after_panel"
                continue

            # A HISTORY LINE CAN WRAP AROUND A FOOTNOTE. CA2 prints the
            # caption's footnote between the two halves ('Appeal from the
            # United States District Court' ... '* The Clerk of Court is
            # respectfully directed ...' ... 'for the Western District of New
            # York No. 6:25-cv-6532, Meredith A. Vacca, Judge.'). The second
            # half opens lower case, which no new section ever does.
            # ...OR AROUND A RULE, WITH THE HISTORY LEFT DANGLING. CA5 sets
            # the remand over two bands ('ON REMAND FROM' / rule / 'THE
            # SUPREME COURT OF THE UNITED STATES'); the second half is in caps
            # like a caption, and it was published as the document's title.
            # A history that ends on a preposition has not finished saying
            # where the case came from, whatever the next row looks like.
            if (
                broke_history
                and cur is not None
                and cur.get("prior_history")
                and (
                    text[:1].islower()
                    or cur["prior_history"].rstrip(" .,").lower().endswith(
                        (" from", " of", " for", " the", " in", " to", " by")
                    )
                )
            ):
                more, lower, judge = self._split_lower_docket(text)
                if lower and not cur.get("lower_docket"):
                    cur["lower_docket"] = lower
                if judge and not cur.get("lower_judge"):
                    cur["lower_judge"] = judge
                if more:
                    cur["prior_history"] = (
                        cur["prior_history"] + " " + more
                    ).strip()
                broke_history = False
                state = "history"
                continue

            # THE DOCUMENT'S OWN TITLE. Set in caps in its own band once the
            # caption is closed ('ORDER DENYING CERTIFICATE OF APPEALABILITY*').
            # It answers the party-roll test — caps, long enough — so it has to
            # be claimed here or it lands on the end of the case name.
            if (
                self.criteria_has_title
                and state == "loose"
                and seen_caption
                and title is None
                and self._is_party_text(text)
                and self._is_title_text(text)
                and not any(w in low for w in _STATUS_WORDS)
                and not self._is_court_banner(text)
            ):
                title = text
                continue

            # A caption row: it names parties, or it labels their status.
            # The 'counsel comes after the roster' rule needs BOTH a roster and
            # a caption already seen — CA2's summary order prints 'PRESENT:'
            # ABOVE the caption, so keying on the roster alone suppressed every
            # caption on that whole variant.
            # A caption row NAMES parties (caps) or LABELS them ('Plaintiffs -
            # Appellants,'). Counsel prose says who it acts for in the same
            # words — 'Barry K. Arrington, Arrington Law Firm, Wheat Ridge,
            # Colorado for Plaintiffs- Appellants' — so a status word alone is
            # not enough: a label is short, an appearance is a sentence. This
            # matters most where a court prints no roster at all, because then
            # the 'counsel follows the roster' rule never engages.
            caption_row = self._is_party_text(text) or (
                any(w in low for w in _STATUS_WORDS) and len(text) <= 60
            )
            if caption_row and self._is_court_banner(text):
                caption_row = False          # the court's own name
            if caption_row and state == "banner" and not seen_rule:
                # A CAPTION OPENS BELOW A RULE, never above the first one.
                # Everything over it is the court's own name and its notices,
                # and those are set in caps too — CA2's 'ANY PARTY NOT
                # REPRESENTED BY COUNSEL.' opened the caption 9 rows early,
                # which then blocked the real caption further down and sent it
                # to counsel instead.
                caption_row = False
            # The roster normally separates the caption from the appearances,
            # so a party-shaped row after it is counsel. But a RULE opens a new
            # caption block: CA2 sets a bankruptcy 'IN RE:' caption, rules it
            # off, then sets the appeal caption underneath — and the second one
            # is still a caption however late it comes.
            if caption_row and caption_closed:
                # THE CAPTION DOES NOT REACH ACROSS ANOTHER SECTION. CA5 sets
                # the rehearing label below the origin ('... Defendant—Appellee.
                # / rule / Appeal from the United States District Court for the
                # Southern District of Mississippi ... / rule / ON PETITION FOR
                # REHEARING'), and joined to the parties it made the case name
                # read as though the court were a party to it.
                caption_row = False
            if caption_row and not (seen_panel and seen_caption and not fresh_block):
                if cur is None:
                    cur = open_case()
                # CA2 runs the docket INTO the caption ('v. No. 25-2417-cv').
                at = text.find("No. ")
                if at >= 0 and not cur["docket"]:
                    docket, _rest = self._split_docket(text[at:])
                    if docket.strip() != "No.":
                        cur["docket"] = docket
                        text = (text[:at] + " " + text[at + len(docket) :]).strip()
                clean, cap_dockets = self._split_caption_dockets(text)
                if cap_dockets:
                    have = cur.get("docket") or ""
                    for piece in cap_dockets.split(";"):
                        piece = piece.strip()
                        if piece and piece not in have:
                            have = f"{have}; {piece}".strip("; ")
                    cur["docket"] = have if have.startswith(("No.", "Nos.")) \
                        else f"No. {have}"
                    text = clean
                if text and any(c.isalnum() for c in text):
                    cur["caption"].append(text)
                seen_caption = True
                state = "caption"
                fresh_block = False
                continue

            # Nothing matched: continue whatever is open.
            # THE ROSTER CLOSES THE CAPTION FOR GOOD. Without this the caption
            # state, once open, kept claiming every later row — CA3's counsel
            # block ('Counsel for Appellee' / the names / 'Counsel for
            # Appellant') was appended to the case name, which is why the name
            # ran on past its parties and counsel never reached its own field.
            if (
                state in ("docket", "caption")
                and cur is not None
                and not seen_panel
                and not caption_closed
            ):
                # A CAPTION GROWS IN THREE PLACES — here, in the caption branch
                # and alongside the docket — so the 'we have a caption' flag has
                # to be set in all of them. Set in only one, it stayed False on
                # any record whose caption arrived by the other routes, and the
                # guard that stops counsel being read as caption never engaged:
                # 'Noreen McCarthy and The McCarthy Law Firm for appellant.' is
                # short and names a party, so it went into the case name.
                # A caption row reached by continuation carries dockets just
                # as one reached by the caption test does — CA2's consolidated
                # 'v. 23-258 (L)' / '23-263 (CON)' column arrives HERE, which
                # is why splitting only in the caption branch left it in the
                # case name.
                clean, cap_dockets = self._split_caption_dockets(text)
                if cap_dockets:
                    have = cur.get("docket") or ""
                    for piece in cap_dockets.split(";"):
                        piece = piece.strip()
                        if piece and piece not in have:
                            have = f"{have}; {piece}".strip("; ")
                    cur["docket"] = (
                        have if have.startswith(("No.", "Nos.")) else f"No. {have}"
                    )
                    text = clean
                if text and any(c.isalnum() for c in text):
                    cur["caption"].append(text)
                seen_caption = True
            elif state == "history" and cur is not None:
                # The history runs on over its own rows, and what continues it
                # is not always more history: CA1 sets the district judge on a
                # line of its own directly beneath ('[Hon. María
                # Antongiorgi-Jordán, U.S. District Judge]'). Read the
                # continuation the same way as the opening row so the judge and
                # the lower docket land in their own fields instead of being
                # glued onto the end of the forum.
                # The judge can be NAMED on a continuation row rather than
                # bracketed: CA3 closes its history block with 'District Judge:
                # Honorable Malachy E. Mannion'. Left in place it reads as more
                # forum text.
                lead = text.split(":", 1)
                if len(lead) == 2 and lead[0].strip().lower().endswith("judge"):
                    if not cur.get("lower_judge"):
                        cur["lower_judge"] = text.strip()
                    continue
                more, lower, judge = self._split_lower_docket(text)
                if lower and not cur.get("lower_docket"):
                    cur["lower_docket"] = lower
                if judge and not cur.get("lower_judge"):
                    cur["lower_judge"] = judge
                if more:
                    cur["prior_history"] = (
                        (cur["prior_history"] or "") + " " + more
                    ).strip()
            elif state == "panel":
                panel_parts.append(text)
                if any(w in low.split() for w in _TITLE_WORDS) or any(
                    low.rstrip(".").endswith(w) for w in _TITLE_WORDS
                ):
                    state = "after_panel"
            elif seen_caption or seen_panel:
                # WHAT THIS IS DEPENDS ON THE ROW, NOT ON WHERE IT SITS. Half
                # the circuits print counsel above the roster (CA10, CADC) and
                # half below it (CA1, CA2), so position cannot decide — the row
                # has to say it is an appearance.
                kind = self._tail_kind(text)
                # A COUNSEL BAND RUNS TO ITS RULE. Where the court fences the
                # appearances (CA4), every row inside the fence is counsel —
                # only the first announces itself, and the wrapped remainder
                # says nothing about what it is.
                if self.counsel_runs_to_rule and counsel_open:
                    kind = "counsel"
                # A COUNSEL ENTRY RUNS ON. Only its first line announces itself
                # ('FOR RESPONDENT: Brian M. Boynton, ...'); the lines under it
                # are ordinary prose.
                if (
                    kind != "counsel"
                    and tail_state == "counsel"
                    and counsel_parts
                    and not counsel_parts[-1].rstrip().endswith(".")
                ):
                    # ...only while the previous entry is unfinished. One that
                    # ended on a full stop is complete, and letting it run on
                    # swallowed the case summary that followed it.
                    kind = "counsel"
                if kind == "counsel":
                    counsel_open = True
                    if self.counsel_label_trails and unclaimed:
                        counsel_parts.extend(unclaimed)
                        counsel_idx.extend(unclaimed_idx)
                    unclaimed, unclaimed_idx = [], []
                    counsel_parts.append(text)
                    counsel_idx.append(idx)
                elif (
                    kind == "summary"
                    and self.criteria_has_summary
                    and not text.lstrip().startswith(("*", "∗", "†", "‡"))
                    and tail_state != "note"
                ):
                    summary_parts.append(text)
                elif self.counsel_label_trails:
                    # Hold it: the label that would identify it may be the
                    # NEXT row.
                    unclaimed.append(text)
                    unclaimed_idx.append(idx)
                elif text.lstrip().startswith(("*", "∗", "†", "‡")):
                    # A FOOTNOTE ON THE CAPTION, marked as one by the court
                    # ('* The Clerk of Court is instructed to amend the
                    # official caption...'). It is not the case summary, and it
                    # is not an appearance — so it is not recorded here at all.
                    kind = "note"
                # ...and otherwise NOTHING. A row this walk cannot identify is
                # left out of the criteria rather than filed under whatever
                # bucket is nearest — the raw headmatter still shows it, and a
                # field that collects leftovers is worse than an absent one.
                tail_state = kind
            elif state == "banner" and not seen_panel and cur is None:
                # CA2 prints a RUNNING HEAD above the banner ('24-1510 Adidas
                # America, Inc. v. Thom Browne, Inc.') — a docket token followed
                # by the short case name. It is page furniture, not the court.
                origin = self._origin_row(text)
                if origin:
                    origin_fields[origin[0]] = origin[1]
                    continue
                # ``court`` IS THE COURT'S NAME, nothing else. The banner zone
                # also carries the document's label ('SUMMARY ORDER'), notices
                # ('ANY PARTY NOT REPRESENTED BY COUNSEL.') and the convening
                # preamble ('At a stated term of ... held at the Thurgood
                # Marshall United States Courthouse ...'); joining all of it
                # made the field a paragraph. The rest stays in the raw
                # headmatter, which is where the reader sees it.
                if not self._is_court_banner(text):
                    continue
                head = text.split()
                if head and self._is_docket_token(head[0]):
                    # Page furniture — but it names the docket, which a
                    # summary order prints nowhere else.
                    if head_docket is None:
                        head_docket = self._running_head_docket(text)
                else:
                    banner.append(text)
            else:
                counsel_parts.append(text)
                counsel_idx.append(idx)
        if cur is not None:
            cases.append(cur)

        # The caption zone is ONE thing — the long case name the court prints
        # between its rules. Keep the source rows (they carry the party/status
        # structure) but publish the joined name, so the panel shows one
        # caption per case. A consolidated appeal still shows one per case.
        for case in cases:
            if case.get("caption"):
                case["case_name"] = " ".join(case["caption"])
        # ONE ORIGIN FOR ALL OF THEM. A CA4 consolidated record states the
        # court appealed from once, below the last caption ('Appeals from the
        # United States District Court for the Western District of North
        # Carolina, at Charlotte. Max O. Cogburn, Jr., District Judge.'), and
        # it governs every case in the record — but the walk could only file it
        # against whichever case was still open, leaving the others with none.
        if self.criteria_shared_tail and len(cases) > 1:
            for key in ("prior_history", "lower_court", "lower_docket",
                        "lower_judge"):
                stated = next((c[key] for c in cases if c.get(key)), None)
                if stated:
                    for case in cases:
                        case.setdefault(key, None)
                        if not case.get(key):
                            case[key] = stated
        # The running head names the docket of the LEAD case; use it only where
        # the body of the headmatter never stated one.
        if origin_fields and cases:
            for key, value in origin_fields.items():
                cases[0].setdefault(key, value)
        if head_docket and cases and not cases[0].get("docket"):
            cases[0]["docket"] = head_docket
        elif head_docket and not cases:
            cases.append({"docket": head_docket, "caption": [],
                          "prior_history": None})

        # A roster set over two rows ('Before' / 'Barron, Chief Judge, ...')
        # is one line.
        panel_line = " ".join(panel_parts).strip() or None
        if panel_line:
            panel_line, trailing = self._split_trailing_dates(panel_line)
            for key, value in trailing.items():
                dates.setdefault(key, value)
            panel_line = panel_line or None
        # THE APPEARANCES ARE ONE BLOCK, NOT A LIST OF ROWS. A court sets its
        # counsel as a contiguous run — firm, address, 'Counsel for Appellant',
        # a blank line, then the next side — and the blank lines between the
        # entries are what tells them apart. Rebuilt row by row it came out as
        # one undifferentiated stack, and any row the walk could not name
        # individually (a firm's name, a street) fell out of it entirely.
        # So: take the whole span from the first counsel row to the last,
        # verbatim, keeping the empty rows that separate the entries.
        claimed = set(panel_parts) | set(summary_parts) | set(banner)
        for case in cases:
            claimed.update(case.get("caption") or [])
        if title:
            claimed.add(title)
        counsel_parts = self._counsel_span(
            doc, counsel_idx, counsel_parts, claimed, counsel_text)
        # The filing date can run on the end of the counsel block with no wall
        # between them.
        while counsel_parts:
            last = counsel_parts[-1].strip()
            if not last:
                counsel_parts.pop()
                continue
            tail_dates = self._split_labelled_dates(last)
            if tail_dates:
                dates.update(tail_dates)
                counsel_parts.pop()
            elif self._is_date_text(last):
                filed = counsel_parts.pop()
            else:
                break
        counsel = "\n".join(counsel_parts).strip("\n") or None

        if publication:
            crit["publication"] = publication
            kept_rows = []
            for r in doc.summary:
                if not isinstance(r, str):
                    kept_rows.append(r)
                    continue
                bare = _plain(r).strip()
                if bare == publication:
                    continue                      # the flag had its own row
                if bare in lifted_rows:
                    # The flag shared the banner row: drop the flag's words
                    # from it and keep the court's name, which is content.
                    kept_rows.append(lifted_rows[bare])
                    continue
                kept_rows.append(r)
            doc.summary = kept_rows
        if banner:
            crit["court"] = " ".join(banner)
        if cases:
            crit["cases"] = cases
        if panel_line:
            crit["panel_line"] = panel_line
            crit["panel"] = self._panel_names(panel_line)
        if title:
            crit["title"] = title
        if disposition_parts:
            crit["disposition"] = " ".join(disposition_parts)
        if summary_parts:
            crit["summary"] = "\n".join(summary_parts)

        if counsel:
            crit["counsel"] = counsel
        if filed:
            crit["date_filed"] = filed
        for key, value in dates.items():
            crit[f"date_{key}"] = value
        self._publish_criteria(doc, crit)

    def skip_headmatter_segment(self, seg) -> bool:
        """Route a PAGE NUMBER out of the headmatter and into ``dropped``.

        A circuit's counsel block routinely runs across the page break, and the
        page number sits between two appearances — so it arrives in the middle of
        the headmatter rather than below it, where the furniture sweep would have
        taken it. Narragansett's read '… amicus curiae United South and Eastern
        Tribes …' / '2' / 'Dimitar P. Georgiev, Assistant U.S. Attorney …'.

        A bare integer alone on its row is a page number: a docket always carries
        a hyphen or a 'No.', and no party or appearance is a number by itself."""
        if len(seg) == 1:
            bare = self.line_plain_text(seg[0]).strip()
            if bare.isdigit() and len(bare) <= 4:
                return True
        return super().skip_headmatter_segment(seg)

    def _scrub_markers(self, crit):
        """Strip STRUCTURAL MARKERS out of the parsed values.

        ``__DIVIDER__`` stands for a rule the page DREW. It belongs in the raw
        headmatter rows, where the renderer turns it back into a border — but a
        criteria value is text the court said, and a marker is not. Any row the
        walk folds into a field can carry one, and CADC's prior history came out
        as 'Appeal from the United States District Court for the District of
        Columbia (No. 1:24-cv-00780) __DIVIDER__'. Scrubbed once here rather than
        at each of the several places a value is accumulated."""
        marker = self.HEADMATTER_DIVIDER

        def clean(value):
            if isinstance(value, str):
                if marker not in value:
                    return value
                return " ".join(value.replace(marker, " ").split()).strip(" ;,")
            if isinstance(value, list):
                out = [clean(item) for item in value]
                return [item for item in out if item not in ("", None)]
            if isinstance(value, dict):
                return {key: clean(item) for key, item in value.items()}
            return value

        return clean(crit)

    def _publish_criteria(self, doc, crit):
        """Attach ``crit`` to the document and mirror it into the flat fields.

        The shared walk is one WAY of reading a headmatter, not the contract.
        A circuit whose format the walk does not fit writes its own reader and
        ends by calling this — so what a court has to own is the reading, not
        the plumbing that carries the result to the renderer and the DB."""
        crit = self._scrub_markers(crit)
        doc.criteria = crit
        cases = crit.get("cases") or []
        dates = {
            key[len("date_"):]: value
            for key, value in crit.items()
            if key.startswith("date_")
        }
        dockets = [c["docket"] for c in cases if c.get("docket")]
        if dockets:
            doc.docket_number = dockets[0]
            if len(dockets) > 1:
                doc.other_docket = "; ".join(dockets[1:])
        history = [c["prior_history"] for c in cases if c.get("prior_history")]
        if history:
            doc.lower_court = history[0]
            doc.history = "; ".join(dict.fromkeys(history))
        if crit.get("panel_line"):
            doc.judges = crit["panel_line"]
            doc.panel = crit.get("panel", [])
        parties = [t for c in cases for t in c.get("caption", [])]
        if parties:
            doc.parties = parties
        decided = (
            dates.get("filed")
            or dates.get("decided")
            or dates.get("decided_and_filed")
        )
        if decided and not doc.decision_date:
            doc.decision_date = decided
        submitted = dates.get("submitted") or dates.get("argued_and_submitted")
        if submitted and not doc.submitted:
            doc.submitted = submitted

    def _merge_furniture(self, doc) -> None:
        """Append the recorded page furniture to ``doc.dropped`` — once."""
        if getattr(self, "_furniture_merged", None) is doc:
            return
        self._furniture_merged = doc
        # de-dup, preserve first-seen order
        extra = list(dict.fromkeys(getattr(self, "_furniture_dropped", None) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the recorded furniture BEFORE the completeness sweep.

        The sweep builds its 'already placed' haystack from the document as it
        stands, and ``doc.dropped`` was only being filled after ``extract``
        returned — so every running head the filter had correctly removed AND
        recorded still came back as unplaced content ('Nos. 24-2489 & 24-2672
        3' on each odd page)."""
        self._merge_furniture(doc)
        super()._sweep_residual(doc, source_pages)

    def _record_dropped(self, text: str) -> None:
        """Register a line of identified page furniture removed during line
        filtering, so it surfaces in the Removed box instead of vanishing."""
        if not text:
            return
        if getattr(self, "_furniture_dropped", None) is None:
            self._furniture_dropped = []
        self._furniture_dropped.append(text)

    def _is_running_head(self, page, line) -> bool:
        if self.running_head_max_top is None:
            return False
        if page.page_number < self.running_head_first_page:
            return False
        if line.get("top", 1e9) >= self.running_head_max_top:
            return False
        if self.running_head_max_size is None:
            return True
        chars = line.get("chars") or []
        if not chars:
            return False
        return max(c.get("size", 0) for c in chars) <= self.running_head_max_size

    def _drop_running_header(self, lines):
        """Record whatever the base's docket-header sweep removes, so the
        running header surfaces in the Removed box instead of vanishing."""
        kept = super()._drop_running_header(lines)
        if len(kept) != len(lines):
            keep = {id(l) for l in kept}
            for ln in lines:
                if id(ln) not in keep:
                    self._record_dropped(self.line_plain_text(ln).strip())
        return kept

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

        Bounded by the court's DOUBLE-spaced pitch, not its single: on a
        double-spaced court the two halves of one wrapped byline sit a full
        body line apart (ca4: 29.9pt), so a single-spaced bound never reached
        them and the whole majority opinion stayed in the headmatter.

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
        if not 0 < gap <= self.gap_double_max:
            return None
        if nxt.get("x0", 0) > line.get("x0", 0) + 2:
            return None
        # The two lines' CHARS are what every downstream reader rebuilds the
        # text from, and concatenating them directly welds the last word of one
        # line to the first of the next ('the denial ofrehearing en banc').
        # The line break itself is a space, so carry one across.
        head = list(line.get("chars") or [])
        tail = list(nxt.get("chars") or [])
        if head and tail:
            joiner = dict(head[-1])
            joiner["text"] = " "
            joiner["x0"] = joiner["x1"] = head[-1].get("x1", 0)
            head = head + [joiner]
        merged = self._rebuild_line(line, head + tail)
        merged["text"] = f"{text} {(nxt.get('text') or '').strip()}"
        split = self._byline_split(merged)
        if split is None or not split[0].rstrip().endswith((".", ":")):
            return None
        return merged

    def _drop_head_band(self, page, lines):
        """Remove (and record) the running-head lines from ``lines``."""
        if self.running_head_max_top is None:
            return lines
        kept = []
        for ln in lines:
            if self._is_running_head(page, ln):
                self._record_dropped(self.line_plain_text(ln).strip())
                continue
            kept.append(ln)
        return kept

    def _is_stamp_char(self, c) -> bool:
        """Is this glyph part of the clerk's e-filing stamp?

        ``efile_stamp_size`` may name SEVERAL sizes. The stamp is not set in
        one size throughout: CA10 sets its block at 12pt but the filing DATE
        inside it at 14pt, so a single-size test dropped the surrounding lines
        and left the date behind — which then merged into the centred banner
        beside it ('UNITED STATES COURT OF APPEALS April 21, 2026') and took
        'FOR THE TENTH CIRCUIT' into the Removed box with it."""
        if self.efile_stamp_font is None or self.efile_stamp_size is None:
            return False
        fn = c.get("fontname") or ""
        if not fn.endswith(self.efile_stamp_font):
            return False
        sizes = self.efile_stamp_size
        if not isinstance(sizes, (tuple, list)):
            sizes = (sizes,)
        return any(abs(c.get("size", 0) - s) < 0.1 for s in sizes)

    def _maybe_drop_running_header(self, page, lines):
        lines = self._join_wrapped_bylines(
            super()._maybe_drop_running_header(page, lines)
        )
        if page.page_number != 1 or self.efile_stamp_font is None:
            return lines
        kept = []
        for ln in lines:
            chars = ln.get("chars") or []
            stamp = [c for c in chars if self._is_stamp_char(c)]
            if not stamp:
                kept.append(ln)
                continue
            self._record_dropped(self.line_plain_text({"chars": stamp}).strip())
            rest = [c for c in chars if not self._is_stamp_char(c)]
            if rest:  # a mixed line (banner + stamp tail): keep the banner part
                kept.append(self._rebuild_line(ln, rest))
        return kept

    @staticmethod
    def _rebuild_line(ln, chars):
        new = dict(ln)
        new["chars"] = chars
        new["x0"] = min(c["x0"] for c in chars)
        new["x1"] = max(c["x1"] for c in chars)
        new["top"] = min(c["top"] for c in chars)
        new["bottom"] = max(c["bottom"] for c in chars)
        new["text"] = "".join(c["text"] for c in sorted(chars, key=lambda c: c["x0"]))
        return new

    # ---------------------------------------------------------------- byline
    def find_authors(self, all_segments) -> list:
        # Detect opinion starts ONLY via the strict form-based byline (not the
        # permissive parse_author_line, which exists only to label kind). Drop a
        # byline with no opinion body before the next one — that is the
        # trial-judge history line ('..., District Judge.') sitting just above
        # the real author, not an opinion.
        self._pc_starts = set()
        cands = [
            i
            for i, (_p, seg, _k) in enumerate(all_segments)
            if seg and self._byline_split(seg[0]) is not None
        ]
        # NO OPINION BEGINS ABOVE THE PANEL ROSTER. The roster introduces the
        # court's own writing, so everything over it is headmatter — and CA2
        # sets the TRIAL judge on a line of its own directly under the
        # appeal-from block ('Jed S. Rakoff, Judge.'), which is a name plus a
        # singular bench title plus a period and therefore indistinguishable
        # from an author byline by form. Read as one, it opened a phantom
        # opinion that swallowed the roster and the counsel block behind it.
        # The existing 'byline with no body' guard cannot catch this, because
        # real content does follow the trial judge.
        roster = self._panel_segment(all_segments)
        if roster is not None:
            cands = [i for i in cands if i > roster]
        out = []
        for n, i in enumerate(cands):
            end = cands[n + 1] if n + 1 < len(cands) else len(all_segments)
            if self._opinion_has_body(all_segments, i, end):
                out.append(i)
        if out:
            return out
        # No signed byline and no PER CURIAM / BY THE COURT line: an UNSIGNED per
        # curiam opinion. It opens immediately after the panel roster ('Before:
        # <judges>, Circuit Judges.'); author is PER CURIAM. Without this the
        # whole opinion would fall into the headmatter.
        start = self._percuriam_start(all_segments)
        if start is not None:
            self._pc_starts.add(start)
            return [start]
        return []

    def _percuriam_start(self, all_segments):
        """Index of the first opinion-body segment after the panel roster, for an
        unsigned per curiam opinion, or None. The roster is a single line opening
        'Before' that names the bench ('Before: WALKER, SULLIVAN, and BIANCO,
        Circuit Judges.'). The body is the next non-divider, non-empty segment."""
        panel = self._panel_segment(all_segments)
        if panel is None:
            return None
        for j in range(panel + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def _panel_segment(self, all_segments):
        """Index of the segment holding the panel roster, or None."""
        panel = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            # A ROSTER IS READ WHOLE, NOT BY ITS FIRST LINE. CA4 wraps it over
            # three ('Before WILKINSON, Circuit Judge, FLOYD, Senior Circuit
            # Judge, and David J. / NOVAK, United States District Judge for
            # the Eastern District of Virginia, sitting by / designation.'),
            # so the first line ends on 'J.' and the segment was rejected —
            # and with no roster found, nothing stopped the second line being
            # read as an opinion byline. The opinion then opened three rows
            # early and took the disposition and the appearances with it.
            low = " ".join(
                self.line_plain_text(l).strip() for l in seg
            ).lower()
            # The roster opens with a CAPITALISED 'Before' and closes on the
            # bench word. Matching the lower-cased text let body prose that
            # merely begins a sentence with it win — 'before an administrative
            # law judge ("ALJ"). Fletcher-Silvas argues …' was taken as the
            # roster, and because the last match wins the opinion then started
            # after it, stranding the whole opening paragraph in headmatter.
            if not t.startswith("Before"):
                continue

            def closes(s):
                # On the STRING, not the last token: a wrapped roster merges
                # its lines and the space can be lost ('sitting bydesignation').
                # THE BENCH WORD CAN CARRY A FOOTNOTE MARKER. CA9 hangs one on
                # the visiting judge ('Before: NGUYEN and VANDYKE, Circuit
                # Judges, and HUIE, District Judge.***'), and with the marker
                # left on, the roster did not close, no roster was found, and
                # nothing marked where the court's own writing began — the
                # whole memorandum stayed in the headmatter.
                return s.rstrip(".:;,*†‡∗ ").endswith(
                    ("judge", "judges", "designation")
                )

            # ...and where the roster's own lines are split into separate
            # segments (CA4 spaces them like ordinary prose), read forward
            # until it closes. Bounded: a roster is a line or three, never a
            # page, so a run that does not close is not a roster.
            last = i
            while not closes(low) and last + 1 < len(all_segments) and last - i < 3:
                last += 1
                nxt = all_segments[last][1]
                if not nxt:
                    break
                low += " " + " ".join(
                    self.line_plain_text(l).strip() for l in nxt
                ).lower()
            if "judge" not in low or not closes(low):
                continue
            panel = last
        return panel

    def build_opinion(self, op_start, op_end, **kwargs):
        # An unsigned per curiam start has no byline line; keep its first line as
        # body and label the author PER CURIAM (set via the _pc_now flag, which
        # split_author_line below reads while super() consumes the first line).
        self._pc_now = op_start in getattr(self, "_pc_starts", set())
        op = super().build_opinion(op_start, op_end, **kwargs)
        self._pc_now = False
        if op_start in getattr(self, "_pc_starts", set()):
            op.author = "PER CURIAM"
            op.type = self.normalize_opinion_type(None)
        return op

    def split_author_line(self, line):
        if getattr(self, "_pc_now", False):
            return "PER CURIAM", [line]  # no byline line — keep it as body
        return super().split_author_line(line)

    def _byline_at(self, line) -> bool:
        return self._byline_split(line) is not None

    def _byline_split(self, line):
        """Federal byline by FORM (not bold): '<Name>, <singular bench title>'
        immediately followed by '.'/':' (or end of line). Returns
        (byline_text, inline_body_text) or None. Excludes 'Before ... Judges.'
        rosters and headmatter labels."""
        text = (line.get("text") or "").strip()
        if not text:
            return None
        # A byline never OPENS with a lowercase letter. Without this, a wrapped
        # body line that happens to break at the right word reads as a per
        # curiam byline and starts a phantom opinion mid-paragraph — CA9's
        # 'by the Court in that case. Compare Terry Williams, 529 U.S. ...'
        # matched the 'BY THE COURT' form once uppercased.
        if text[:1].islower():
            return None
        up = text.upper()
        for bad in _NON_AUTHOR:
            if up.startswith(bad):
                if up.startswith("PER CURIAM"):
                    break
                return None
        if up.startswith("PER CURIAM") or up.startswith("BY THE COURT"):
            i = text.find(".")
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        if "," not in text:
            return None
        comma = text.index(",")
        name = text[:comma].strip()
        if not _is_name(name):
            return None
        for kw in _BENCH:
            # The bench title follows the NAME's comma, so search from there.
            # Searching from 0 let the title be found BEFORE the comma, which
            # made the continuation of a wrapped byline read as a byline of its
            # own ('Circuit Judge, joins, concurring:' — the tail of 'BERZON,
            # Circuit Judge, with whom W. FLETCHER, / Circuit Judge, joins,
            # concurring:' — parsed as judge 'Circuit Judge').
            start = comma + 1
            while True:
                idx = text.find(kw, start)
                if idx == -1:
                    break
                end = idx + len(kw)
                if end < len(text) and text[end] == "s":  # 'Judges' = panel
                    start = end
                    continue
                # Everything from the name's comma to the title keyword must be
                # title qualifiers (and a name suffix), not sentence text — else
                # this 'Judge' is incidental to a body line ('Moreover, ... must
                # be considered. Judge ...'), not a byline.
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
                # A DESIGNATED judge names the court they sit on before the
                # terminator: 'David J. NOVAK, United States District Judge for
                # the Eastern District of Virginia, sitting by designation:'.
                # Requiring the terminator straight after the title left that
                # byline unrecognised, so the whole majority opinion stayed in
                # the headmatter (ca4 rhino_energy: 1,060 rows, dissent only).
                # The qualifier is one clause — no sentence-ending period
                # inside it — so a body line can never be swept up.
                if text[j:].lstrip().lower().startswith(("for the", "of the")):
                    for term in (":", "."):
                        t = text.find(term, j)
                        if t != -1 and "." not in text[j:t]:
                            return text[: t + 1], text[t + 1 :].strip()
                start = end
        return None

    def _kind_clause_end(self, text: str, comma: int):
        """Index of the terminator closing a separate writing's kind clause, or
        None if what follows the bench title is not one.

        A majority byline puts its terminator straight after the title
        ('ROTH, Circuit Judge.'), but a concurrence or dissent names its kind
        there instead, joined by a comma:

            ROTH, Circuit Judge, dissenting.
            BOVE, Circuit Judge, concurring.
            SMITH, Circuit Judge, with whom JONES joins, dissenting in part.
            MASCOTT, Circuit Judge, dissenting sur denial of rehearing en banc.

        Requiring the '.'/':' immediately reads that comma as ordinary sentence
        text, so the writing is never detected as an opinion start at all — it
        is swept into whatever precedes it (on CA3, into the majority, and from
        there into the counsel trailer). ``_has_byline_form`` already documents
        this shape for the font-keyed circuits; this is the form-keyed half.

        Kept tight so a body line can never reach here: the clause must NAME a
        kind (a concur/dissent stem) and stay short. The name and the title run
        have already been vetted by the caller."""
        stop = len(text)
        for i in range(comma + 1, len(text)):
            if text[i] in ".:":
                stop = i
                break
        span = text[comma + 1 : stop]
        low = span.lower()
        if "concur" not in low and "dissent" not in low:
            return None
        # Long enough for the fullest real form — 'joined by RESTREPO and
        # FREEMAN, Circuit Judges, dissenting from the denial of rehearing en
        # banc' is 15 words — and still far short of a sentence.
        if len(span.split()) > 20:
            return None
        return min(stop, len(text) - 1)

    # Words that may sit between a judge's name and the bench title ('Senior
    # Circuit Judge', 'United States District Judge'), plus name suffixes
    # ('JAMES E. GRAVES, JR., Circuit Judge'). Anything else there means the
    # 'Judge' belongs to a sentence, not a byline.
    _TITLE_RUN_WORDS = frozenset(
        {
            "circuit", "senior", "chief", "district", "united", "states",
            "associate", "presiding", "acting", "supreme", "magistrate",
            "bankruptcy", "jr", "sr", "ii", "iii", "iv", "us",
        }
    )

    def _is_title_run(self, span: str) -> bool:
        for t in span.replace(",", " ").split():
            tl = t.strip(".").lower()
            if tl in self._TITLE_RUN_WORDS:
                continue
            if len(tl) == 1 and tl.isalpha():  # a 'J.' judicial / name initial
                continue
            return False
        return True

    def _has_byline_form(self, s: str) -> bool:
        """A name, a comma, then a singular bench title (Judge/Justice) reached
        through title qualifiers only — the byline shape, WITHOUT requiring a
        trailing '.'/':' terminator (a concurrence/dissent byline carries a kind
        suffix after the title: 'NAME, Circuit Judge, dissenting in part.'). The
        plural 'Judges' roster is rejected. Shared by the font-keyed per-court
        detectors (ca1, ca10) that delimit the byline by weight, not by form."""
        if "," not in s:
            return False
        comma = s.index(",")
        if not _is_name(s[:comma].strip()):
            return False
        for kw in _BENCH:
            idx = s.find(kw, comma)
            while idx != -1:
                end = idx + len(kw)
                if end < len(s) and s[end] == "s":  # 'Judges' = plural roster
                    idx = s.find(kw, end)
                    continue
                if self._is_title_run(s[comma + 1 : idx]):
                    return True
                idx = s.find(kw, end)
        return False

    def parse_author_line(self, text):
        """Parse a federal byline into (name, title, kind). Handles the period
        form via the base, plus the colon form ('PAN, Circuit Judge:') and a
        trailing kind ('..., concurring')."""
        r = super().parse_author_line(text)
        if r is not None:
            return r
        if not text:
            return None
        t = text.strip().rstrip(".:").strip()
        if t.upper().startswith("PER CURIAM"):
            return ("PER CURIAM", "per curiam", None)
        if t.upper().startswith("BY THE COURT"):
            return ("By the Court", "per curiam", None)
        if "," not in t:
            return None
        name, rest = t.split(",", 1)
        name, rest = name.strip(), rest.strip()
        # Guard against ordinary body lines ('Shortly after the officers entered
        # the residence, they found ...'): the name must look like a judge name
        # and the part after the comma must name a judicial office. Without this
        # every comma-bearing body line parsed as a byline, fragmenting the body.
        if not _is_name(name):
            return None
        # A surname is never itself a bench word. The wrapped continuation of a
        # byline-shaped sentence opens with the tail of the title ('Judge,
        # Joseph F. Bianco, and Michael H. Park, Circuit Judges, dissents by
        # opinion'), and reading 'Judge' as the name manufactured a byline
        # mid-sentence — a segment boundary that cut the sentence in half.
        if name.rstrip(".").lower() in _BENCH_WORDS:
            return None
        if not any(w in rest for w in ("Judge", "Justice", "Chancellor")):
            return None
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
        return (name.strip(), rest, kind)

    # ---------------------------------------------------------------- layout
    def filter_margins(self, obj):
        page_no = obj.get("page_number", 1)
        if page_no > 1 and obj.get("top", 0) < self.page2_header_cutoff:
            return None
        return super().filter_margins(obj)

    def split_body_paragraphs(self, seg):
        """New paragraph at a first-line indent (x0 > body_baseline_x0 + 12);
        baseline lines continue the prior paragraph."""
        if not seg:
            return []
        threshold = self.body_baseline_x0 + 12
        paras = [[seg[0]]]
        for i in range(1, len(seg)):
            indented = seg[i].get("x0", 0) >= threshold
            prev_indented = seg[i - 1].get("x0", 0) >= threshold
            if indented and not prev_indented:
                paras.append([seg[i]])
            else:
                paras[-1].append(seg[i])
        return paras

    def find_footnote_separator(self, page) -> Optional[float]:
        """~144pt hairline at x0~72 in the bottom 2/3. Reject candidates that
        share a y-band with other hairlines (citation underlines)."""
        return self._sep_at(page, 68, 80)

    def _sep_at(self, page, x_lo, x_hi):
        # The 'not near the top of the page' guard belongs to the CAPTION PAGE.
        # There it keeps a caption rule from reading as a footnote rule. On a
        # later page there is no caption to confuse, and the guard only does
        # harm: a LONG footnote starts high, so CA10's rule at 19% down page 35
        # was rejected and footnote 19 vanished — with coverage still reading
        # 100% because its prose matched elsewhere, and only the label sequence
        # (1-18, 20-22) showing anything was wrong.
        first_page = page.page_number == getattr(self, "_caption_pno", 1)
        floor = page.height * (0.30 if first_page else 0.10)
        rects = [r for r in page.rects if r["height"] < 2]
        rail = self._page_text_rail(page)
        cands = []
        for r in rects:
            if not (120 <= (r["x1"] - r["x0"]) <= 170 and r["top"] > floor):
                continue
            if any(o is not r and abs(o["top"] - r["top"]) <= 2 for o in rects):
                continue
            if x_lo <= r["x0"] <= x_hi:
                cands.append(r)
                continue
            # The x band is a property of the court's USUAL margin, not of the
            # footnote rule: measured across cadc, the rule starts at the page's
            # own left text rail in 371 of 377 cases — at 156 most of the time,
            # but at 72 and at 144 in documents set to a different measure. The
            # fixed 150-165 band rejected those outright, and eight cadc
            # documents delivered their footnotes as body prose in silence.
            #
            # Corroborated rather than merely widened: a rule away from the
            # configured band is taken only with footnote-sized text beneath it,
            # so a caption shelf or a table rule at the rail cannot pass.
            if rail is not None and abs(r["x0"] - rail) <= 4 and (
                self._rule_over_footnotes(page, r["top"])
                or self._labelled_note_below(page, r["top"])
            ):
                cands.append(r)
        return min(cands, key=lambda r: r["top"])["top"] if cands else None

    # ``_page_text_rail`` now lives on BaseExtractor — it was written here,
    # then copied into tex and _oregon on the same day. One copy.

    def matches_expected_layout(self, pdf) -> bool:
        if not pdf.pages:
            return False
        target = (self.circuit_phrase or "").lower()
        for line in pdf.pages[0].extract_text_lines():
            t = line.get("text") or ""
            if "United States Court of Appeals" in t:
                return True
            if target and target in t.lower():
                return True
        return False
