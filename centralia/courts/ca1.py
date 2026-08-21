"""United States Court of Appeals for the First Circuit ('ca1').

Everything unique to ca1 lives here. It imports core, never another court
file, and no other court file imports it.

ca1's headmatter is a fixed ZONE SEQUENCE, and the zones are separated by
WHITESPACE — the court draws no dividers at all:

    United States Court of Appeals          banner, 24pt
    For the First Circuit                   …and 18pt
    No. 25-1160                             the docket, at the rail
    ANDREA BECKWITH; EAST COAST SCHOOL …    the caption
        Plaintiffs, Appellees,              …its status rows
        v.                                  …its hinge
    AARON M. FREY, …
        Defendant, Appellant.
    APPEAL FROM THE UNITED STATES DISTRICT COURT     the origin…
    FOR THE DISTRICT OF MAINE
    [Hon. Lance E. Walker, U.S. District Judge]      …and who tried it
    Before                                  the roster, stacked over
    Montecalvo, Thompson, and Aframe,       three centred rows
    Circuit Judges.
    Christopher C. Taub, Chief Deputy …     counsel, hanging indent
      of the Maine Attorney General, …

What separates one zone from the next is a GAP: the court sets 13.6pt
leading inside a zone and stands the next one off by 27pt or more. Nothing
here is read by wording that the page's own measurements can settle.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import furniture_key, repeated_top_keys
from . import register

register(CourtProfile(
    "ca1", "United States Court of Appeals for the First Circuit",
    byline=BylineGrammar(style="prose",
                         titles=("Circuit Judge", "Judge", "District Judge",
                                 "Justice", "J.")),
    # The footer is a centred '- N -' page number; core folds it out of the
    # body so a paragraph broken across the page turn comes back whole.
    fold_page_numbers=True,
))

STYLE_ZONED = "whitespace-zoned"

_FOLIO = re.compile(r"^[\-–—\s\[\(]*\d{1,3}[\-–—\s\]\)]*$")
_DOCKET_ROW = re.compile(r"^(?:nos?\.)\s*\d{2}-\d{3,5}"
                         r"(?:[,;]\s*\d{2}-\d{3,5})*\.?$", re.I)
_ORIGIN_OPEN = ("appeal from", "appeals from", "on appeal from",
                "petition for review", "petitions for review",
                "on petition for review", "review of", "certified question",
                "appeal of", "cross-appeal from")
_JUDGE_ROW = re.compile(r"^\[.*\bjudge\b.*\]$", re.I)
_BENCH = ("judge", "judges", "circuit", "district", "senior", "chief",
          "magistrate", "and", "bankruptcy")
_STATUS = ("plaintiff", "plaintiffs", "defendant", "defendants",
           "appellant", "appellants", "appellee", "appellees",
           "petitioner", "petitioners", "respondent", "respondents",
           "intervenor", "intervenors", "amicus", "amici", "movant",
           "debtor", "creditor", "cross")
_NOTICE_CUES = ("not for publication", "may not be cited", "unpublished",
                "local rule 32.1", "first circuit rule", "is not precedent")
_ENTERED = re.compile(r"^(entered|issued|decided|filed)\s*:", re.I)
_SECTION_LABEL = re.compile(r"^(?:[IVXLC]+|[A-Z])\b\.?\s*\d*$"
                            r"|^(?:[IVXLC]+|[A-Z])\.\s")


def _is_title_row(line, text: str, centered: bool, gap: float) -> bool:
    """The document's own NAME — 'ERRATA SHEET', 'ORDER OF COURT',
    'JUDGMENT' — set bold, caps and centred, and stood off from the zone
    above it.

    An errata sheet has no origin, no panel, no counsel and no date: it is
    banner, docket, caption, then its title and the amendments it makes. The
    caption state has nothing to end it on, so without this the title AND
    the whole body come back tagged as caption. Measured across the court,
    the only rows of this shape on pages 1-3 are those three titles — a ca1
    party row is never bold — and numbered section headings are excluded.
    """
    if not getattr(line, "all_bold", False) or not centered:
        return False
    if not (3 <= len(text) <= 44) or not _is_caps(text):
        return False
    if text.rstrip().endswith((",", ";")) or _SECTION_LABEL.match(text):
        return False
    return gap >= 20


_COUNSEL_MARK = re.compile(
    r"\b(on brief|on the brief|Attorney|Attorneys|Esq\.?|LLP|LLC|P\.C\.|"
    r"P\.A\.|Office of|Solicitor|Counsel|for (?:the )?(?:appellant|appellee|"
    r"petitioner|respondent|plaintiff|defendant)s?)\b", re.I)
# 'GELPÍ, Circuit Judge.' — the writing's own byline, which on ca1 opens the
# first paragraph and is therefore INDENTED like a counsel entry. Only the
# byline itself can end the appearances there.
_BYLINE = re.compile(
    r"^[A-ZÁÉÍÓÚÑÜ][\w'’\-\.]*(?:\s+[A-ZÁÉÍÓÚÑÜ][\w'’\-\.]*)*,\s+"
    r"(?:Circuit|District|Chief|Senior|Associate)\s+Judges?[.:]")
# …and the byline may BREAK between the name and the office ('LYNCH,' /
# 'Circuit Judge. After Christian Joel …'), so the office alone opens a
# writing too.
_BYLINE_TITLE = re.compile(
    r"^(?:Circuit|District|Chief|Senior|Associate)\s+Judges?[.:]")
# A DATE standing alone is the date the document was filed — ca1 prints it
# under the counsel block with no label of any kind.
_BARE_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},\s+\d{4}\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_caps(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _opens_caps(text: str, least: int = 2) -> bool:
    """The row OPENS with a run of caps tokens — a party NAME. A party row
    need not be caps throughout: the name is, the descriptor after it is
    not ('AARON M. FREY, in their personal capacity …')."""
    run = 0
    for token in text.split():
        letters = [c for c in token if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            run += 1
            if run >= least:
                return True
            continue
        break
    return False


def _is_status(text: str) -> bool:
    """A row that names a party's ROLE rather than a party."""
    bare = _norm(text).rstrip("*†‡").strip(" ,.;")
    if not bare or len(bare) > 60:
        return False
    parts = [p for chunk in bare.split() for p in chunk.split("-")]
    return bool(parts) and all(
        p.strip(" ,.;").lower() in _STATUS + ("and", "the") for p in parts)


