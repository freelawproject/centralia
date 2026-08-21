"""United States Court of Appeals for the Fourth Circuit ('ca4').

Everything unique to ca4 lives here. It imports core, never another court
file, and no other court file imports it.

ca4 prints ONE layout, and it is the plainest contract of any circuit:

    STYLE 'ruled bands' — the court FENCES every section of its headmatter
    with a drawn rule and puts exactly one thing inside each fence.

        USCA4 Appeal: 25-1448  Doc: 39  Filed: …    the ECF stamp (furniture)
        PUBLISHED                                   the publication flag
        UNITED STATES COURT OF APPEALS              the banner
        FOR THE FOURTH CIRCUIT
        ─────────                                   a drawn 108pt rule
        No. 25-1448                                 the docket
        ─────────
        AMERICAN ACCEPTANCE CORPORATION OF SC, …    the caption: parties…
                 Plaintiff – Appellant,             …their status, indented
            v.                                      …the pivot
        JOHN GIETZ; SHERIFF BRYAN KOON, …           …the other side
                 Defendants – Appellees.
        ─────────
        Appeal from the United States District …    the origin
        ─────────
        Argued:  October 23, 2025   Decided:  …     the dates
        ─────────
        Before BENJAMIN, Circuit Judge, FLOYD, …    the roster
        ─────────
        Affirmed by published opinion.  Judge …     the disposition
        ─────────
        ARGUED:  Joseph Studemeyer, STUDEMEYER …    the appearances

THE RULES ARE THE ZONE BOUNDARIES. Every one of the 103 records in the
corpus draws them, always the same way — a 108pt-wide filled rect centered
on the page — and they sit BETWEEN headmatter rows, never under one. That
makes the BAND the unit of meaning: a band asks 'what is this section?',
which is a much smaller question than 'what state should this row put the
machine into?', and it is what keeps the roster's second row from reading
as a byline (`GILES, United States District Judge …` parses as one) — a row
inside a fenced band is that band's, whatever it looks like on its own.

The bands are read in the order the court prints them, but each is
identified by its OWN landmark, not by its position: a consolidated record
repeats docket-then-caption for every appeal and states the origin, the
dates, the roster and the disposition once, at the end, for all of them.

The reader claims HEADMATTER ONLY: it stops at the first byline, and
everything below — the writings, their footnotes, their paragraphs — is
core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import FurnitureFinder
from . import register

CA4 = register(CourtProfile(
    "ca4", "United States Court of Appeals for the Fourth Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the short form on separate writings; the circuits'
        # shared grammar, kept verbatim so nothing about ca4's bylines
        # changes by being moved out of the loop it used to sit in.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_RULED_BANDS = "ruled bands"

# ---- ca4's declared facts (measured over the corpus, not tuned) -----------
# THE FENCE: a filled rect 108pt wide, centered on the page axis. Measured on
# all 103 records; the only variation is a caption set off-axis, where the
# same 108pt rule sits 18pt to the left. Width is the fact — a rule that
# spans the measure is an underline or a footnote separator, not a fence.
_FENCE_WIDTH = (60.0, 200.0)
_FENCE_OFF_AXIS = 60.0
# The court sets its headmatter at the body size on the body rail.
_RAIL = 72.0
# A byline in the trailing (unfenced) region is SHORT and consumes its whole
# row; the roster's continuation is neither.
_BYLINE_MAX = 60

_DOCKET_ROW = re.compile(
    r"^Nos?\.\s*\d{2}-\d{3,5}"
    r"(?:\s*\(L\))?(?:\s*[,;&]\s*(?:and\s+)?\d{2}-\d{3,5}(?:\s*\(L\))?)*\.?$",
    re.I)
_TYPED_DASHES = re.compile(r"^[-–—_]{4,}$")
_BARE_LABEL = re.compile(
    r"^(?:Argued(?:\s+and\s+Submitted)?|Submitted|Reargued|Decided|Amended"
    r"|Filed|Entered)\s*:?\s*$", re.I)
_FOLIO = re.compile(r"^[\-–—\s\[\(]*\d{1,3}[\-–—\s\]\)]*$")

# ORIGIN OPENERS — how ca4 names the tribunal it is reviewing. A closed
# vocabulary of the court's own openers, never a test on the court's NAME.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "cross-appeals from", "petition for review", "petitions for review",
    "on petition for review", "on petitions for review", "on remand from",
    "review of", "on review of", "appeal of", "appeals of",
    "on petition for writ", "petition for writ", "on petition for a writ",
    "petition for a writ", "application for certificate",
    "application for leave", "on application for", "on writ of",
)
# THE DATE LABELS ca4 prints, longest first so 'Argued and Submitted' wins
# over 'Submitted'.
_DATE_LABELS = ("argued and submitted", "submitted on briefs", "reargued",
                "argued", "submitted", "decided", "amended", "filed",
                "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "claimant", "claimants", "party-in-interest", "third party",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# The unpublished-opinion notice ca4 prints under its appearances. It is not
# an appearance and it is not the court's own words about this case — it is
# recorded as a drop, the way every other notice is.
_NOTICE = "not binding precedent"
# The publication flag, matched on its stem so PUBLISHED / UNPUBLISHED both
# read alike.
_PUBLICATION = {"published": "published", "unpublished": "unpublished"}


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("united states court of appeals",
                   "for the fourth circuit",
                   "united states court of appeals for the fourth circuit")


def _origin_kind(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _is_disposition(text: str) -> bool:
    """'Affirmed by published opinion.  Judge Giles wrote the opinion, in
    which Judge Benjamin and Judge Floyd joined.'

    ca4 states what it did in a band of its own between the roster and the
    appearances, always in the same form: the outcome, then 'by
    published/unpublished … opinion', then who wrote and who joined. TESTED
    BEFORE THE ORIGIN — its opening words are the outcome, and those are the
    same words an origin row can open with ('Petition for review granted;
    order vacated and remanded by published opinion. …')."""
    low = _norm(text).lower()
    return " by published " in low or " by unpublished " in low


def _labelled_dates(text: str) -> dict:
    """{'argued': 'October 23, 2025', 'decided': 'May 12, 2026'}.

    ca4 runs its dates along one row under their own labels, the argued date
    on the rail and the decided date at the right margin (pdfio splits that
    row at the column gap, so each half arrives on its own). A date row is
    SHORT — 'filed' inside prose is an ordinary English word."""
    if len(text) > 160:
        return {}
    low = text.lower()
    hits = []
    for label in _DATE_LABELS:
        start = 0
        while True:
            at = low.find(label, start)
            if at < 0:
                break
            after = low[at + len(label):at + len(label) + 1]
            if (at == 0 or not low[at - 1].isalnum()) and after not in ("]", ")"):
                hits.append((at, label))
            start = at + len(label)
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
        end = picked[i + 1][0] if i + 1 < len(picked) else len(text)
        seg = text[at + len(label):end]
        # A DATE VALUE IS READ IN THE FORM THE PAGE SET IT — the comma in
        # 'May 12, 2026' is part of the date, so the value is a SLICE of the
        # row, never a re-join of its tokens.
        mm = re.search(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
                       r"|\d{1,2}\s+[A-Z][a-z]+\.?\s+\d{4})", seg)
        if mm is None:
            continue
        first = mm.group(1).split()[0].strip(".,").lower()
        if first not in _MONTHS and not first.isdigit():
            continue
        out[label.replace(" ", "_")] = _norm(mm.group(1))
    return out


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test: ca4
    sets 'BENJAMIN' in caps and 'Patricia Tolliver GILES' mixed, and both are
    judges. The designation clause a visiting judge carries ('… sitting by
    designation.') names nobody, so the roster ends where it begins."""
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
        piece = chunk.strip().strip(".*: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*: ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not another
            # judge ('RAYMOND J. LOHIER, JR.').
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _split_origin(text: str):
    """(forum, lower docket, trial judge) out of ca4's origin row.

    'Appeal from the United States District Court for the District of South
    Carolina, at Columbia.  Mary G. Lewis, District Judge.
    (3:24-cv-01099-MGL)' — the forum runs to the town, the judge is the
    sentence after it that ends in a bench word, and the lower docket is the
    parenthesis at the end."""
    flat = _norm(text)
    docket = None
    mm = re.search(r"\(([^()]*\d[^()]*)\)\s*\.?$", flat)
    if mm:
        docket = mm.group(1).strip()
        flat = flat[:mm.start()].rstrip(" .")
    # THE TRIAL JUDGE IS A SENTENCE THAT ENDS ON A BENCH WORD, and the bench
    # words are a closed vocabulary. Splitting on full stops instead cut the
    # clause at the judge's own middle initial ('Mary G. Lewis').
    judge = None
    jm = re.search(r"(?:^|\.\s+)([A-Z][^.]*?,\s*(?:[A-Z][\w.]*\s+){0,3}"
                   r"(?:Judge|Judges|Justice|Chief Judge|Senior Judge|"
                   r"Magistrate Judge|District Judge|Bankruptcy Judge))\s*\.",
                   flat)
    if jm:
        judge = _norm(jm.group(1))
    return flat.strip(), docket, judge


def _is_counsel_opener(text: str) -> bool:
    head = _norm(text).upper()
    return head.startswith(("ARGUED:", "ARGUED :", "ON BRIEF:", "ON BRIEF :",
                            "ON THE BRIEF:", "COUNSEL:"))


def _fences(model) -> dict:
    """Where the page drew its section fences, per page.

    ca4's fence is a short centered rule the page draws BETWEEN two
    headmatter rows. A rule that spans the measure is an underline or a
    footnote separator and is not a fence."""
    out: dict = {}
    for pm in model.pages:
        tops = []
        for r in pm.h_rules:
            if not (_FENCE_WIDTH[0] <= r.width <= _FENCE_WIDTH[1]):
                continue
            if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_OFF_AXIS:
                continue
            tops.append(r.top)
        if tops:
            out[pm.number] = sorted(tops)
    return out


@decider("headmatter.read", court="ca4")
def read_headmatter_ca4(model, geom, **_):
    """Read ca4's ruled-band headmatter, or NOTHING.

    NOTHING is returned for anything that is not the contract above: core's
    shared walk places those rows unidentified, which is a smaller error than
    a confident misreading."""
    if not model.pages:
        return NOTHING
    fences = _fences(model)
    if len(fences.get(1, ())) < 2:
        return NOTHING                      # not the ruled-band contract

    finder = FurnitureFinder(model, geom.body_x0 if geom else _RAIL,
                             geom.body_size if geom else 13.0)
    parser = BylineParser(CA4.byline)

    # The block can run several pages on a consolidated record (jonathan_r
    # states its appearances on pages 3-4); what stops the reader is its
    # LANDMARKS, not a page count.
    rows: list = []                       # (page, top, line) in page order
    for pm in model.pages[:8]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: ca4's CM/ECF
            # overlay ('USCA4 Appeal: 25-1448  Doc: 39  Filed: …') and the
            # foot folio. Core measures and records those; the reader steps
            # over them rather than claiming them twice.
            if finder.kind(pm, line):
                continue
            rows.append((pm.number, line.top, line))
    rows.sort(key=lambda r: (r[0], r[1]))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for _, _, l in rows[:6]):
        return NOTHING                      # ca4 always names itself first

    def fence_index(page: int, top: float) -> tuple:
        """Which band a row is in: (page, count of fences above it)."""
        return (page, sum(1 for t in fences.get(page, ()) if t < top))

    # ---- bands ----------------------------------------------------------
    bands: list = []                        # [(key, [rows])]
    for page, top, line in rows:
        key = fence_index(page, top)
        if bands and bands[-1][0] == key:
            bands[-1][1].append(line)
        else:
            bands.append((key, [line]))

    # A band that is bounded BELOW by a fence is closed: the court said so.
    # The trailing band — the one under the last fence of the last page the
    # headmatter reaches — is open, and it is the only place a byline can
    # end the reader.
    def closed(idx: int) -> bool:
        page, n = bands[idx][0]
        return n < len(fences.get(page, ()))

    def _byline_row(text: str) -> bool:
        """A ca4 byline: short, and the parse consumes the whole row.

        'GILES, United States District Judge for the Eastern District of
        Virginia, sitting by' parses as a byline and is the roster's second
        row; it is 83 characters long and it is inside a fenced band, so
        neither test lets it through."""
        flat = _norm(text)
        if len(flat) > _BYLINE_MAX:
            return False
        r = parser.parse(flat)
        if r is None:
            return False
        return getattr(r, "end", 0) >= len(flat.rstrip(" .:"))

    # ---- classify each band ---------------------------------------------
    kinds: list = []
    seen_docket = seen_tail = seen_counsel = False
    closed_through = 0                    # bands the court itself closed
    for i, (_key, blines) in enumerate(bands):
        texts = [_norm(l.plain) for l in blines]
        head = texts[0]
        kind = None
        if seen_counsel:
            # THE APPEARANCES RUN ON PAST THE PAGE BREAK — one entry per
            # party, and a consolidated record's caption can fill two pages
            # by itself, so the roster lands on page 3 and finishes on page
            # 4. Below them the court prints its notice and nothing else, so
            # the band under the appearances is still theirs until the
            # BYLINE, which is where this reader stops for good.
            kind = "notice" if all(_NOTICE in t.lower() for t in texts) \
                else "counsel"
        elif all(_is_banner(t) or t.lower() in _PUBLICATION for t in texts):
            kind = "court"
        elif _DOCKET_ROW.match(head):
            # A NEW DOCKET OPENS A NEW CASE, and the case starts with its
            # caption. A consolidated ca4 record repeats docket-then-caption
            # (and may repeat the origin with them), so the tail flag has to
            # fall back with it — left standing, the second appeal's caption
            # read as the appearances.
            kind = "docket"
            seen_docket = True
            seen_tail = False
        elif _is_disposition(" ".join(texts)):
            kind = "summary"
            seen_tail = True
        elif _origin_kind(head):
            kind = "lower-court"
            seen_tail = True
        elif (any(_labelled_dates(t) for t in texts)
              and all(_labelled_dates(t) or _BARE_LABEL.match(t)
                      for t in texts)):
            # A LABEL WITH NO VALUE IS STILL THE DATE BAND. mcpherson sets
            # 'Argued:  October 23, 2025' on the rail and a bare 'Decided:'
            # at the right margin — the slip states no decision date. A band
            # test that demanded a date from every row read the whole tail,
            # roster and disposition included, as the appearances.
            kind = "date"
            seen_tail = True
        elif head.lower().startswith("before"):
            kind = "panel"
            seen_tail = True
        elif _is_counsel_opener(head):
            kind = "counsel"
            seen_counsel = True
        elif all(_NOTICE in t.lower() for t in texts):
            kind = "notice"
        elif seen_tail:
            # THE BAND AFTER THE COURT'S OWN TAIL IS THE APPEARANCES. ca4
            # labels them 'ARGUED:' when someone argued and labels them not
            # at all when nobody did ('Amer Rizvi, Appellant Pro Se.  Heather
            # Kathleen Bardot, MCGAVIN, BOYCE, …'), so a wording test loses
            # the roster on every pro-se record. The fence says where it is.
            kind = "counsel"
            seen_counsel = True
        elif seen_docket:
            # EVERYTHING BETWEEN THE DOCKET AND THE TAIL IS THE CAPTION —
            # not only the rows that look like parties. The 'v.' says
            # nothing for itself and a wrapped respondent list looks like
            # prose; ca4 puts nothing else in that span.
            kind = "caption"
        else:
            kind = "court"
        kinds.append(kind)
        if closed(i):
            closed_through = i + 1

    # ---- where the reader stops -----------------------------------------
    # THE FIRST BYLINE ENDS THE HEADMATTER. Inside a fenced band a row that
    # parses as a byline is the roster's own continuation ('GILES, United
    # States District Judge for the Eastern District of Virginia, sitting
    # by'), so only the trailing region — from the appearances down — is
    # tested. Where no byline is found the claim is cut back to the last
    # band the COURT closed with a fence: an over-long claim would swallow
    # the opinion, and a short one only leaves rows for core's shared walk.
    trail = next((i for i, k in enumerate(kinds) if k == "counsel"), None)
    if trail is None:
        bands, kinds = bands[:closed_through], kinds[:closed_through]
    else:
        cut = None
        for i in range(trail, len(bands)):
            hit = next((n for n, l in enumerate(bands[i][1])
                        if _byline_row(l.plain)), None)
            if hit is not None:
                cut = (i, hit)
                break
        if cut is None:
            bands = bands[:max(closed_through, trail + 1)]
            kinds = kinds[:max(closed_through, trail + 1)]
        else:
            i, hit = cut
            bands = bands[:i] + ([(bands[i][0], bands[i][1][:hit])]
                                 if hit else [])
            kinds = kinds[:i + (1 if hit else 0)]
    if "caption" not in kinds and "docket" not in kinds:
        return NOTHING

    # ---- emit -----------------------------------------------------------
    crit: dict = {"headmatter_style": STYLE_RULED_BANDS}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    cases: list = []
    caption_rows: list = []
    panel_rows: list = []
    origin_bands: list = []
    counsel_rows: list = []
    disposition_rows: list = []
    dates: dict = {}
    banner_rows: list = []
    notice_lines: list = []
    pages_by_no = {pm.number: pm for pm in model.pages}

    def emit(line, role: str):
        pm = pages_by_no[line.page]
        text = _norm(line.plain)
        align = line_alignment(line, pm.width, geom)
        rel = 0.0
        if role in ("caption", "counsel") and align == "L" \
                and line.x0 > _RAIL + 24:
            rel = min(line.x0 - _RAIL, (pm.width or 612.0) * 0.5)
        items.append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.bold), rel=rel, role=role))
        consumed.add(line.id)

    last_key = None
    for (key, blines), kind in zip(bands, kinds):
        # THE FENCE ITSELF RENDERS. A reader that claims the region inherits
        # the page's furniture, and here the fences are not furniture at all
        # — they are the court's own section marks. They carry the provenance
        # of the row above them so the merge-by-position in core keeps them
        # where the page drew them.
        if last_key is not None and key != last_key and items:
            prev = items[-1]
            if key[0] == last_key[0]:      # a fence, not a page turn
                items.append(m.Rule(prov=prev.prov, span="full"))
        last_key = key

        if kind == "notice":
            notice_lines.extend(blines)
            continue
        band_origin = None
        for line in blines:
            text = _norm(line.plain)
            low = text.lower()
            if kind == "court":
                if low.strip(" .*") in _PUBLICATION:
                    crit.setdefault("publication_status",
                                    _PUBLICATION[low.strip(" .*")])
                elif _is_banner(text):
                    banner_rows.append(text)
                emit(line, "court")
            elif kind == "docket":
                cases.append({"docket": text, "caption": []})
                if not crit.get("docket_number"):
                    crit["docket_number"] = text
                else:
                    crit.setdefault("other_dockets", []).append(text)
                emit(line, "docket")
            elif kind == "caption":
                if not _TYPED_DASHES.match(text):
                    caption_rows.append(text)
                    if cases:
                        cases[-1]["caption"].append(text)
                emit(line, "caption")
            elif kind == "lower-court":
                if band_origin is None:
                    band_origin = []
                    origin_bands.append(band_origin)
                band_origin.append(text)
                emit(line, "lower-court")
            elif kind == "date":
                dates.update(_labelled_dates(text))
                emit(line, "date")
            elif kind == "panel":
                panel_rows.append(text)
                emit(line, "panel")
            elif kind == "summary":
                disposition_rows.append(text)
                emit(line, "summary")
            elif kind == "counsel":
                counsel_rows.append(text)
                emit(line, "counsel")

    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        # THE PARTIES ARE THE LEAD CASE'S. A consolidated record prints one
        # caption per appeal; joining them all yields a case name that names
        # four sides and belongs to none of them.
        lead = cases[0]["caption"] if cases else caption_rows
        sides = _sides(lead)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            # A MANDAMUS PETITION HAS ONE SIDE ('In re: EXPRESS SCRIPTS,
            # INC., / Petitioner.'). One party is still the parties.
            one = _sides(lead, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one
    for n, band in enumerate(origin_bands):
        # THE PRINTED FORM AND THE PARSED FORM ARE BOTH FACTS. The origin
        # states the forum, the trial judge and the lower docket in one
        # sentence; the row stands as `lower_court`, and what it names is
        # read out beside it. A consolidated record states one origin per
        # appeal — the LEAD one is the document's, the rest contribute their
        # dockets and nothing else.
        printed = _norm(" ".join(band))
        _forum, lower_docket, judge = _split_origin(printed)
        if n == 0:
            crit["lower_court"] = printed
            if judge:
                crit["lower_court_judge"] = judge
        if lower_docket:
            crit.setdefault("other_dockets", []).append(lower_docket)
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if disposition_rows:
        crit["disposition"] = _norm(" ".join(disposition_rows))
    if counsel_rows:
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    for label, value in dates.items():
        if label in ("decided", "filed", "amended"):
            crit.setdefault("decision_date", value)
        elif label in ("submitted", "submitted_on_briefs"):
            crit.setdefault("submitted", value)
    if notice_lines:
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in notice_lines))[:1200],
            prov=m.Prov(notice_lines[0].page,
                        tuple(l.id for l in notice_lines)),
            kind="notice"))
        consumed.update(l.id for l in notice_lines)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed, "anchor_ids": [],
            "doc_type_final": None}


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        first = flat.split()[0].rstrip(".").lower() if flat.split() else ""
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. ").lower()
        # A STATUS row is a role label, not a party ('Plaintiff – Appellant,'
        # 'Amici Supporting Appellants.'). Closed vocabulary.
        words = [w.strip(",.;–-") for w in bare.replace("–", " ").split()]
        if words and all(
                w in _STATUS_WORDS or w in ("and", "supporting", "the", "-",
                                            "third", "party", "pro", "se",
                                            "cross", "in", "interest", "of")
                or not w for w in words):
            continue
        if flat.startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        # After the pivot a fresh amici roll belongs to the case it follows,
        # never to a new side.
        side.append(flat)
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(",. ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(",. "),
            _norm(" ".join(right)).rstrip(",. "))
