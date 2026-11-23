"""Supreme Court of the United States — the U.S. Reports PRELIMINARY PRINT.

A PAPER, not a court (see `courts.PAPERS`). The Reporter of Decisions
publishes each decision twice: the slip opinion on decision day, which
`courts/scotus.py` reads, and months later the preliminary print — the same
words set as the bound volume will set them. `scotus.py`'s `source.paper`
decider routes a print here; the record still reports court 'scotus'.

The print shares almost no layout fact with the slip
(notes/scotus-preliminary-print-vs-slip.md):

    p.1        COVER — 'PRELIMINARY PRINT / Volume 606 U. S. Part 2 /
               Pages 942–945 / OFFICIAL REPORTS OF THE SUPREME COURT', the
               date, the Reporter's name, a notice. Apparatus, whole.
    p.2 head   '942  OCTOBER TERM, 2024' over the section name ('Syllabus').
    caption    ONCE, mixed case, 11pt: 'GOLDEY, ASSOCIATE WARDEN, et al. v.
               FIELDS' / 'et al.' — no banner, no rules, no bracketed date.
    origin     small caps, 11pt: 'on petition for writ of certiorari to the
               united' / 'states court of appeals for the fourth circuit'.
    docket     one 9pt row, docket and dates: 'No. 23–1239. Argued January
               22, 2025—Decided May 15, 2025' (a '*' calls a 'Together with'
               note for the companion dockets).
    syllabus   9pt, straight on from the docket row, through the disposition
               and the lineup ('Kagan, J., delivered the opinion …') — and
               it SHARES its last page with what follows.
    counsel    argued cases only, 11pt: '… argued the cause for petitioner.'
               with a '*' note naming every amicus brief, which runs on
               into the footnote zone of the opinion's first page.
    writings   title-case bylines ('Justice Kagan delivered …', 'Per
               Curiam.'), each opening under the last — no cover per writing.
    last page  the REPORTER'S NOTE: the edits made since the slip.
    every page 'Page Proof Pending Publication', 21.7pt, stamped through the
               text (lifted out of the glyph stream by pdfio; the copies
               that stand clear of any text are dropped here).

Everything from the cover to the first byline is read here and CLAIMED;
the writings are core's, exactly as for any other court.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.headmatter import _hm_line
from . import register_paper

PAPER = "scotus.prelim"

register_paper(CourtProfile(
    PAPER, "Supreme Court of the United States",
    # 'Justice Kagan delivered the opinion of the Court.' / 'Chief Justice
    # Roberts …' / 'Justice Thomas, with whom Justice Alito joins,
    # dissenting.' — the slip's caps grammar matches none of them.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("Chief Justice", "Justice"),
                         allow_titlecase_name=True),
    front_matter=("syllabus",),
    para_indent_min=8.0,
    caption_wraps=True,
    signatures=False,
))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _rows(pm) -> list:
    return sorted((l for l in pm.lines if l.plain.strip()),
                  key=lambda l: (l.top, l.x0))


_WATERMARK = "page proof pending publication"


def _is_watermark(line) -> bool:
    return _norm(line.plain).lower() == _WATERMARK


# The first writing's byline ends the front matter. Only the FIRST byline
# matters here, and it is always one of these: the lead opinion is
# delivered or announced, or the Court speaks per curiam.
_FIRST_BYLINE = re.compile(
    r"^(?:per curiam\.?$|(?:chief )?justice [A-Z][\w’'.-]*"
    r"(?:,| delivered| announced))", re.I)

# What the origin opens on, in the closed vocabulary the Court prints.
_ORIGIN_OPENERS = ("on writ of certiorari", "on petition for", "on appeal",
                   "on appeals", "on application", "on motion",
                   "on writs of certiorari", "certiorari to", "appeal from",
                   "appeals from", "on request for", "on the application",
                   "on bill of complaint", "on exceptions", "on order",
                   "on certificate", "on certified question")

_DOCKET = re.compile(r"^Nos?\.\s*\S")
_DATE_IN_ROW = re.compile(
    r"\b(Argued|Submitted|Reargued|Decided|Filed)\b[^A-Za-z0-9]{0,4}"
    r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})")
_VOLUME = re.compile(r"^Volume\s+(\d+)\s+U\.\s*S\.")
_PAGES = re.compile(r"^Pages?\s+(\d+)")
_TOGETHER = re.compile(r"Together with Nos?\.\s*([^,]+(?:,\s*\d[^,]*)*)")
_DOCKET_NO = re.compile(r"\d{1,3}[A-Z]?[–-]\d+(?:,\s*Orig\.)?|\d+,\s*Orig\.")
_LABEL = re.compile(r"^(?:\d{1,3}|[*†‡§]+)\s")


def is_preliminary_print(model) -> bool:
    """Page 1 opens 'PRELIMINARY PRINT' and names the OFFICIAL REPORTS."""
    if not model.pages:
        return False
    rows = [_norm(l.plain) for l in _rows(model.pages[0])]
    return (bool(rows) and rows[0].upper() == "PRELIMINARY PRINT"
            and any(r.upper().startswith("OFFICIAL REPORTS")
                    for r in rows[:8]))


def _zone_top(pm, geom) -> float | None:
    """Where the page's footnotes begin: the Court separates them with a
    short rule (50pt, flush left) — never a full-measure one. Anywhere
    below the running head: a note that fills a counsel page opens at a
    quarter of the way down (Barnes, 605 U. S. 73, p.4)."""
    column = (geom.column if geom else 300.0) or 300.0
    rules = [r for r in pm.h_rules
             if (r.x1 - r.x0) < 0.4 * column and r.top > pm.height * 0.2]
    return min((r.top for r in rules), default=None)


def _paragraphs(lines: list, right: float) -> list[list]:
    """Lines → paragraphs, by the paper's own setting.

    A paragraph's SECOND line states its runover edge; a later line off that
    edge opens a new paragraph. That one rule reads all three settings the
    print uses: the syllabus's hanging 'Held:' (out 155, runovers 164), its
    indented paragraphs (173 / 164) and the lineup and counsel (164 or 166 /
    155). A short line closing a sentence, or a gap wider than the lead,
    ends a paragraph too."""
    paras: list[list] = []
    runover = None
    prev = None
    for line in lines:
        new = prev is None
        if not new:
            lead = max(prev.size or 9.0, 6.0) * 1.25
            same_page = line.page == prev.page
            gap = line.top - prev.top
            ended = (_norm(prev.plain)[-1:] in ".:;”\"" and
                     prev.x1 < right - 15)
            if same_page and gap > 1.6 * lead:
                new = True
            elif ended:
                new = True
            elif runover is None:
                runover = line.x0
            elif abs(line.x0 - runover) > 1.5:
                new = True
        if new:
            paras.append([line])
            runover = None
        else:
            paras[-1].append(line)
        prev = line
    return paras


def _blocks(lines: list, right: float, vocab: set) -> list:
    from ..resolve.assemble import _join
    out = []
    for run in _paragraphs(lines, right):
        out.append(m.Paragraph(
            text=_join(run, vocab),
            prov=m.Prov(run[0].page, tuple(l.id for l in run))))
    return out


def _mine_dates(crit: dict, text: str) -> None:
    for label, value in _DATE_IN_ROW.findall(text):
        key = label.lower()
        value = _norm(value).rstrip(".")
        if key in ("decided", "filed"):
            crit.setdefault("decision_date", value)
        elif key == "argued":
            crit.setdefault("date_argued", value)
            crit.setdefault("submitted", value)
        elif key == "reargued":
            crit.setdefault("date_reargued", value)
            crit["submitted"] = value
        elif key == "submitted":
            crit.setdefault("date_submitted", value)
            crit.setdefault("submitted", value)


def _sides(caption: str) -> list[str]:
    for pivot in (" v. ", " V. "):
        if pivot in caption:
            left, _, right = caption.partition(pivot)
            return [s.strip().rstrip(",. ") for s in (left, right)]
    return []


@decider("syllabus.pages", court=PAPER)
def syllabus_pages_prelim(model=None, **_):
    """None. The print's syllabus shares its last page with the counsel list
    or the opinion, so it is read by LINE in `headmatter.read` and handed
    over as paragraphs — a page-granular syllabus would take the opinion's
    opening with it."""
    return set()


@decider("headmatter.read", court=PAPER)
def read_headmatter_prelim(model, geom, **_):
    """Cover, caption, syllabus, counsel and the Reporter's Note — claimed."""
    if not is_preliminary_print(model) or len(model.pages) < 2:
        return NOTHING
    from ..geometry import learn_vocabulary
    from ..resolve.footnotes import line_markup
    vocab = learn_vocabulary(model)
    body = (geom.body_size if geom else 11.0) or 11.0
    right = geom.right_x1 if geom and geom.right_x1 else 454.0

    crit: dict = {"headmatter_style": "preliminary-print",
                  "court": "Supreme Court of the United States"}
    items: list = []
    consumed: set = set()
    dropped: list = []

    def _drop(lines, kind: str, page: int) -> None:
        lines = [l for l in lines if l.id not in consumed]
        if not lines:
            return
        dropped.append(m.Dropped(
            text=" ".join(_norm(l.plain) for l in lines)[:4000],
            prov=m.Prov(page, tuple(l.id for l in lines)), kind=kind))
        consumed.update(l.id for l in lines)

    def _is_head(pm, line) -> bool:
        """The running head: the folio row and, under it, the section name
        — both sub-body type in the page's top fifth (120pt and 144pt on a
        792pt sheet; the first text row stands at 164)."""
        return (line.top <= (pm.height or 792.0) * 0.2
                and (line.size or body) < body - 1.0)

    # ---- the cover: apparatus, whole — and the official citation ---------
    cover = model.pages[0]
    vol = first = None
    for line in _rows(cover):
        t = _norm(line.plain)
        mv, mp = _VOLUME.match(t), _PAGES.match(t)
        if mv:
            vol = mv.group(1)
        if mp:
            first = mp.group(1)
    if vol and first:
        crit["citation"] = f"{vol} U. S. {first}"
    _drop(_rows(cover), "cover", cover.number)

    # ---- the Reporter's Note: the last page, from its title down ---------
    last = model.pages[-1]
    note_rows = [l for l in _rows(last) if not _is_head(last, l)
                 and not _is_watermark(l)]
    if note_rows and _norm(note_rows[0].plain).lower().replace("'", "’") \
            == "reporter’s note":
        _drop(_rows(last), "reporter-note", last.number)

    # ---- the stamp, wherever it stands clear of the text -----------------
    for pm in model.pages:
        for line in pm.lines:
            if _is_watermark(line) and line.id not in consumed:
                _drop([line], "watermark", pm.number)

    # ---- every page's running head ------------------------------------
    # A READER THAT CLAIMS A PAPER INHERITS ITS FURNITURE. The section name
    # under the folio ('Per Curiam', 'Opinion of the Court', 'Kagan, J.,
    # dissenting') is set in every head, and where core's repetition test
    # misses it — a per curiam two pages long — 'Per Curiam' reads as a
    # byline and opens a second, phantom per curiam (Dept. of Education v.
    # California, 604 U. S. 650, p.3).
    for pm in model.pages:
        for line in _rows(pm):
            if line.id in consumed or not _is_head(pm, line):
                continue
            t = _norm(line.plain)
            if " v. " in t and len(t) < 80 and not crit.get(
                    "short_case_name"):
                crit["short_case_name"] = re.sub(r"^\d+\s+", "", t)
            kind = "folio" if t.strip(" .").isdigit() else "running-head"
            _drop([line], kind, pm.number)

    # ---- the caption page, row by row ------------------------------------
    page = model.pages[1]
    rows = _rows(page)
    walk = [l for l in rows if l.id not in consumed]

    state = "caption"
    last_item = None
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    docket_text = ""
    i = 0
    while i < len(walk):
        line = walk[i]
        t = _norm(line.plain)
        big = (line.size or body) >= body - 0.5
        if state in ("caption", "origin") and big:
            role = "lower-court" if (
                state == "origin" or t.lower().startswith(_ORIGIN_OPENERS)) \
                else "caption"
            if role == "lower-court":
                state = "origin"
            cont = (last_item is not None
                    and getattr(last_item, "role", "") == role)
            if cont:
                last_item.text = last_item.text.rstrip() + " " \
                    + line_markup(line).strip()
                last_item.prov = m.Prov(page.number,
                                        tuple(last_item.prov.line_ids)
                                        + (line.id,))
            else:
                last_item = _hm_line(line, page, geom, indent_rel=True)
                last_item.role = role
                items.append(last_item)
            (origin_rows if role == "lower-court" else caption_rows).append(t)
            consumed.add(line.id)
            i += 1
            continue
        if state in ("caption", "origin") and _DOCKET.match(t):
            docket_text = t
            item = _hm_line(line, page, geom, indent_rel=True)
            item.role = "docket"
            consumed.add(line.id)
            # A reargued case runs its dates onto a second row.
            while t.endswith(("—", "–", "-")) and i + 1 < len(walk):
                i += 1
                nxt = walk[i]
                t = _norm(nxt.plain)
                docket_text += t
                item.text = item.text.rstrip() + line_markup(nxt).strip()
                item.prov = m.Prov(page.number, tuple(item.prov.line_ids)
                                   + (nxt.id,))
                consumed.add(nxt.id)
            items.append(item)
            state = "syllabus"
            i += 1
            break
        break
    if not docket_text or not caption_rows:
        return NOTHING

    head_no = re.split(r"\.\s+(?=(?:Argued|Reargued|Submitted|Decided))",
                       docket_text, maxsplit=1)[0].strip().rstrip(".*")
    crit["docket_number"] = head_no
    _mine_dates(crit, docket_text)
    caption = _norm(" ".join(caption_rows))
    crit["caption"] = [caption]
    sides = _sides(caption)
    if len(sides) == 2:
        crit["parties"] = sides
        crit["case_name"] = " v. ".join(sides)
    if origin_rows:
        origin = _norm(" ".join(origin_rows))
        # Small caps come out of the text layer lower-case; the page shows
        # capitals, and the slip prints the same origin in caps.
        crit["lower_court"] = origin.upper() if origin == origin.lower() \
            else origin

    # ---- syllabus and counsel: by line, across pages, to the first byline
    syllabus_lines: list = []
    counsel_lines: list = []
    note_lines: list = []           # the amicus note, claimed
    together: list[str] = []        # the companion-docket note, read
    section = "syllabus"
    first_op_page = None
    for pm in model.pages[1:]:
        if first_op_page is not None:
            break
        zt = _zone_top(pm, geom)
        for line in _rows(pm):
            if line.id in consumed:
                continue
            t = _norm(line.plain)
            if zt is not None and line.top > zt:
                continue                      # notes: read below
            big = (line.size or body) >= body - 0.5
            if big and _FIRST_BYLINE.match(t):
                first_op_page = pm.number
                break
            if section == "syllabus" and big:
                section = "counsel"
            (syllabus_lines if section == "syllabus"
             else counsel_lines).append(line)
            consumed.add(line.id)

    # ---- the front matter's own notes ------------------------------------
    # Two '*' notes hang off the front matter. 'Together with No. 24–657 …'
    # names the companion dockets: it is READ here for `other_dockets` and
    # left to core, which files it as a headmatter footnote exactly as it
    # does on the slip. 'Briefs of amici curiae were filed …' belongs to the
    # counsel list, and it may run on into the zone of the opinion's first
    # page ('nia et al. by Timothy K. Talbot…' at the top of Barnes's p.5),
    # where core would read its tail as the opinion's own note. It is the
    # counsel's, to its end: the next labelled note, or the end of the zone.
    note_kind = None                   # None | 'together' | 'amicus'
    for pm in model.pages[1:]:
        if first_op_page is not None and pm.number > first_op_page:
            break
        zt = _zone_top(pm, geom)
        if zt is None:
            continue
        for line in _rows(pm):
            if line.top <= zt or line.id in consumed or _is_watermark(line):
                continue
            t = _norm(line.plain)
            # A SYMBOL opens a front-matter note — '*', or '†' where the
            # '*' already went to the companion dockets (TikTok, Bufkin); a
            # NUMBER opens the opinion's own.
            if t[:1] in "*†‡§":
                note_kind = ("together" if t.lstrip("*†‡§ ").startswith(
                    "Together with") else "amicus")
            elif _LABEL.match(t + " "):
                note_kind = None
            elif pm.number == first_op_page and note_kind is None:
                break
            if note_kind == "amicus":
                note_lines.append(line)
                consumed.add(line.id)
            elif note_kind == "together":
                together.append(t)

    for mt in _TOGETHER.finditer(" ".join(together)):
        for d in _DOCKET_NO.findall(mt.group(1)):
            crit.setdefault("other_dockets", []).append(f"No. {d}")

    syllabus = _blocks(syllabus_lines, right, vocab)
    # COUNSEL IS A ROWS SECTION (`sections.py`): one row per appearance as
    # the page sets it — a paragraph, wrapped — never a flow Paragraph.
    from ..resolve.assemble import _join
    attorneys: list = []
    for run in (_paragraphs(counsel_lines, right)
                + _paragraphs(note_lines, right)):
        row = _hm_line(run[0], model.pages[run[0].page - 1], geom,
                       indent_rel=True)
        row.text = _join(run, vocab)
        row.prov = m.Prov(run[0].page, tuple(l.id for l in run))
        row.role = "counsel"
        attorneys.append(row)
    if counsel_lines:
        crit["attorneys"] = "\n".join(
            re.sub(r"<[^>]+>", "", _join(run, vocab))
            for run in _paragraphs(counsel_lines, right))

    return {"criteria": crit, "items": items, "attorneys": attorneys,
            "summary": [], "syllabus": syllabus, "dropped": dropped,
            "consumed": consumed, "anchor_ids": set(),
            "doc_type_final": None}
