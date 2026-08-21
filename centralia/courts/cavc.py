"""United States Court of Appeals for Veterans Claims ('cavc').

THE CONTRACT — 'masthead ladder'. The Veterans Court prints ONE cover and
prints it in one fixed order under a single landmark: it names itself, in
caps, across the head of page 1. Everything below that row is a rung of a
ladder, and every rung is identified by something the court PRINTS, never by
what a case is about:

    Case: 24-9605   Page: 1 of 10   Filed: 05/13/2026   the ECF stamp (a Drop)
    UNITED STATES COURT OF APPEALS FOR VETERANS CLAIMS  the masthead
    NO. 24-9605                                         the docket
    ANNETTE S. HUBBELL,               APPELLANT,        the caption…
    V.                                                  …its pivot…
    DOUGLAS A. COLLINS,
    SECRETARY OF VETERANS AFFAIRS,    APPELLEE.         …and the other side
    On Appeal from the Board of Veterans' Appeals       the origin
    (Argued April 29, 2026            Decided July 15, 2026)     the dates
    Amy F. Odom, of Providence, Rhode Island, for the appellant. appearances
    Before ALLEN, Chief Judge, and BARTLEY and LAURER, Judges.   the panel
    O R D E R                              the WRITING's own heading
    LAURER, Judge, filed the opinion of the Court. …     the announcement
    LAURER, Judge: Context matters. …                    the first byline

FOUR MEASUREMENTS DO ALL OF THE WORK, and none of them reads a case.

 1. THE MASTHEAD. The court's own name, set across the head of page 1. It
    is the only landmark that identifies the contract, so a record that does
    not open with it gets NOTHING and core's shared walk keeps it.

 2. THE PARAGRAPH INDENT IS THE BAND. The court sets its appearances, its
    roster and its announcement as ordinary hanging paragraphs — first row
    at the half-inch indent (x0=108), every runover at the body rail
    (x0=72). That one fact joins a three-row appearance, a wrapped roster
    and stinson's five-row announcement without a word being read. Where
    the court CENTRED the roster instead (stinson, wells) the band runs on
    while its sentence is unfinished and stops at the next landmark.

 3. AN APPEARANCE OPENS ON AN ITALIC NAME. cavc italicizes counsel's name
    and nothing else at the head of a row on the cover. It is a typeface
    fact, and it is what tells the appearances from the prose of an order.

 4. THE WRITING'S OWN OPENING ENDS THE READER. Two forms, and the court
    prints exactly one of them:
      - 'O R D E R', letter-spaced and centred. It is the ORDER'S OWN
        HEADING, not a section label of the cover: it is what anchors an
        unsigned per curiam order, so the reader stops ABOVE it and never
        claims it. (The old engine put it in the writing too.)
      - a byline — 'LAURER, Judge:', 'PER CURIAM:', 'BARTLEY, Chief Judge:'.

    THE ANNOUNCEMENT IS NOT A BYLINE. 'LAURER, Judge, filed the opinion of
    the Court. BARTLEY, Senior Judge, filed a dissenting opinion, which TOTH
    and JAQUITH, Judges, joined.' names who wrote what; it is a summary of
    the paper, and on the eight opinion covers it stands between the roster
    and the real byline. Read as a byline it opens a phantom writing that
    takes the majority's whole body — which is what 'PER CURIAM. TOTH,
    Judge, filed a concurring opinion.' did to atilano. It is told from a
    byline by the FILING VERB, a closed vocabulary, and it is claimed as
    `summary` so the real byline below it opens the writing.

    Where the court headed the paper 'O R D E R' the announcement stands
    BELOW that heading and therefore inside the writing, and the reader
    never reaches it.

TWO CAPTION SETTINGS, one contract. Nineteen records centre every caption
row on the page axis; five range the party at the body rail and set its
STATUS flush right (x0≈396) on the same baseline. pdfio splits that printed
row at its gutter, so pieces that share a baseline are re-joined into one
visual row before anything is read — otherwise 'APPELLANT,' reads as a row
of its own and the caption loses its order.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import learn_vocabulary, line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import FOOTNOTE_LABEL_CHARS, line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

CAVC = register(CourtProfile(
    "cavc", "United States Court of Appeals for Veterans Claims",
    # The bench of the Veterans Court: Judge, Chief Judge, Senior Judge.
    # Without the profile `get_profile()` hands back the default
    # `titles=('Justice',)`, every 'LAURER, Judge:' parses as nothing, and
    # a signed precedential opinion is typed 'order' — 6 of the 24 records.
    byline=BylineGrammar(
        style="prose",
        titles=("Chief Judge", "Senior Judge", "Judge", "Judges")),
    rollout="migrated",
))

STYLE_MASTHEAD_LADDER = "masthead ladder"

# ---- cavc's declared facts (measured over the 24-record corpus) ----------
# THE MASTHEAD, as the court sets it. One string, its own name.
_MASTHEAD = "UNITED STATES COURT OF APPEALS FOR VETERANS CLAIMS"
# THE PARAGRAPH INDENT: half an inch off the 72pt body rail. Every hanging
# band on the cover — appearances, roster, announcement — opens here and
# runs over at the rail.
_INDENT = 36.0
_RAIL_SLOP = 3.5
# Pieces that share a baseline are ONE printed row (the ranged caption's
# flush-right status, the '(Argued … Decided …)' pair).
_ROW_BAND = 2.5
# The cover never leaves page 1 in this corpus; the deepest is boehringer's
# announcement at top 416 on a 792pt page. Page 2 is read only so a cover
# that overran would not be cut in half — the walk ends at the writing's
# opening either way.
_MAX_PAGES = 2
# An italic run this long at the head of a row is counsel's name.
_ITALIC_MIN_GLYPHS = 3
# How far a centred band may run on an unfinished sentence.
_RUNON_MAX_ROWS = 3

# THE DOCKET, as the court prints it: 'NO. 24-9605', 'No. 17-1428',
# 'NO. 20-8342(E)', 'NO.  25-4538'.
_DOCKET = re.compile(r"^NOS?\.\s*(\d{2}-\d{3,5}(?:\([A-Z]\))?)"
                     r"((?:\s*[,;]\s*\d{2}-\d{3,5}(?:\([A-Z]\))?)*)\.?$",
                     re.I)
# THE ORIGIN — how cavc names what it is reviewing. Only the opener is read;
# the tribunal itself never is.
_ORIGIN_OPENERS = (
    "on appeal from", "on appeals from", "on remand from",
    "on petition for review", "on petitions for review",
    "on review of", "on certification from", "on appeal of",
)
# THE DATE BAND, parenthesised: '(Argued April 29, 2026', 'Decided July 15,
# 2026)', '(Decided November 3, 2022)'.
_DATE_LABELS = ("argued and submitted", "reargued", "argued", "submitted",
                "decided", "filed")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# THE WRITING'S OWN HEADING. Letter-spaced by the court, so it is read
# through _squeeze; centred and alone on its row.
_WRITING_HEADINGS = ("ORDER", "OPINION", "MEMORANDUM DECISION",
                     "PER CURIAM ORDER", "ORDER AND OPINION",
                     "OPINION AND ORDER", "JUDGMENT")
# THE ANNOUNCEMENT — who filed what. The FILING VERB is the discriminator
# and it is a closed vocabulary; the names either side of it are never read.
_ANNOUNCE = re.compile(
    r"^(?:PER\s+CURIAM\.\s+)?"
    r"[A-Z][A-Za-z.'’\-]*(?:\s+[A-Z][A-Za-z.'’\-]*)*,\s+"
    r"(?:Chief\s+|Senior\s+|Acting\s+)?Judges?,\s+"
    r"(?:filed|authored|joined|delivered)\b")
_ANNOUNCE_PC = re.compile(r"^PER\s+CURIAM\.\s+\S")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "movant",
    "movants", "claimant", "claimants", "amicus", "amici",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
_PIVOT = ("v.", "vs.", "v", "versus")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    """'O R D E R' -> 'ORDER'."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _visual_rows(lines: list) -> list:
    """``lines`` (page order) grouped into the rows the page printed."""
    out: list = []
    for line in lines:
        if out and out[-1][0].page == line.page \
                and abs(out[-1][0].top - line.top) <= _ROW_BAND:
            out[-1].append(line)
        else:
            out.append([line])
    for row in out:
        row.sort(key=lambda l: l.x0)
    return out


