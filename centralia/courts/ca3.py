"""United States Court of Appeals for the Third Circuit ('ca3').

Everything unique to ca3 lives here. It imports core, never another court
file, and no other court file imports it.

ca3 prints ONE cover, in two measures. Whether the page is set on the bound
measure (x0≈144, a 5x8 slip) or the wide one (x0≈72), the SEQUENCE is the
same, and every section is announced either by a typed rule or by the words
the court itself prints:

    PRECEDENTIAL                       the publication banner (right, bold)
    UNITED STATES COURT OF APPEALS     the court, centered, 1-2 rows
    FOR THE THIRD CIRCUIT
    ________________                   a typed rule closes each section
    No. 24-2942                        the docket
    ________________
    UNITED STATES OF AMERICA           the caption: parties…
        v.                             …its hinge…
    NICOLE K. SCHUSTER,
        Appellant                      …and their statuses
    ________________
    On Appeal from the United States District Court     the origin…
    for the Eastern District of Pennsylvania
    (D.C. No. 2:23-cr-00406-001)                        …its docket…
    District Judge: Honorable Paul S. Diamond           …and who tried it
    ________________
    Argued July 8, 2025                          when it was heard
    Before: KRAUSE, MATEY, and SCIRICA, Circuit Judges       the roster
    (Opinion filed: March 23, 2026)              …and when it was filed
    Brett G. Sweitzer  [ARGUED]                  the appearances, at the
    Federal Community Defender Office            rail and ragged right
        …
        Counsel for Appellant
    ________________
    OPINION OF THE COURT               the paper's own name
    ________________
    KRAUSE, Circuit Judge.             …and the writing starts

The ORDER form (a rehearing denial, a clerk's order) prints the same cover
with the origin reduced to its bare district docket and the title —
'SUR PETITION FOR REHEARING' — standing where the dates would be, over a
'Present:' roster instead of a 'Before:' one.

What the reader does NOT touch: ca3 also prints its appearance roster BELOW
the writings (the profile declares ``counsel_after_writings``), and that
roster is core's to harvest. The reader stops at the first byline and never
reaches into a writing.
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
    "ca3", "United States Court of Appeals for the Third Circuit",
    byline=BylineGrammar(style="prose",
                         titles=("Circuit Judge", "Judge", "District Judge",
                                 "Justice", "J.")),
    # ca3's order form prints its appearance roster BELOW the writings, so
    # there the roster is not headmatter at all and takes a section of its
    # own. (A one-pass probe over the corpus found the trailing roster on 36
    # ca3 records — far more than any other court.)
    counsel_after_writings=True,
))

STYLE_COVER = "third-circuit cover"

_RULE = re.compile(r"^[_\-–—]{6,}$")
_FOLIO = re.compile(r"^[\-–—\s\[\(]*\d{1,3}[\-–—\s\]\)]*$")
# 'ALD-169', 'DLD-165', 'CLD-170', 'BLD-140' — the clerk's motions-calendar
# code, printed alone in the top-left corner above the banner.
_CALENDAR = re.compile(r"^[A-Z]{3}-\d{2,4}$")
# 'No. 25-1892' / 'Nos. 24-2990 and 24-3198' / 'Nos. 24-3291 & 24-3374' /
# 'Nos. 24-2320, 24-2368, and 24-2557' — the connectives STACK, so the run
# takes any number of them between two dockets.
_DOCKET_ROW = re.compile(
    r"^nos?\.?\s*\d{2}-\d{3,5}"
    r"(?:(?:\s*(?:,|&|and)\s*)+(?:nos?\.\s*)?\d{2}-\d{3,5})*\.?$", re.I)
_MONTH = (r"(?:January|February|March|April|May|June|July|August|September|"
          r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|"
          r"Oct|Nov|Dec)")
_DATE = re.compile(rf"\b{_MONTH}\.?\s+\d{{1,2}},?\s+\d{{4}}\b")
_DATE_LABEL = re.compile(
    rf"\b(argued|submitted|decided|filed|reargued|resubmitted)\b\s*:?\s*"
    rf"(?:on\s+)?({_MONTH}\.?\s+\d{{1,2}},?\s+\d{{4}})", re.I)

# The court's own words for where the case came from. ca3 opens the origin
# with one of these on every record that states one at all.
_ORIGIN_OPEN = (
    "on appeal from", "appeal from", "appeals from", "on appeal of",
    "cross-appeal from", "on petition for review", "petition for review",
    "petitions for review", "on petitions for review",
    "on a petition for writ of mandamus", "on a petition for review",
    "petition for writ of mandamus", "on review of", "review of",
    "on remand from", "on a motion", "appeal from the",
)
# …and the rows that continue it: the forum's second half, the trial
# court's own docket, and the judge who heard it.
_ORIGIN_MORE = ("for the ", "of the ", "(d.c.", "(district court",
                "(agency", "(bia", "(bankr", "(related to", "(no.",
                "(m.d.", "(e.d.", "(w.d.", "(d.n.j", "(d. del",
                "(amended pursuant")
_BENCH_LABEL = ("district judge", "immigration judge", "bankruptcy judge",
                "magistrate judge", "chief district judge", "circuit judge",
                "chief judge", "senior judge", "u.s. immigration judge",
                "judge", "honorable")
# A row that OPENS the submission/argument statement. ca3 spells the rule
# it heard the case under, and the date lands on the row below.
_SITTING_OPEN = ("submitted", "argued", "resubmitted", "reargued",
                 "summary action pursuant", "pursuant to third circuit",
                 "on submission")
_PUBLICATION = {"precedential": "published",
                "not precedential": "unpublished",
                "nonprecedential": "unpublished",
                "non-precedential": "unpublished"}
# The paper's own name, printed centered between two rules just above the
# body. Closed vocabulary: these are the only titles ca3 sets there.
_TITLE_WORDS = ("opinion", "order", "judgment", "per curiam",
                "sur petition for rehearing", "sur petition for panel "
                "rehearing", "memorandum")
_STATUS = ("appellant", "appellants", "appellee", "appellees",
           "petitioner", "petitioners", "respondent", "respondents",
           "plaintiff", "plaintiffs", "defendant", "defendants",
           "intervenor", "intervenors", "debtor", "debtors", "movant",
           "amicus", "amici", "cross", "creditor", "trustee")
_BENCH = ("judge", "judges", "circuit", "district", "senior", "chief",
          "magistrate", "bankruptcy", "and", "j.", "jj.", "justice")
# A counsel entry announces itself with one of these, wherever ca3 sets it
# — the label comes AFTER the names as often as before.
_COUNSEL_MARK = re.compile(
    r"\[argued\]|\(argued\)|\bcounsel for\b|\bon the briefs?\b|"
    r"\besq\.|\bllp\b|\bllc\b|\bp\.c\.\b|\bp\.a\.\b|"
    r"\boffice of\b|\bfederal (?:community |public )?defender\b|"
    r"\bpro se\b|\battorneys? for\b", re.I)
# A BYLINE NAMES ONE JUDGE — the bench word is SINGULAR. A roster's wrap
# has the identical shape and is plural ('AMBRO, Circuit Judges' closes the
# 'Before: MONTGOMERY-REEVES, ROTH and' above it), so NUMBER is the only
# thing that tells the writing's opening from the panel's second row. ca3
# also sets the byline in FULL CAPS with no closing stop on some records
# ('RESTREPO, CIRCUIT JUDGE'), so the bench title is matched without regard
# to case while the NAME still has to be capitalised.
_BYLINE = re.compile(
    r"^[A-ZÁÉÍÓÚÑÜ][\w'’\-\.]*(?:\s+[A-ZÁÉÍÓÚÑÜ][\w'’\-\.]*)*,\s+"
    r"(?i:circuit|district|chief|senior|associate|bankruptcy)\s+"
    r"(?i:judge)(?![sS])")
_SIGNATURE = ("by the court", "per curiam", "for the court")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_caps(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _opens_caps(text: str, least: int = 2) -> bool:
    """The row OPENS with a run of caps tokens — a party NAME. A party row
    need not be caps throughout: the name is, the descriptor that follows it
    is not ('MATT PLATKIN, Attorney General on behalf of the State…')."""
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
    """A row naming a party's ROLE rather than a party: 'Appellant',
    'Appellants in case 24-2990', 'Intervenor-Appellee', 'Debtor'."""
    bare = _norm(text).rstrip("*†‡").strip(" ,.;")
    if not bare or len(bare) > 60:
        return False
    words = [w for chunk in bare.split() for w in chunk.split("-")]
    # 'Appellants in case 24-2990' / 'Appellant in No. 24-2210'
    ok = _STATUS + ("and", "the", "in", "case", "no", "nos", "of", "all")
    return bool(words) and all(
        w.strip(" ,.;").lower() in ok
        or (w[:1].isdigit() and "-" not in w)
        or w[:2].isdigit()
        for w in words)


def _is_pivot(text: str) -> bool:
    bare = _norm(text).strip("—–-").rstrip(".").strip().lower()
    return bare in ("v", "vs", "versus", "against")


def _roster_names(roster: str) -> list[str]:
    """The judges named, without the connectives and the bench words."""
    out: list[str] = []
    for chunk in re.split(r",| and | AND |&|\band\b", roster):
        bare = chunk.strip().rstrip(",.").strip().rstrip("*†‡0123456789")
        bare = bare.strip(" .,")
        if not bare:
            continue
        if any(w.strip(" .,").lower() in _BENCH for w in bare.split()):
            continue
        out.append(bare)
    return out


def _roster_closed(text: str) -> bool:
    """A roster row that ENDS on the bench closes the run. The wrap always
    breaks after a name or a connective ('… PORTER, and' / '… PHIPPS,'), so
    the bench word arriving last is what says the roster is complete."""
    bare = _norm(text).rstrip(".").rstrip("*†‡0123456789").rstrip(" ,.")
    if not bare:
        return False
    return bare.split()[-1].lower() in ("judge", "judges", "j.", "jj.",
                                        "justice", "justices")


def _bare_title(text: str) -> str:
    """The row without its footnote mark. The mark is whatever glyph the
    document's symbol font gives it — ca3 sets it as U+F02A (a private-use
    asterisk) as often as a real one, so it is stripped by CLASS, not by a
    list of characters that will always be one short."""
    return _norm(text).strip("".join(
        c for c in set(_norm(text)) if not c.isalnum()))


def _is_title(text: str) -> bool:
    """The paper's own name — 'OPINION', 'OPINION OF THE COURT',
    'NONPRECEDENTIAL OPINION*', 'SUR PETITION FOR REHEARING'."""
    bare = _bare_title(text)
    if not bare or len(bare) > 46 or not _is_caps(bare):
        return False
    low = bare.lower()
    return any(low == w or low.startswith(w + " ") or low.endswith(" " + w)
               for w in _TITLE_WORDS)


def _origin_row(text: str) -> bool:
    """A row continuing the origin statement."""
    low = _norm(text).lower()
    if low.startswith(_ORIGIN_MORE):
        return True
    if any(low.startswith(b) for b in _BENCH_LABEL) and ":" in low[:34]:
        return True
    # 'Judge Anita B. Brody, No. 2:24-cv-01895' — the compact measure runs
    # the bench and the trial docket onto one row.
    if any(low.startswith(b + " ") for b in _BENCH_LABEL):
        return True
    if low.startswith(("no.", "nos.", "(no.")) and any(
            k in low for k in ("-cv-", "-cr-", "-md-", "-mc-", "-bk-",
                               "-ap-", "cv-", "cr-")):
        return True
    if low.startswith("district court no"):
        return True
    # A row wholly in PARENTHESES carrying a trial-court docket is the
    # origin whatever the clerk parenthesised ('(2:23-cr-00406-001)',
    # '(D.N.J. No. 2:25-cv-01963)', '(A207-938-810)'). The court's own
    # cover never parenthesises anything else at this point.
    bare = _norm(text)
    if bare.startswith("(") and bare.endswith(")") and len(bare) <= 110:
        inner = bare[1:-1]
        if any(c.isdigit() for c in inner) and (
                "-" in inner or "no" in inner.lower()):
            return True
    return False


@decider("headmatter.read", court="ca3")
def read_headmatter_ca3(model, geom, **_):
    """Read ca3's cover, or answer NOTHING."""
    if not model.pages:
        return NOTHING
    page = model.pages[0]
    lines = [l for pm in model.pages[:8] for l in pm.lines if l.plain.strip()]
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    if not lines:
        return NOTHING
    texts = [_norm(l.plain) for l in lines[:8]]
    # THE BANNER IDENTIFIES THE COVER. Without the court naming itself in
    # the opening rows this is not a ca3 cover and core keeps the document.
    if not any("court of appeals" in t.lower() for t in texts):
        return NOTHING

    top_keys = repeated_top_keys(model, geom.body_size if geom else None)
    rail = min(l.x0 for l in lines if l.page == 1)
    right = max(l.x1 for l in lines if l.page == 1)
    page_mid = (page.width or 612.0) / 2

    crit: dict = {"headmatter_style": STYLE_COVER}
    items: list = []
    consumed: set[int] = set()
    anchor_ids: list[int] = []
    head_lines: list = []
    folio_lines: list = []
    banner: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    roster: list[str] = []
    panel: list[str] = []
    counsel_rows: list = []
    cols: set = set()
    sides: list[list[str]] = [[], []]
    side = 0
    state = "court"
    fn_open = fn_first = False
    saw_panel = False

    def _hm(line, text, center=False, role=""):
        # THE CAPTION KEEPS ITS OWN WHITESPACE. ca3 hangs the status labels
        # and the per-case appellant lines well right of the party names
        # ('Appellants in case 24-2990' at x0=340 against a 72pt rail), and
        # stacking them flush loses which belongs to which. The offset from
        # the rail is carried on the row and rendered as one — the page's
        # own spacing, not an invented indent.
        rel = 0.0
        if role == "caption" and not center and line.x0 > rail + 24:
            rel = min(line.x0 - rail, (page.width or 612.0) * 0.5)
        items.append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align.CENTER if center else m.Align.LEFT,
            x0=line.x0, size=line.size or 0.0, rel=rel, role=role))

    for line in lines:
        text = _norm(line.plain)
        low = text.lower()
        centered = abs((line.x0 + line.x1) / 2 - page_mid) < 30

        # ---- furniture, in any state ----
        # A FOLIO prints on every page the reader spans, not just the
        # first: the counsel block runs five pages on a consolidated record
        # and each page's bare number would otherwise ride into it as an
        # entry. Recorded as the folio it is, so the claim stays total.
        if _FOLIO.match(text):
            consumed.add(line.id)
            folio_lines.append(line)
            continue
        if (line.top / (page.height or 792.0) <= 0.22
                and furniture_key(text) in top_keys):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # A TYPED RULE ends the section above it. ca3 rules every section
        # boundary on its cover, which is what makes the walk safe.
        if _RULE.match(text):
            consumed.add(line.id)
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            if state == "caption" and caption_rows:
                state = "front"
            elif state in ("origin", "counsel"):
                state = "front"
            continue
        # FOOTNOTE APPARATUS: the star note under the roster is the note
        # core attaches, not a headmatter row. Passed over, never claimed —
        # claimed it would render twice.
        _bare_mark = text.strip(" .") in ("*", "†", "‡", "∗")
        if _bare_mark or text.lstrip()[:1] in ("*", "†", "‡", "∗"):
            fn_open, fn_first = True, _bare_mark
            continue
        if fn_open:
            if fn_first or text[:1].islower():
                fn_first = False
                continue
            fn_open = False

        # APPARATUS SET A STEP SMALLER THAN THE BODY is a note, not a
        # cover row — whittaker's en banc order carries '1 Judge Ambro's
        # vote is limited to panel rehearing.' at 10pt under a 13pt page,
        # in the counsel block's own column. Passed over, never claimed:
        # core attaches it as the footnote it is.
        if (geom and line.size and state in ("front", "counsel")
                and line.size <= (geom.body_size or 12.0) - 1.5):
            continue

        # THE WRITING'S OWN BYLINE ends the headmatter, in any state but
        # the roster's — where the same shape is the roster's own wrap.
        if state != "panel" and _BYLINE.match(text):
            break
        if low.startswith(_SIGNATURE) and (saw_panel or counsel_rows):
            break

        # ---- the cover's sections, in the order the court prints them ----
        # A CONSOLIDATED RECORD PRINTS ONE COVER PER DOCKET, and the
        # appellate docket standing alone opens the next one (whittaker
        # sets Nos. 24-2210 & 24-2211 on page 1 and No. 25-1044 on page 2,
        # each over its own caption). Without this the second caption is
        # read as the origin's continuation and then as a writing.
        if state in ("origin", "front") and _DOCKET_ROW.match(text) \
                and not counsel_rows:
            state = "docket"

        if state == "court":
            if low.strip(" .*†‡∗") in _PUBLICATION:
                crit["publication_status"] = _PUBLICATION[low.strip(" .*†‡∗")]
                consumed.add(line.id)
                _hm(line, text, center=centered, role="court")
                continue
            if _CALENDAR.match(text):
                consumed.add(line.id)
                _hm(line, text, role="court")
                continue
            if ("court of appeals" in low or "third circuit" in low
                    or low.rstrip(".") in ("circuit", "the third circuit")):
                banner.append(text)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="court")
                continue
            state = "docket"

        if state == "docket":
            if _DOCKET_ROW.match(text):
                if crit.get("docket_number"):
                    crit.setdefault("other_dockets", []).append(
                        text.rstrip("."))
                else:
                    crit["docket_number"] = text.rstrip(".")
                consumed.add(line.id)
                _hm(line, text, center=centered, role="docket")
                continue
            state = "caption"

        # A SECTION LANDMARK OUTRANKS THE STATE IT INTERRUPTS. ca3 runs the
        # caption straight into the origin on the compact measure, with no
        # rule between them, and prints the paper's title above the roster
        # on its order form and below it on an opinion.
        if "".join(low.split()).startswith(("before", "present")) and (
                ":" in text[:12] or "judge" in low):
            state = "panel"
        elif low.startswith(_ORIGIN_OPEN) and not saw_panel:
            state = "origin"
        elif state == "caption" and caption_rows and _origin_row(text):
            state = "origin"
        elif _is_title(text):
            crit.setdefault("title", _bare_title(text))
            # WHERE the title stands says whose it is. On the ORDER form it
            # stands above the 'Present:' roster, in the slot the dates
            # would take — that is the cover naming the paper, and it is
            # headmatter. On the OPINION form it stands BELOW the roster and
            # the appearances, fenced on both sides, with the byline
            # directly under it — that is the writing's own heading, and it
            # opens the writing. Left standing (unclaimed) it lands at the
            # top of the opinion, the same trade ca6 makes with 'ORDER'.
            if saw_panel:
                break
            state = "front"
            consumed.add(line.id)
            anchor_ids.append(line.id)
            _hm(line, text, center=centered, role="title")
            continue
        elif state in ("origin", "front") and (
                low.startswith(_SITTING_OPEN)
                or (_DATE.search(text) and len(text) < 90)):
            state = "front"

        if state == "caption":
            # A CAPTION IS NOT PROSE. It ends at a full-measure lower-case
            # row at the rail — the court speaking — and nowhere else.
            # …and never MID-PARTY: ca3 sets a defendant list across as many
            # rows as the measure takes and its continuations open in lower
            # case ('… FRANK MONACK, in his individual and' / 'official
            # capacity; ANDREA PALMER, …'). A row continuing a party that
            # has not closed is that party, whatever its case.
            _mid_wrap = bool(caption_rows) and not caption_rows[-1].rstrip(
                ).endswith((",", ".", ";"))
            if (line.width >= 0.72 * (right - rail)
                    and line.x0 <= rail + 6 and text[:1].islower()
                    and len(text) > 60
                    and not _mid_wrap and not _opens_caps(text)):
                break
            consumed.add(line.id)
            _hm(line, text, center=centered, role="caption")
            if _is_pivot(text):
                caption_rows.append(text)
                side = 1
                continue
            if _is_status(text):
                caption_rows.append(text)
                continue
            # A party name WRAPS as far as the measure takes it; a row that
            # does not close its party continues it.
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
            continue

        if state == "origin":
            # THE ORIGIN RUNS TO ITS NEXT LANDMARK, not to a vocabulary.
            # It states the forum, wraps onto a second row, then gives the
            # trial docket and the judge; every one of those rows is the
            # origin, and testing them one wording at a time left the
            # Board of Immigration Appeals, the agency number and the
            # immigration judge unclaimed on every petition-for-review
            # record in the corpus.
            origin_rows.append(text)
            consumed.add(line.id)
            _hm(line, text, center=centered, role="lower-court")
            continue

        if state == "panel":
            roster.append(text)
            if _norm(text).lower().rstrip(":") not in ("before", "present"):
                head = text.split(":", 1)[1] if ":" in text[:12] else text
                panel.extend(_roster_names(head))
            consumed.add(line.id)
            _hm(line, text, center=centered, role="panel")
            saw_panel = True
            if _roster_closed(text):
                state = "front"
            continue

        if state in ("front", "counsel"):
            # A closed roster's run-on row: an en banc court lists its
            # senior judges after the bench word ('…, Circuit Judges' /
            # 'and AMBRO, Senior Judge').
            if (state == "front" and roster and low.startswith("and ")
                    and "judge" in low):
                roster.append(text)
                panel.extend(_roster_names(text))
                consumed.add(line.id)
                _hm(line, text, center=centered, role="panel")
                continue
            # THE SITTING: 'Argued July 8, 2025', 'Submitted Pursuant to
            # Third Circuit LAR 34.1(a)' over its own date row, '(Opinion
            # filed: March 23, 2026)'.
            # …a date row is SHORT and centered on the measure. Body prose
            # names a date as readily as a cover does ('At the direction of
            # the Court, the opinion filed on March 10, 2025 is amended…'),
            # and only the width tells the two apart.
            _dated = (_DATE.search(text) is not None
                      and len(text) < 90
                      and line.width < 0.72 * (right - rail))
            if state == "front" and (low.startswith(_SITTING_OPEN) or _dated):
                for label, value in _DATE_LABEL.findall(text):
                    key = label.lower()
                    value = value.strip().rstrip(".")
                    if key in ("decided", "filed"):
                        crit["decision_date"] = value
                    else:
                        crit["submitted"] = value
                if _DATE.search(text) and not _DATE_LABEL.search(text):
                    _d = _DATE.search(text).group(0).rstrip(".")
                    if "filed" in low:
                        crit["decision_date"] = _d
                    else:
                        crit.setdefault("submitted", _d)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="date")
                continue
            # …and the origin prints BELOW the dates on some records.
            if state == "front" and not origin_rows and (
                    low.startswith(_ORIGIN_OPEN) or _origin_row(text)):
                state = "origin"
                origin_rows.append(text)
                consumed.add(line.id)
                _hm(line, text, center=centered, role="lower-court")
                continue
            # COUNSEL IS SET AT THE RAIL AND RAGGED RIGHT. Every other row
            # on this cover is centered on the measure, and the court's own
            # prose is justified to it and opens on a paragraph indent — so
            # position alone separates an appearance from the writing.
            _at_rail = line.x0 <= rail + 8
            _ragged = line.x1 < right - 12
            _mark = bool(_COUNSEL_MARK.search(text))
            # A justified row split at a wide gap arrives as two lines
            # sharing one printed row ('Joel S. Sansone' | '(Argued)');
            # both belong to the entry.
            _same_row = bool(counsel_rows and line.row is not None
                             and line.row == counsel_rows[-1][0].row)
            if state == "counsel":
                # THE BLOCK ENDS AT A ROW OUTSIDE EVERY COLUMN THE BLOCK
                # ITSELF USES. ca3 sets the appearances at the rail and
                # their 'Counsel for …' labels one or two indents in, and
                # a label long enough to wrap is justified to the measure
                # like body prose — so raggedness cannot bound the block
                # and its own columns must.
                if (any(abs(line.x0 - c) <= 3 for c in cols)
                        or _mark or _same_row):
                    cols.add(line.x0)
                    counsel_rows.append((line, text))
                    consumed.add(line.id)
                    _hm(line, text, role="counsel")
                    continue
                break
            # An appearance is SHORT and never reaches the measure; the
            # mark alone cannot open the block, or the per curiam that
            # opens 'Proceeding pro se, …' becomes an appearance.
            if ((saw_panel and _at_rail and _ragged and len(text) < 96)
                    or (_mark and _ragged and len(text) < 120)):
                state = "counsel"
                cols.add(line.x0)
                counsel_rows.append((line, text))
                consumed.add(line.id)
                _hm(line, text, role="counsel")
                continue
            # A row this cover does not account for CONTINUES THE SECTION
            # ABOVE IT — every section here wraps, and the alternative is
            # to leave the row unclaimed, where core reads it as the
            # opening of a writing of its own.
            _prev = next((it.role for it in reversed(items)
                          if getattr(it, "role", "")), "")
            # …but never a row set to the FULL MEASURE: the court's own
            # prose is justified to the rail and a cover row never is, so
            # width alone keeps an order's opening sentence out of the
            # roster it prints under.
            if (_prev in ("lower-court", "date", "panel", "title")
                    and line.width < 0.72 * (right - rail)
                    and len(text) < 96 and not text[:1].islower()):
                consumed.add(line.id)
                _hm(line, text, center=centered,
                    role="date" if _prev == "title" else _prev)
                continue
            break

    if not (caption_rows or panel):
        return NOTHING
    if banner:
        crit["court"] = _norm(" ".join(banner))
    if origin_rows:
        court_rows, judge, low_docket = [], [], []
        for row in origin_rows:
            rl = row.lower()
            if any(rl.startswith(b) for b in _BENCH_LABEL):
                judge.append(row)
                continue
            if rl.startswith("(") or rl.startswith(("no.", "nos.",
                                                    "district court no")):
                low_docket.append(row.strip("()"))
                continue
            court_rows.append(row)
        if court_rows:
            crit["lower_court"] = _norm(" ".join(court_rows))
        if low_docket:
            crit["other_dockets"] = (crit.get("other_dockets") or []) \
                + [_norm(d) for d in low_docket]
        if judge:
            crit["lower_court_judge"] = _norm(" ".join(judge)).rstrip(".")
    if panel:
        crit["panel"] = panel
        crit["panel_line"] = _norm(" ".join(roster))
        crit["judges"] = crit["panel_line"]
    if caption_rows:
        crit["caption"] = caption_rows
        left = _norm(" ".join(sides[0])).rstrip(",. ")
        rightp = _norm(" ".join(sides[1])).rstrip(",. ")
        if left and rightp:
            crit["parties"] = [left, rightp]
            crit["case_name"] = f"{left} v. {rightp}"
    # COUNSEL PRINTED IN THE HEADMATTER STAYS THERE — it renders where the
    # page puts it, and only its MEANING is copied into criteria.
    if counsel_rows:
        crit["attorneys"] = _norm(" ".join(t for _, t in counsel_rows))[:2000]

    dropped = [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                         kind="running-head") for l in head_lines]
    dropped += [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                          kind="folio") for l in folio_lines]
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids}
