"""Office of Legal Counsel, U.S. Department of Justice ('olc').

THIS IS NOT A COURT'S PAPER. OLC issues no judgments and hears no parties;
it answers a question put to it by another part of the Executive Branch, in
a memorandum. There is no caption, no docket, no panel and no counsel — and
a reader that went looking for them would find, and mistint, prose. What the
slip sheet prints is a MEMORANDUM'S COVER, and it prints it the same way in
all 32 records of this corpus:

    ┌───────────────────────────────────────────────────────────┐
    │ (Slip Opinion)                                            │ the stamp
    │                                                           │
    │        Revocation of Prior Monument Designations          │ the QUESTION,
    │                                                           │ 12pt BOLD
    │ The Antiquities Act of 1906 permits a President to alter  │
    │    a prior declaration of a national monument, …          │ the HEADNOTE,
    │ The contrary conclusion of the Attorney General in        │ 9pt, one or
    │    Proposed Abolishment of Castle Pinckney …              │ more paras
    │                                                           │
    │                                     May 27, 2025          │ the DATE,
    │                                                           │ flush right
    │     MEMORANDUM OPINION FOR THE COUNSEL TO THE PRESIDENT   │ the ADDRESSEE
    │                                                           │
    │ In the midst of public concerns that the Pueblo ruins …   │ the memorandum
    └───────────────────────────────────────────────────────────┘

and it closes, at the foot of the last page of text, with

    LANORA C. PETTIT
    Deputy Assistant Attorney General
    Office of Legal Counsel

THE PAPER IS ONE STOCK AND ONE SIZE. Every record is a 423x657 slip sheet
with the text measure running 48.2 to 374.8 — so the measure's axis is
211.5, and every band of the cover is placed against it:

    band        type              placement
    stamp       9pt roman         at the rail, in the top band (furniture)
    title       12pt BOLD         centred on the measure axis, 1-4 rows
    headnote    9pt roman         a HANGING indent: the paragraph opens at
                                  the rail (48.2) and its runovers set to
                                  59.8, which is what separates one
                                  paragraph of the headnote from the next
    date        9pt roman         FLUSH RIGHT, ending at 374.x
    addressee   11pt CAPS         centred on the measure axis, 1-2 rows
    body        11pt roman        the measure, lower case

Counted over all 32 records: 32 '(Slip Opinion)' stamps, 32 bold titles, 32
headnotes, 32 flush-right dates, 32 'MEMORANDUM OPINION FOR …' addressees
and 32 signature blocks. There is no second format, and the reader claims
nothing it cannot name — a row this paper does not print is left to core.

THE DISPATCH IS THE ADDRESSEE, not the stamp and not the title. '(Slip
Opinion)' is a Government Printing Office stamp that many series carry, and
a bold centred line at the head of a page is the commonest thing in this
whole corpus. The row that can only be an OLC memorandum is the one that
says whom the memorandum is FOR, set in the body's own 11pt small caps
measure and centred on the measure axis. No addressee, no claim.

WHY THE ADDRESSEE IS HEADMATTER AND NOT THE OPINION'S FIRST LINE. The old
engine opened the writing on it, which reads it as prose the Office wrote;
it is not — it is the memorandum's 'TO' line, the cover's last row, and the
Office's prose begins under it with an indented first line. It is claimed
here with role 'caption', which is the role this model gives to the row
naming whom a paper is addressed to, and it is also offered back as the
ANCHOR: a memorandum whose body would not otherwise assemble gets it back
rather than losing its writing.

THE SIGNATURE IS READ ONLY WHERE IT CLOSES THE DOCUMENT. Two records are
signed by two officials (a three-row block twice over) and one —
department_of_agriculture_preferences — signs on page 25 of 44 and then
prints a 19-page Appendix. Lifting a signature out of the middle of a
document would put the Appendix before the signature that precedes it, so
the band is taken only when nothing but footnotes and furniture follows it.

WHAT THIS FILE DOES NOT DO. The footnotes, the paragraphing, the running
heads ('49 Op. O.L.C. __ (May 27, 2025)') and the author's name are all
core's; core already reads the signer's name off the closing block and it
is not re-derived here.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import learn_vocabulary
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

OLC = register(CourtProfile(
    "olc", "Office of Legal Counsel, U.S. Department of Justice",
    # ONE MEMORANDUM, ONE WRITING. There is no bench here, so there is
    # nothing to concur in or dissent from: every record is one opinion of
    # the Office, signed by one (occasionally two) Assistant Attorneys
    # General on behalf of it.
    single_writing=True,
    # The Office does not sign in the bench's grammar ('SMITH, J.:'); it
    # signs its name over its title at the FOOT of the memorandum, which
    # core reads as a closing signature. There is no byline to parse.
    byline=BylineGrammar(style="none"),
    # The memorandum's first lines indent ~11.5pt from the rail (48.2 ->
    # 59.8) on this small stock; the 12pt default swallowed them.
    para_indent_min=10.0,
    rollout="migrated",
))

# --- the stock, measured over all 32 records --------------------------------
_SHEET_W = 423.0            # the slip sheet
_RAIL = 48.2                # the text measure's left edge
_RIGHT = 374.8              # …and its right
_AXIS = (_RAIL + _RIGHT) / 2        # 211.5 — the measure's axis
_AXIS_TOL = 14.0
_RAIL_TOL = 2.5
_HEAD_SIZE = 9.0            # the headnote and the date
_TITLE_SIZE = 12.0          # the question
_BODY_SIZE = 11.0           # the memorandum, and its addressee
_SIZE_TOL = 0.6

# The addressee. 'MEMORANDUM OPINION FOR …' in 32 of 32; the Office's other
# published forms ('MEMORANDUM FOR …', 'LETTER OPINION FOR …') are named
# because they are the same row of the same cover, not because a record
# here uses them.
_ADDRESSEE = re.compile(
    r"^(MEMORANDUM OPINION FOR|MEMORANDUM FOR|LETTER OPINION FOR"
    r"|OPINION FOR)\b")
# 'May 27, 2025' — the only date the cover prints.
_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}\.?$")
# The Office naming itself under the signer's title. The signature band's
# last row in all 32 records, and the one landmark that identifies the band.
_OFFICE = re.compile(r"^Office of Legal Counsel$")
# THE RUNNING HEADS, which this Office sets verso/recto and which are the
# only place two facts appear at all: the VERSO carries the Office's own
# volume citation, the RECTO the short title the Office gave the opinion
# (32 of 32 records, from page 2 on). Both are furniture and stay Dropped —
# they are READ, never claimed.
_CITE_HEAD = re.compile(r"^\d+\s+Op\.\s*O\.L\.C\.\s")
# A SUSPENDED COMPOUND resuming after a line break: a bare connective and a
# word that carries its own hyphen ('and sex-based', 'or sex-neutral').
_SUSPENDED = re.compile(r"^(?:and|or|nor|to)\s+\S*[a-z]-[a-z]", re.I)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, furniture removed, grouped by baseline."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


def _is_caps(text: str) -> bool:
    """A row set in the addressee's capitals. Letters only — the row can
    carry a comma, a period or a '&'."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}
        self.signature: list = []

    def _row(self, group: list, role: str, align, joined: str = "") -> m.HmLine:
        parts = sorted(group, key=lambda l: l.x0)
        text = joined
        if not text:
            for part in parts:
                piece = line_markup(part)
                text = (text.rstrip() + " " + piece.lstrip()) \
                    if text.strip() else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def emit(self, group: list, role: str, align=m.Align.CENTER) -> None:
        if not group:
            return
        self.items.append(self._row(group, role, align))
        self.consumed.update(l.id for l in group)

    def emit_flow(self, lines: list, role: str, vocab=None) -> None:
        """One PARAGRAPH of the headnote, set as the page sets it: its rows
        joined into the sentence they are, its every line id carried. A
        merge that keeps the text and drops the provenance is the same
        unaccounted line as a row nobody read.

        THE HEADNOTE IS JUSTIFIED PROSE and breaks words at the measure
        ('identi-' / 'fied'), so the wrap is joined the way core joins a
        wrapped paragraph: the DOCUMENT'S OWN VOCABULARY decides whether the
        hyphen was the word's or the break's, and unproved the hyphen stays
        and the wrap WELDS. A hyphen that earns a space is the defect the
        `hyph` metric counts, and the criteria and the body must never
        disagree about a broken word."""
        if not lines:
            return
        parts: list[str] = []
        for line in lines:
            piece = line_markup(line).strip()
            if not piece:
                continue
            if parts and parts[-1].endswith(("-", "\u2013", "\u2014")):
                head = parts[-1]
                if vocab:
                    word = []
                    for ch in reversed(head[:-1]):
                        if ch.isalpha() or ch in "\u2019'":
                            word.append(ch)
                        else:
                            break
                    first = piece.split()[0].strip(
                        "\u201c\u201d\"'\u2019\u2018()[]{}.,;:!?")
                    if word and ("".join(reversed(word))
                                 + first).lower() in vocab:
                        parts[-1] = head[:-1] + piece
                        continue
                # A SUSPENDED COMPOUND keeps its space. 'race- and
                # sex-based' breaks after 'race-' and the hyphen is not a
                # word break at all — it stands in for the second half of a
                # compound the connective is about to complete. The shape is
                # closed and unmistakable: a bare connective followed by a
                # word that is ITSELF hyphenated ('and sex-based', 'or
                # sex-neutral'), which no ordinary line-break hyphen can
                # produce (a broken 'day-to-day' resumes 'to-day', with no
                # space after the connective). Welded, the headnote read
                # 'race-and sex-based' in department_of_agriculture.
                if _SUSPENDED.match(piece):
                    parts.append(piece)
                    continue
                parts[-1] = head + piece
                continue
            parts.append(piece)
        self.items.append(
            self._row(lines, role, m.Align.LEFT, joined=" ".join(parts)))
        self.consumed.update(l.id for l in lines)

    def sign_row(self, group: list) -> None:
        """One printed row of the closing band. Not `emit`: it closes the
        memorandum rather than opening it, and renders at order 60."""
        if not group:
            return
        self.signature.append(self._row(group, "signature", m.Align.CENTER))
        self.consumed.update(l.id for l in group)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "signature": self.signature, "anchor_ids": self.anchor,
                "doc_type_final": m.DocType.OPINION}