def _plain(row: list) -> str:
    text = ""
    for line in row:
        piece = _norm(line.plain)
        if not piece:
            continue
        text = (text + "  " + piece) if text else piece
    return text


def _markup(row: list) -> str:
    text = ""
    for line in row:
        piece = line_markup(line)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    return text


def _join(texts: list, vocab: set | None = None) -> str:
    """Join a band's rows the way the page reads. A row broken on a hyphen
    is welded only when the DOCUMENT'S OWN VOCABULARY proves the word."""
    out = ""
    for piece in texts:
        piece = _norm(piece)
        if not piece:
            continue
        if not out:
            out = piece
            continue
        if out.endswith(("-", "–", "—")):
            if vocab:
                word = []
                for ch in reversed(out[:-1]):
                    if ch.isalpha() or ch in "’'":
                        word.append(ch)
                    else:
                        break
                head = piece.split()[0].strip(
                    "“”\"'’‘()[]{}.,;:!?")
                if word and ("".join(reversed(word)) + head).lower() in vocab:
                    out = out[:-1] + piece
                    continue
            out += piece
        else:
            out += " " + piece
    return out


def _ends_sentence(text: str) -> bool:
    flat = _norm(text).rstrip()
    while flat and flat[-1] in FOOTNOTE_LABEL_CHARS:
        flat = flat[:-1].rstrip()
    return flat.endswith((".", ":", "!", "?"))