def _roster_names(roster: str) -> list[str]:
    """The judges named, without the connectives and bench words."""
    out: list[str] = []
    for chunk in re.split(r",| and | AND |&", roster):
        bare = chunk.strip().rstrip(",.").strip().rstrip("*†‡").strip(" .,")
        if not bare:
            continue
        if any(w.strip(" .,").lower() in _BENCH for w in bare.split()):
            continue
        out.append(bare)
    return out


def _roster_closed(text: str) -> bool:
    bare = text.rstrip().rstrip("*†‡0123456789").rstrip()
    return "judge" in text.lower() and bare.endswith(".")


@decider("headmatter.read", court="ca1")
def read_headmatter_ca1(model, geom, **_):
    """Read ca1's whitespace-zoned headmatter, or answer NOTHING."""
    if not model.pages:
        return NOTHING
    page = model.pages[0]
    top_keys = repeated_top_keys(model, geom.body_size if geom else None)
    lines = [l for pm in model.pages[:4] for l in pm.lines if l.plain.strip()]
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    if not lines:
        return NOTHING
    texts = [_norm(l.plain) for l in lines[:40]]
    # The banner names the court on the opening rows, set far larger than the
    # body. Without it this is not a ca1 cover and core keeps the document.
    if not any("court of appeals" in t.lower() for t in texts[:6]):
        return NOTHING

    rail = min(l.x0 for l in lines)
    body_size = geom.body_size if geom else 12.0
    crit: dict = {"headmatter_style": STYLE_ZONED}
    items: list = []
    consumed: set[int] = set()
    head_lines: list = []
    notice: list = []
    fn_lines: list = []
    banner: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    roster: list[str] = []
    panel: list[str] = []
    counsel_rows: list = []
    sides: list[list[str]] = [[], []]
    side = 0
    state = "court"
    fn_open = fn_first = False
    entry_open = False
    notice_open = False
    notice_size = None

    def _hm(line, text, center=False, role=""):
        items.append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align.CENTER if center else m.Align.LEFT,
            x0=line.x0, size=line.size or 0.0, role=role))

    page_mid = page.width / 2
    prev_top = None
    prev_page = None
    for idx, line in enumerate(lines):
        text = _norm(line.plain)
        low = text.lower()
        centered = abs((line.x0 + line.x1) / 2 - page_mid) < 30
        # The GAP that separates one zone from the next: inside a zone ca1
        # sets 13.6pt leading, and stands the next zone off by 27pt or more.
        gap = (line.top - prev_top) if (prev_top is not None
                                        and line.page == prev_page) else 0.0
        prev_top, prev_page = line.top, line.page

        # ---- furniture, in any state ----
        if _FOLIO.match(text):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if (line.top / (page.height or 792.0) <= 0.22
                and furniture_key(text) in top_keys):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        _cues = sum(1 for cue in _NOTICE_CUES if cue in low)
        _open_sentence = bool(notice) and not notice[-1][1].rstrip().endswith(".")
        if _cues >= 2 and notice_size is None:
            notice_size = line.size or 0.0
        if _cues >= 2 or (notice_size is not None
                          and abs((line.size or 0.0) - notice_size) <= 0.4
                          and (_cues >= 1 or (notice_open and _open_sentence))):
            notice_open = True
            notice.append((line, text))
            consumed.add(line.id)
            continue
        notice_open = False
        _bare_mark = text.strip(" .") in ("*", "†", "‡")
        if _bare_mark or text.lstrip()[:1] in ("*", "†", "‡"):
            fn_open, fn_first = True, _bare_mark
            fn_lines.append(line)
            consumed.add(line.id)
            continue
        if fn_open:
            # A note runs until ITS OWN SENTENCE ENDS. Continuing only on a
            # lower-case row stops at a wrapped citation ('…Fed. R. App. P.' /
            # '43(c)(2), Acting Attorney General Todd Blanche is
            # automatically substituted…'), and the rest of the note is then
            # read as counsel.
            _prev_open = fn_lines and not _norm(
                fn_lines[-1].plain).rstrip().endswith((".", "!", "?"))
            if fn_first or _prev_open or text[:1].islower():
                fn_first = False
                fn_lines.append(line)
                consumed.add(line.id)
                continue
            fn_open = False

        # A TYPED RULE separates zones on the records that draw one; it is
        # never content, and treating it as one knocked the reader out of the
        # banner before it reached the docket (african_communities lost its
        # docket to the caption).
        if set(text) <= set("_-–—") and len(text) >= 6:
            consumed.add(line.id)
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            continue

        # ---- the zone sequence ----
        if state == "court":
            if (line.size or 0) >= body_size + 3 or "court of appeals" in low \
                    or low.startswith("for the "):
                banner.append(text)
                consumed.add(line.id)
                _hm(line, text, center=True, role="court")
                continue
            if _DOCKET_ROW.match(text) or (
                    text.lower().startswith(("no.", "nos.")) and len(text) < 60):
                crit["docket_number"] = text.rstrip(".")
                consumed.add(line.id)
                _hm(line, text, role="docket")
                state = "caption"
                continue
            state = "caption"

        if state == "caption":
            if _is_title_row(line, text, centered, gap):
                state = "tail"
            elif low.startswith(_ORIGIN_OPEN):
                state = "origin"
            elif _JUDGE_ROW.match(text):
                state = "origin"
            elif low.rstrip(":") == "before" or low.startswith("before "):
                state = "panel"
            else:
                bare = text.strip().strip("—–-").rstrip(".").strip().lower()
                if bare in ("v", "vs", "versus"):
                    caption_rows.append(text)
                    side = 1
                    consumed.add(line.id)
                    _hm(line, text, center=centered, role="caption")
                    continue
                if _is_status(text):
                    caption_rows.append(text)
                    consumed.add(line.id)
                    _hm(line, text, center=centered, role="caption")
                    continue
                # A party name WRAPS across as many rows as the measure
                # takes; a row that does not close its party continues it.
                if caption_rows and not caption_rows[-1].rstrip().endswith(
                        (",", ".", ";")):
                    caption_rows[-1] = f"{caption_rows[-1]} {text}"
                    if sides[side]:
                        sides[side][-1] = f"{sides[side][-1]} {text}"
                    else:
                        sides[side].append(text)
                else:
                    caption_rows.append(text)
                    sides[side].append(text)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="caption")
                continue

        if state == "origin":
            if low.rstrip(":") == "before" or low.startswith("before "):
                state = "panel"
            else:
                if _JUDGE_ROW.match(text):
                    crit["lower_court_judge"] = text.strip("[]")
                else:
                    origin_rows.append(text)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="lower-court")
                continue

        if state == "panel":
            consumed.add(line.id)
            _hm(line, text, center=centered, role="panel")
            roster.append(text)
            if low.rstrip(":") != "before":
                panel.extend(_roster_names(text))
            if _roster_closed(text):
                state = "tail"
            continue

        if state == "tail":
            # The DATE a document was entered closes an order's headmatter.
            if _ENTERED.match(text) and len(text) < 60:
                from ..resolve.headmatter import find_date as _fd
                _d = _fd(text)
                if _d:
                    crit["decision_date"] = _d
                consumed.add(line.id)
                _hm(line, text, center=centered, role="date")
                continue
            if _is_title_row(line, text, centered, gap):
                crit.setdefault("title", text)
                consumed.add(line.id)
                _hm(line, text, center=True, role="title")
                continue
            if _BYLINE.match(text) or _BYLINE_TITLE.match(text):
                break
            # A lone SURNAME row that the office follows is the byline's
            # first half — drop it back to the writing with its second.
            if (counsel_rows and _is_caps(text.rstrip(","))
                    and text.rstrip().endswith(",") and len(text) < 30):
                _nxt = None
                for _l2 in lines[lines.index(line) + 1:]:
                    _t2 = _norm(_l2.plain)
                    if _t2:
                        _nxt = _t2
                        break
                if _nxt and _BYLINE_TITLE.match(_nxt):
                    break
            if _BARE_DATE.match(text):
                from ..resolve.headmatter import find_date as _fd2
                if not crit.get("decision_date"):
                    crit["decision_date"] = _fd2(text)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="date")
                continue
            # COUNSEL is set as a HANGING INDENT: the entry's first line is
            # indented from the rail and its continuations return to it. The
            # court's own prose starts at the rail and stays there, so the
            # block ends at a row at the rail that opens no entry.
            _indented = line.x0 > rail + 12
            # An entry's continuation returns to the rail, so position alone
            # cannot tell it from the court's own prose. What can: a
            # continuation CONTINUES A SENTENCE. Once the last counsel row
            # has closed its sentence, a fresh row at the rail is the court
            # speaking ('Accordingly, the government's request for summary
            # reversal is allowed.'), and reading it as counsel leaves the
            # judgment with nothing but its distribution list.
            # AN ENTRY IS THE UNIT, NOT THE ROW. ca1 sets counsel as a
            # hanging indent: the entry opens indented and its
            # continuations return to the rail, and the mark that identifies
            # it ('on brief', 'Attorney', a firm) may not appear until two
            # rows in ('David O. Martoni-Dale, with whom W. Stephen Muldrow,
            # United' / 'States Attorney, …'). Judging row by row ends the
            # block at a legitimate entry, and — because the tail then stops
            # early — the filing date below it is never claimed and comes
            # back as a one-block phantom writing.
            #
            # So an entry OPENS only on evidence found across its whole
            # span, and a row that opens no entry ends the headmatter. That
            # is also what keeps a judgment's order text and an unsigned per
            # curiam's opening line out of the appearances: neither carries
            # a counsel mark anywhere in its span.
            _indented = line.x0 > rail + 12
            if _indented or not counsel_rows:
                _span = [text]
                for _l2 in lines[idx + 1: idx + 9]:
                    _t2 = _norm(_l2.plain)
                    if not _t2:
                        continue
                    if _l2.x0 > rail + 12:      # the next entry starts
                        break
                    _span.append(_t2)
                    if _t2.rstrip().endswith((".", "!", "?")):
                        break
                if not _COUNSEL_MARK.search(" ".join(_span)):
                    break
                entry_open = True
            elif not entry_open:
                break
            counsel_rows.append((line, text))
            consumed.add(line.id)
            _hm(line, text, role="counsel")
            continue

    if not (caption_rows or panel):
        return NOTHING
    if banner:
        crit["court"] = _norm(" ".join(banner))
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    if panel:
        crit["panel"] = panel
        crit["panel_line"] = _norm(" ".join(roster))
        crit["judges"] = crit["panel_line"]
    if caption_rows:
        crit["caption"] = caption_rows
        left = _norm(" ".join(sides[0])).rstrip(",. ")
        right = _norm(" ".join(sides[1])).rstrip(",. ")
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
    if counsel_rows:
        entries: list[str] = []
        for line, text in counsel_rows:
            if line.x0 > rail + 12 or not entries:
                entries.append(text)
            else:
                entries[-1] = f"{entries[-1]} {text}"
        crit["attorneys"] = " ".join(entries)[:2000]

    dropped = [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                         kind="running-head") for l in head_lines]
    dropped += [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                          kind="footnote") for l in fn_lines]
    if notice:
        dropped.append(m.Dropped(
            text=_norm(" ".join(t for _, t in notice))[:1200],
            prov=m.Prov(notice[0][0].page, tuple(l.id for l, _ in notice)),
            kind="notice"))
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed}