@decider("headmatter.read", court="olc")
def read_headmatter_olc(model, geom, **_):
    """Read the OLC memorandum's cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    if abs(page1.width - _SHEET_W) > 6:
        return NOTHING                  # not the Office's slip sheet
    body_x0 = geom.body_x0 if geom and geom.body_x0 else _RAIL
    body_size = geom.body_size if geom and geom.body_size else _BODY_SIZE
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if not rows:
        return NOTHING
    # THE DISPATCH: the addressee. Not a row count from the top — the
    # headnote runs 1 to 14 rows over the corpus, and a 14-row window read
    # four records' covers as unclaimable. The row is found by what it IS:
    # the body's 11pt capitals, centred on the measure axis, naming whom
    # the memorandum is for. Without it this is not an OLC memorandum and
    # core's shared walk is the better reading.
    addressee_at = None
    for i, group in enumerate(rows):
        text = _norm(" ".join(l.plain for l in group))
        if not _ADDRESSEE.match(text) or not _is_caps(text):
            continue
        size = max((l.size or 0.0) for l in group)
        mid = (min(l.x0 for l in group) + max(l.x1 for l in group)) / 2
        if abs(size - _BODY_SIZE) <= _SIZE_TOL and abs(mid - _AXIS) <= _AXIS_TOL:
            addressee_at = i
            break
    if addressee_at is None:
        return NOTHING
    vocab = learn_vocabulary(model)

    ctx = _Ctx()
    title_rows: list[str] = []
    para: list = []             # the headnote paragraph being gathered

    def flush() -> None:
        ctx.emit_flow(para, "summary", vocab)
        para.clear()

    for i, group in enumerate(rows):
        parts = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in parts))
        if not text:
            continue
        if i > addressee_at:
            break                        # the memorandum itself
        size = max((l.size or 0.0) for l in parts)
        x0 = min(l.x0 for l in parts)
        x1 = max(l.x1 for l in parts)
        centred = abs((x0 + x1) / 2 - _AXIS) <= _AXIS_TOL

        # THE ADDRESSEE, and the rows it wraps onto: the cover's last band,
        # 11pt capitals centred on the measure axis. It ends at the first
        # row that is not in capitals, which is the Office's own prose.
        if i == addressee_at:
            flush()
            band = [parts]
            for nxt in rows[i + 1:i + 3]:
                nxt = sorted(nxt, key=lambda l: l.x0)
                ntext = _norm(" ".join(l.plain for l in nxt))
                nsize = max((l.size or 0.0) for l in nxt)
                ncent = abs((min(l.x0 for l in nxt) + max(l.x1 for l in nxt))
                            / 2 - _AXIS) <= _AXIS_TOL
                if (abs(nsize - _BODY_SIZE) <= _SIZE_TOL and ncent
                        and _is_caps(ntext)):
                    band.append(nxt)
                else:
                    break
            printed = []
            for row in band:
                ctx.emit(row, "caption")
                # THE ANCHOR. Released, the cover loses its last row;
                # withheld, a memorandum whose body will not assemble loses
                # its writing.
                ctx.anchor.extend(l.id for l in row)
                printed.append(_norm(" ".join(l.plain for l in row)))
            ctx.crit["caption"] = printed
            ctx.crit.setdefault("title", "Memorandum Opinion")
            # THE ADDRESSEE IS THE COVER'S LAST BAND, so the walk is over.
            # Resuming it re-entered this branch on the band's own second
            # and third rows and emitted them a second time
            # (application_of_18_u.s.c._209 printed 'OFFICE OF PERSONNEL
            # MANAGEMENT' twice).
            break

        # THE TITLE: the question, 12pt bold, centred on the measure axis.
        if abs(size - _TITLE_SIZE) <= _SIZE_TOL and centred:
            flush()
            title_rows.append(text)
            ctx.emit(parts, "title")
            continue

        # THE DATE: 9pt, flush right against the measure.
        if (abs(size - _HEAD_SIZE) <= _SIZE_TOL
                and abs(x1 - _RIGHT) <= 2.0 and x0 > _AXIS
                and _DATE.match(text)):
            flush()
            ctx.crit.setdefault("decision_date", text.rstrip("."))
            ctx.emit(parts, "date", align=m.Align.RIGHT)
            continue

        # THE HEADNOTE: 9pt with a HANGING indent. A row at the rail opens a
        # paragraph; a row at the runover edge continues it.
        if abs(size - _HEAD_SIZE) <= _SIZE_TOL and x0 < _AXIS:
            if abs(x0 - _RAIL) <= _RAIL_TOL:
                flush()
            para.extend(parts)
            continue

        # A ROW AT NO POSITION THIS COVER USES is left to core rather than
        # tinted with a role that would be a guess.
        flush()
    flush()

    if title_rows:
        ctx.crit.setdefault("case_name", _norm(" ".join(title_rows)))
    ctx.crit["court"] = OLC.court_label
    ctx.crit["headmatter_style"] = "olc-memorandum"
    _read_running_heads(ctx, model, finder)
    _read_signature(ctx, model, finder)
    return ctx.result()


def _read_running_heads(ctx: _Ctx, model, finder) -> None:
    """The verso citation and the recto short title, read off the furniture.

    Not claimed and not placed: core has already recorded both as running
    heads, and a reader that placed them would print them twice. But they
    are the ONLY place the Office states its own volume citation ('49 Op.
    O.L.C. __ (May 27, 2025)') and the only place it states the short form
    of the title, and a criterion the page prints is not junk merely
    because the row it prints on is."""
    for pm in model.pages[1:6]:
        for line in sorted(pm.lines, key=lambda l: l.top)[:2]:
            if finder.kind(pm, line) != "running-head":
                continue
            text = _norm(line.plain)
            if _CITE_HEAD.match(text):
                ctx.crit.setdefault("citation", text)
            elif text:
                ctx.crit.setdefault("short_case_name", text)


def _read_signature(ctx: _Ctx, model, finder) -> None:
    """The closing band — NAME over TITLE over 'Office of Legal Counsel' —
    taken only where nothing but footnotes and furniture follows it."""
    pages = model.pages
    if not pages:
        return
    last = pages[-1]
    rows = _rows(last, finder)
    marks = [i for i, g in enumerate(rows)
             if _OFFICE.match(_norm(" ".join(l.plain for l in g)))]
    if not marks:
        return
    end = marks[-1]
    # NOTHING BUT SMALLER TYPE BELOW IT. A footnote zone may follow the
    # signature on its own page; a paragraph of the memorandum may not.
    body_size = max((max((l.size or 0.0) for l in g) for g in rows[:end + 1]),
                    default=_BODY_SIZE)
    for group in rows[end + 1:]:
        if max((l.size or 0.0) for l in group) >= body_size - _SIZE_TOL:
            return
    # …and the band is a run of rows centred on the SIGNATURE's own axis,
    # which this Office sets at 264.1 on every record — right of the
    # measure's axis, not on it.
    axis = None
    for group in rows[end::-1]:
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        mid = (x0 + x1) / 2
        if axis is None:
            axis = mid
        if abs(mid - axis) > 6.0 or x0 < _AXIS - 60:
            break
    start = end
    while start > 0:
        group = rows[start - 1]
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        if abs((x0 + x1) / 2 - axis) > 6.0 or x0 <= _RAIL + 4:
            break
        start -= 1
    if start == end:
        return                       # a lone office line is not a signature
    for group in rows[start:end + 1]:
        ctx.sign_row(sorted(group, key=lambda l: l.x0))