def _is_masthead(text: str) -> bool:
    return _norm(text).upper().rstrip(".") == _MASTHEAD


def _opens_italic(line) -> bool:
    """Does this row OPEN on an italic name? cavc italicizes counsel's name
    and nothing else at the head of a cover row."""
    glyphs = 0
    for ch in (line.chars or ()):
        text = ch.get("text") or ""
        if not text.strip():
            if glyphs:
                continue
            return False
        font = ch.get("fontname") or ""
        if "Italic" not in font and "Oblique" not in font:
            return glyphs >= _ITALIC_MIN_GLYPHS
        if text.isalpha():
            glyphs += 1
    return glyphs >= _ITALIC_MIN_GLYPHS


def _docket_numbers(text: str) -> list:
    hit = _DOCKET.match(_norm(text))
    if hit is None:
        return []
    out = [hit.group(1)]
    for extra in re.split(r"[,;]", hit.group(2) or ""):
        extra = extra.strip()
        if extra:
            out.append(extra)
    return out


def _is_origin(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _labelled_dates(text: str) -> dict:
    """{'argued': 'April 29, 2026', 'decided': 'July 15, 2026'}."""
    flat = _norm(text)
    if len(flat) > 140:
        return {}
    low = flat.lower()
    hits = []
    for label in _DATE_LABELS:
        at = low.find(label)
        if at < 0:
            continue
        if at and low[at - 1].isalnum():
            continue
        hits.append((at, label))
    if not hits:
        return {}
    hits.sort(key=lambda p: (p[0], -len(p[1])))
    picked: list = []
    for at, label in hits:
        if picked and at < picked[-1][0] + len(picked[-1][1]):
            continue
        picked.append((at, label))
    out: dict = {}
    for i, (at, label) in enumerate(picked):
        end = picked[i + 1][0] if i + 1 < len(picked) else len(flat)
        seg = flat[at + len(label):end]
        found = re.search(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})", seg)
        if found is None:
            continue
        if found.group(1).split()[0].strip(".,").lower() not in _MONTHS:
            continue
        out[label.replace(" ", "_")] = _norm(found.group(1))
    return out


def _is_date_row(text: str) -> bool:
    """The court's parenthesised date band, and only that: a date inside the
    prose of an order is an ordinary sentence."""
    flat = _norm(text)
    if not flat.startswith("("):
        return False
    return bool(_labelled_dates(flat))


def _is_panel(text: str) -> bool:
    return _norm(text).lower().startswith(("before ", "before:"))


def _is_writing_heading(row: list, page_width: float) -> bool:
    """'O R D E R' — the heading of the writing it opens, alone on a centred
    row. It is never claimed; it is what anchors an unsigned order."""
    if len(row) != 1:
        return False
    flat = _norm(row[0].plain)
    if len(flat) > 40 or _squeeze(flat) not in _WRITING_HEADINGS:
        return False
    mid = (row[0].x0 + row[0].x1) / 2
    return abs(mid - page_width / 2) <= 40.0


def _is_announcement(text: str) -> bool:
    flat = _norm(text)
    if _ANNOUNCE.match(flat):
        return True
    return bool(_ANNOUNCE_PC.match(flat)
                and re.search(r"\b(?:filed|authored|joined)\b", flat))


def _bare(text: str) -> str:
    flat = _norm(text)
    while flat and (flat[-1] in ".*:, " or flat[-1] in FOOTNOTE_LABEL_CHARS):
        flat = flat[:-1]
    return flat.strip()


def _bare_words(text: str) -> list:
    return [w.strip(".,;:*†‡§'’\"()0123456789").lower()
            for w in text.split()]


def _panel_names(text: str) -> list:
    """The judges a 'Before …' roster names. Split on the court's own
    punctuation and drop the fragments that are TITLES — a closed bench
    vocabulary, never a case test."""
    flat = _norm(text)
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    body = flat
    for opener in ("before:", "before"):
        if body.lower().startswith(opener):
            body = body[len(opener):]
            break
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        piece = _bare(chunk)
        if not piece:
            continue
        if any(w in _TITLE_WORDS for w in _bare_words(piece)):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = _bare(part)
            if name.lower().startswith("and "):
                name = _bare(name[4:])
            if not name or not any(c.isalpha() for c in name):
                continue
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _strip_status(text: str) -> str:
    """A party's NAME, with its role label taken off. The label is a closed
    vocabulary; the name is never read."""
    flat = _norm(text).rstrip(".,")
    parts = [p.strip() for p in flat.split(",")]
    while parts and (not parts[-1]
                     or parts[-1].lower().rstrip(".") in _STATUS_WORDS):
        parts.pop()
    return ", ".join(p for p in parts if p)


def _is_pivot(text: str) -> bool:
    return _norm(text).lower().rstrip(",") in _PIVOT


@decider("headmatter.read", court="cavc")
def read_headmatter_cavc(model, geom, **_):
    """Read cavc's masthead-ladder cover, or NOTHING.

    NOTHING is returned for anything that does not open with the court's own
    masthead: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    vocab = learn_vocabulary(model)
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CAVC.byline)
    pages = {pm.number: pm for pm in model.pages}
    indent = body_x0 + _INDENT

    lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # The ECF overlay ('Case: 24-9605  Page: 1 of 10  Filed: …') and
            # the folio. Core measures and records those; the reader steps
            # over them so it never claims a row it did not read.
            if finder.kind(pm, line):
                continue
            lines.append(line)
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    if not lines:
        return NOTHING
    rows = _visual_rows(lines)
    if not any(_is_masthead(_plain(r)) for r in rows[:3]):
        return NOTHING                    # not this court's stationery

    crit: dict = {"headmatter_style": STYLE_MASTHEAD_LADDER}
    items: list = []
    consumed: set[int] = set()
    # NO ANCHOR IS EVER CLAIMED. 'O R D E R' stands below the reader's last
    # row and belongs to the writing it opens, so the anchor an unsigned
    # order needs is never taken away and never has to be given back.
    anchor_ids: list = []

    masthead_rows: list = []
    caption_rows: list = []
    caption_sides: list = [[]]
    origin_rows: list = []
    counsel_rows: list = []
    panel_rows: list = []
    announce_rows: list = []
    dockets: list = []
    dates: dict = {}

    def emit(row: list, role: str):
        first = row[0]
        pm = pages[first.page]
        align = line_alignment(first, pm.width, geom)
        # A ROW MADE OF PIECES SPANS ITS MEASURE: the ranged caption's party
        # sits at the rail and its status flush right, and the joined row is
        # neither centred nor right — it is the printed line.
        if len(row) > 1:
            align = "L" if abs(first.x0 - body_x0) <= _RAIL_SLOP else align
        items.append(m.HmLine(
            text=_markup(row), prov=m.Prov(first.page,
                                           tuple(l.id for l in row)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(l.all_bold for l in row), role=role))
        consumed.update(l.id for l in row)

    def runs_over(row: list, opener_x0: float) -> bool:
        """Is this row the runover of the hanging band above it? The court
        opens a band at the half-inch indent and runs it over at the rail."""
        return (abs(opener_x0 - indent) <= _RAIL_SLOP
                and abs(row[0].x0 - body_x0) <= _RAIL_SLOP)

    i = 0
    n = len(rows)
    stopped = False
    while i < n:
        row = rows[i]
        pm = pages[row[0].page]
        text = _plain(row)

        # ---- the writing's own opening ends the reader --------------------
        if _is_writing_heading(row, pm.width or 612.0):
            stopped = True
            break
        if not _is_announcement(text) and parser.parse(text) is not None:
            stopped = True
            break

        if _is_masthead(text):
            masthead_rows.append(text)
            emit(row, "court")
            i += 1
            continue
        numbers = _docket_numbers(text)
        if numbers:
            dockets.extend(numbers)
            emit(row, "docket")
            i += 1
            continue
        if _is_origin(text):
            origin_rows.append(text)
            emit(row, "lower-court")
            i += 1
            continue
        if _is_date_row(text):
            dates.update(_labelled_dates(text))
            emit(row, "date")
            i += 1
            continue

        # ---- the hanging bands: roster, announcement, appearances ---------
        band_role = None
        if _is_panel(text):
            band_role = "panel"
        elif _is_announcement(text):
            band_role = "summary"
        elif _opens_italic(row[0]) and (caption_rows or origin_rows or dates):
            band_role = "counsel"
        if band_role is not None:
            opener_x0 = row[0].x0
            band = [text]
            emit(row, band_role)
            i += 1
            runon = 0
            while i < n:
                nxt = rows[i]
                nxt_text = _plain(nxt)
                if nxt[0].page != row[0].page:
                    break
                if runs_over(nxt, opener_x0):
                    pass
                elif (not _ends_sentence(band[-1])
                      and runon < _RUNON_MAX_ROWS
                      and not _is_landmark(nxt, nxt_text, pages, parser)):
                    # A band the court CENTRED runs on while its sentence is
                    # unfinished (stinson's roster wraps to a centred row).
                    runon += 1
                else:
                    break
                band.append(nxt_text)
                emit(nxt, band_role)
                i += 1
            if band_role == "panel":
                panel_rows.extend(band)
            elif band_role == "summary":
                announce_rows.extend(band)
            else:
                counsel_rows.extend(band)
            continue

        # ---- everything else on the ladder is the caption -----------------
        # Bounded: the caption band closes at the first landmark above, and
        # the walk has already ended at the writing's opening.
        if counsel_rows or panel_rows or announce_rows:
            break                         # a row this contract does not name
        caption_rows.append(text)
        if _is_pivot(text):
            caption_sides.append([])
        else:
            caption_sides[-1].append(text)
        emit(row, "caption")
        i += 1

    if not stopped:
        # The cover must end at the writing the court opened. Without that
        # the reader has no bound and would claim a body.
        return NOTHING

    # ---- what the block says ---------------------------------------------
    if masthead_rows:
        crit["court"] = _join(masthead_rows)
    if caption_rows:
        crit["caption"] = caption_rows
        sides = [_join(s, vocab) for s in caption_sides if s]
        if sides:
            crit["parties"] = sides
            names = [_strip_status(s) for s in sides]
            crit["case_name"] = " v. ".join(n for n in names if n)
    if origin_rows:
        crit["lower_court"] = _join(origin_rows, vocab)
    if dockets:
        crit["docket_number"] = dockets[0]
        others = [d for d in dockets[1:] if d != dockets[0]]
        if others:
            crit["other_dockets"] = others
    for label, value in dates.items():
        if label in ("decided", "filed"):
            crit.setdefault("decision_date", value)
        elif label in ("argued", "submitted", "argued_and_submitted",
                       "reargued"):
            crit.setdefault("submitted", value)
    if panel_rows:
        printed = _join(panel_rows, vocab)
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _join(counsel_rows, vocab)[:4000]

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": [], "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _is_landmark(row: list, text: str, pages: dict, parser) -> bool:
    """Does this row open a rung of its own? The run-on rule needs it: a
    centred band the court left unterminated still ends where the next
    landmark starts."""
    pm = pages[row[0].page]
    if _is_writing_heading(row, pm.width or 612.0):
        return True
    if _is_masthead(text) or _docket_numbers(text) or _is_origin(text):
        return True
    if _is_date_row(text) or _is_panel(text) or _is_announcement(text):
        return True
    return parser.parse(text) is not None
