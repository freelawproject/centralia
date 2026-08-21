"""The author-byline grammar — home of the ONE sanctioned regex.

A BylineGrammar is court CONFIG (a profile fact), not court code. Three
styles cover the corpus's families:

  prose     'McKINNON, Justice.' / 'Justice Laurie McKinnon delivered …'
            (the regex grammar; state supremes, Montana prose form)
  abbrev    'GAZIANO, J. This case …' / 'STEGALL, J.: …' / 'BOLDEN, J.
            (concurring).' (mass/conn/kan/tenn/wash families)
  reversed  'JUSTICE JAMES: …' / 'CHIEF JUSTICE ROBERTS delivered the
            opinion of the Court.' (scotus, nj, tex)

'PER CURIAM' and the unsigned-order fallback ('/s/ Name' + title) are shared
across all styles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

_BENCH_WORDS = frozenset({"judge", "judges", "justice", "justices", "chief",
                          "chancellor", "magistrate", "commissioner"})

# Longest-first so 'C.J.'/'P.J.' win over the bare 'J.'.
DEFAULT_ABBREV = (
    ("C.J.", "Chief Justice"),
    ("C. J.", "Chief Justice"),
    ("P.J.", "Presiding Justice"),
    ("P. J.", "Presiding Justice"),
    ("A.R.J.", "Active Retired Justice"),
    ("J.", "Justice"),
)
# AN ANNOUNCEMENT IS NOT A BYLINE. A court that issues each separate writing
# as its own slip still NAMES them in the lead opinion's byline block —
# 'JUSTICE SULLIVAN filed a concurring opinion.' It is a filing verb over an
# INDEFINITE opinion; the writing that IS here opens on 'delivered THE opinion
# of the Court' or on a verbless kind clause ('JUSTICE HUDDLE, concurring.').
# Read as a byline it opened a phantom writing that took the majority's whole
# body and credited the majority to the wrong justice — 13 of tex's 50
# records, and utah/state_v._jennings. Replayed over all 7,823 bylines the
# corpus renders: those are the only two courts it moves, both fixes.
# …AND THE ANNOUNCEMENT MAY NAME THE WRITING BY ITS KIND INSTEAD OF BY THE
# WORD 'OPINION'. nj closes both its syllabus and its majority with 'JUSTICE
# FASCIALE filed a dissent.' — the same filing verb over the same indefinite
# article, naming the writing by what it is. Spelled only as 'opinion', the
# row fell through to the filing-verb branch below and opened a phantom
# writing between the majority and the dissent it was announcing.
_ANNOUNCED_WRITING = re.compile(
    r"^(?:filed|authored|issued|wrote)\s+an?\s+(?:[a-z]+\s+){0,4}"
    r"(?:opinion|dissent|concurrence)s?\b")

_KIND_WORDS = ("concur", "dissent")
# A row closing on a THIRD-PERSON concur/dissent — 'concur.',
# 'dissents.', 'concurred.' — reports who JOINED. The participles
# ('concurring') are that writer's own byline and are deliberately
# absent here.
_JOINER_ROW = re.compile(r"\b(?:concur|dissent)(?:s|red|ted)?\s*\.?$", re.I)
# Only the PARTICIPLES vouch for a titlecase surname; see _prose_parse.
_KIND_PARTICIPLES = ("concurring", "dissenting")
# A PARTICIPATION NOTE NAMES A JUDGE WHO DID NOT WRITE, and it looks like a
# byline in every particular: a surname, a title, and a participial clause
# after the comma. 'Pirtle, Judge, participating on briefs.'
# (nebctapp/state_v._hearnes) and 'Vaughn, J., not participating.' are the
# bench's own bookkeeping about who sat and how — printed at the foot of the
# opinion, and nothing is ever written under them. hearnes rendered as TWO
# writings where the page sets one, the second holding its byline and no body
# at all (the user, 2026-08-21).
#
# The courts that refuse a titlecase surname already reject these, but for an
# unrelated reason: their guard wants a _KIND_PARTICIPLES word and
# 'participating' is not one, so alaska drops 'Henderson, Justice, not
# participating.' while nebctapp — which MUST allow titlecase, it signs
# 'Freeman, Judge.' — keeps it. 28 courts allow titlecase, so the test
# belongs at the parse funnel and is about the CLAUSE, not the letterform.
_PARTICIPATION = re.compile(r"^(?:not\s+)?participating\b", re.I)
_DELIVER_VERBS = ("delivered", "filed", "authored", "announced", "wrote")
_NAME_PREFIXES = ("Mc", "Mac", "De", "Van", "O", "D", "La", "Le", "St")


@dataclass(frozen=True)
class BylineGrammar:
    style: str = "prose"                  # prose | abbrev | reversed | none
    titles: tuple = ("Justice",)          # prose full-title words
    abbrev_titles: tuple = DEFAULT_ABBREV
    rev_titles: tuple = ("JUSTICE", "CHIEF JUSTICE")
    require_bold: bool = False
    accept_delivered: bool = False
    strip_para_marker: bool = False       # '¶ 1. EATON, J. …' (vt, wis)
    allow_titlecase_name: bool = False    # 'Papik, J.' (neb)
    title_suffixes: tuple = ()            # 'W.S.' court-section designators
    # 'OPINION OF THE COURT BY GINOZA, J.' / 'OPINION BY JUDGE McCULLOUGH' /
    # 'Opinion by Arthur, J.' — the author is announced in a HEADING, not a
    # signing byline (haw, ky, pacommwct, md, va families). Opt-in.
    opinion_by_headings: bool = False
    # 'By the Court, BELL, J.:' — nev leads its byline with a court tag.
    strip_by_the_court: bool = False
    # wva prints BOTH 'JUSTICE WOOTON delivered the Opinion of the Court.'
    # and 'TRUMP, Justice:' — when the main style misses, try reversed.
    also_reversed: bool = False
    # The twin for the other direction: virginislands signs the opinion of
    # the Court in PROSE ('HODGE, Chief Justice.') and its separate writings
    # in the ABBREV form ('HODGE, C.J., with whom CABRET, J. joins,
    # concurring in part.'). Declared 'abbrev' alone, the prose form matched
    # nothing and 30 of 32 majorities were credited to the CLERK's conformed
    # sign-off at the foot of the document — two of them to a deputy clerk.
    also_abbrev: bool = False
    # A TITLE-CASE name is a byline ONLY when its tail is a KIND clause.
    # wva signs three ways and the third ('Justice Wooton, dissenting:')
    # cannot be admitted outright: bare, the same rule takes 'Ewing,
    # Justice:' — the opinion heading printed AFTER the syllabus on a record
    # the page-1 announcement already opened — and a slip caption's second
    # row ('Barki, Judge, Circuit Court of Ohio County, and Shawn Pethtel').
    # Measured on wva: with the clause required one document gains its
    # author and none changes; without it, three change for the worse.
    titlecase_kind_only: bool = False
    # An en banc majority names its joiners and closes on a PERIOD: 'Jerry E.
    # Smith, Circuit Judge, joined by Elrod, Chief Judge, and Jones, …,
    # Circuit Judges.' The joiner list is read as a roster tail by default,
    # because ca2's en banc VOTE LINE has the same shape and is not a byline;
    # ca2's byline twin is told apart by its ':' terminal. A court that ends
    # the real byline on a period says so here — without it the majority
    # assembles unbylined, and an authored opinion is typed 'order' (ca5).
    joined_by_period: bool = False


@dataclass(frozen=True)
class Byline:
    name: str
    title: str
    kind: str | None      # concurring / dissenting / … (raw clause)
    end: int              # index past the byline clause; rest is inline body


def _strip_name_prefix(tok: str) -> str:
    for p in _NAME_PREFIXES:
        if tok.startswith(p) and len(tok) > len(p) and tok[len(p)].isupper():
            return tok[len(p):]
    return tok


def is_caps_name(name: str, max_tokens: int = 4) -> bool:
    """ALL-CAPS author name: middle initials ('RHONDA K. WOOD'), mixed-case
    prefixes ('McDONALD', 'VanDYKE'), apostrophes ('D'AURIA'). A JOINT
    byline's connector is not a caps token ('MILLETT and GARCIA')."""
    toks = [t for t in name.split() if t not in ("and", "y", "&", "e")]
    if not toks or len(toks) > max_tokens:
        return False
    for tok in toks:
        core = _strip_name_prefix(
            tok.rstrip(".").replace("'", "").replace("’", "").replace("-", ""))
        if not (core and core.isalpha() and core.isupper()):
            return False
    return True


def is_per_curiam(text: str) -> bool:
    t = text.strip()
    if t.endswith("."):
        t = t[:-1]
    return " ".join(t.split()) == "PER CURIAM"


def strip_trailing_mark(text: str) -> str:
    """'McCOOL, Justice.1' -> 'McCOOL, Justice.' (a footnote reference on the
    byline). A symbol font's PUA star (0xF02A — la sets 'McCALLUM, J.')
    is a mark too."""
    marks = set("0123456789*†‡∗⁎﹡＊")
    t = text.rstrip()
    i = len(t)
    while i > 0 and (t[i - 1] in marks or 0xF000 <= ord(t[i - 1]) < 0xF100):
        i -= 1
    return t[:i].rstrip() if i < len(t) else text


def spread_tight_punctuation(text: str) -> tuple[str, list[int]]:
    """Insert the space a tight text layer omits after '.'/',' —
    'MARY L.WAGNER,J.,delivered' (tenn's small-caps bylines carry no space
    glyphs) reads as 'MARY L. WAGNER, J., delivered'. After a comma any
    letter triggers; after a period only an UPPERCASE letter ('F.4th' and
    'e.g.' stay whole). Returns (normalized, positions of inserted spaces
    in the NORMALIZED string) so a match offset can be mapped back."""
    out: list[str] = []
    inserts: list[int] = []
    for i, ch in enumerate(text):
        out.append(ch)
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if ((ch == "," and nxt.isalpha())
                or (ch == "." and nxt.isalpha() and nxt.isupper())):
            inserts.append(len(out))
            out.append(" ")
    return "".join(out), inserts


def para_marker_len(text: str) -> int:
    """Length of a leading '¶ N.' / '¶N' marker (0 if none)."""
    if not text.startswith("¶"):
        return 0
    i, n = 1, len(text)
    while i < n and text[i] == " ":
        i += 1
    while i < n and (text[i].isdigit() or text[i] == "."):
        i += 1
    while i < n and text[i] == " ":
        i += 1
    return i


def _tail_index(text: str, title: str, ntokens: int) -> int:
    """Where the tail begins in TEXT, counted in the ORIGINAL spacing.

    `_reversed` rebuilds the tail as `" ".join(tokens[consumed:])`, which
    collapses every run of whitespace, so `len(text) - len(tail)` overshoots
    the real offset by exactly the number of spaces collapsed — and callers
    use that number as a character index into the uncollapsed row
    (`assemble.py` slices the row at `byline.end`). pa sets its decided-date
    in a second column, so the row arrives double-spaced
    ('JUSTICE MUNDY DECIDED:  APRIL 30, 2026') and the byline ate one
    character of it: author 'JUSTICE MUNDY D', first body paragraph
    'ECIDED:  APRIL 30, 2026'. Any court whose byline row carries a run of
    spaces in its tail was exposed.

    The index is recomputed by walking the row itself: skip `ntokens`
    whitespace-separated tokens, then the separators the tail is lstripped
    of.
    """
    body = text[len(title):]
    base = len(title) + (len(body) - len(body.lstrip()))
    rest = body.strip()
    i = 0
    for _ in range(ntokens):
        while i < len(rest) and rest[i].isspace():
            i += 1
        while i < len(rest) and not rest[i].isspace():
            i += 1
    while i < len(rest) and (rest[i].isspace() or rest[i] == ","):
        i += 1
    return base + i


class BylineParser:
    _ABBREV_LIST = re.compile(
        r"^(?:[A-Z][A-Za-z'’‑-]+,\s*(?:[A-Z]\.\s*){1,4}"
        r"(?:,\s*(?:and\s+)?|and\s+|$))+$")

    def __init__(self, grammar: BylineGrammar):
        self.g = grammar
        titles = "|".join(re.escape(t) for t in grammar.titles)
        # THE one sanctioned regex: name + optional title prefix + title +
        # optional kind, with the alternation/backtracking a hand parser gets
        # subtly wrong.
        # Unicode-aware letter classes ([^\W\da-z_] = any uppercase letter):
        # GELPÍ and CARREÑO-COLL are bylines too.
        # The name may OPEN on initials ('R. NELSON', 'S.R. THOMAS',
        # 'L.R. SMITH') — the circuits abbreviate a shared surname's holder —
        # and may be JOINT ('MERRIAM and KAHN, Circuit Judges, writing
        # jointly…'), which pluralizes the title.
        _NAME = (r"(?:(?:[^\W\da-z_]\.\s*){1,2})?"
                 r"(?:Mc|Mac|S[Tt]\.\s?)?[^\W\da-z_][^\W\d_]+"
                 r"(?:[\s-](?:[^\W\da-z_]\.|[^\W\da-z_][^\W\d_]+)){0,4}"
                 r"(?:\s+and\s+(?:Mc|Mac|S[Tt]\.\s?)?[^\W\da-z_][^\W\d_]+)?")
        _TITLE = (r"(?:United\s+States\s+)?"
                  r"(?:Chief\s+|Presiding\s+|Associate\s+|Senior\s+"
                  r"|Retired\s+|Acting\s+)?"
                  rf"(?:{titles})s?"
                  r"(?:\s+for\s+the\s+[^,.:]{3,60})?")
        self._prose = re.compile(
            rf"^(?P<name>{_NAME})"
            r"(?:,\s+(?:[Jj][Rr]\.|[Ss][Rr]\.|II|III|IV|[^\W\da-z_]\.))?"
            rf",\s+(?P<title>{_TITLE})"
            r"(?:"
            r"\s*\((?P<kind1>[^)]+)\)"
            r"|,\s+(?P<kind2>[^.]+?)"
            r")?"
            r"\s*[.:]?$"
        )
        # A kind clause may CONTAIN periods ('…joined by LIVINGSTON, Chief
        # Judge, except as to Part II.E.1, dissenting from the denial of
        # rehearing en banc:') — admitted only when it ENDS on a participle
        # clause, which prose never does at a line start with this shape.
        self._prose_kindtail = re.compile(
            rf"^(?P<name>{_NAME})"
            r"(?:,\s+(?:[Jj][Rr]\.|[Ss][Rr]\.|II|III|IV|[^\W\da-z_]\.))?"
            rf",\s+(?P<title>{_TITLE})"
            r",\s+(?P<kind2>.+?(?:concurring|dissenting)[^.]*?)"
            r"\s*[.:]?$"
        )
        # The INLINE form: the byline ends at its period and the opinion's
        # first sentence follows on the same line ('BARRON, Chief Judge.  The
        # U.S. Department …' — the circuits' house style).
        self._prose_inline = re.compile(
            r"^(?P<name>(?:(?:[^\W\da-z_]\.\s*){1,2})?"
            r"(?:Mc|Mac|S[Tt]\.\s?)?[^\W\da-z_][^\W\d_]+"
            r"(?:[\s-](?:[^\W\da-z_]\.|[^\W\da-z_][^\W\d_]+)){0,4}"
            r"(?:\s+and\s+(?:Mc|Mac|S[Tt]\.\s?)?[^\W\da-z_][^\W\d_]+)?)"
            r"(?:,\s+(?:[Jj][Rr]\.|[Ss][Rr]\.|II|III|IV|[^\W\da-z_]\.))?"
            rf",\s+(?P<title>"
            r"(?:United\s+States\s+)?"
            r"(?:Chief\s+|Presiding\s+|Associate\s+|Senior\s+|Retired\s+|Acting\s+)?"
            rf"(?:{titles})s?)"
            r"(?:\s*\((?P<kind1>[^)]+)\)|,\s+(?P<kind2>[^.]+?))?"
            r"[.:](?=\s)"
        )

    def parse(self, text: str) -> Byline | None:
        from bisect import bisect_right
        text = text.strip()
        # A LETTER-SPACED SURNAME is still that surname: arizctapp signs
        # 'M O R S E, Judge:' and every one of its opinions read as
        # authorless. Fold the leading spaced run and parse normally; the
        # folded form can't match this pattern again, so no recursion. The
        # reported end is shifted back by the spaces removed so the caller
        # still slices the ORIGINAL text correctly.
        _sp = re.match(r"^((?:[A-Za-z] ){2,}[A-Za-z])(?=[,.:;]|\s|$)", text)
        if _sp:
            _run = _sp.group(1)
            _b = self.parse(_run.replace(" ", "") + text[len(_run):])
            if _b is None:
                return None
            return Byline(_b.name, _b.title, _b.kind,
                          _b.end + _run.count(" "))
        # A FOOTNOTE REFERENCE ON THE BYLINE belongs to the byline's ROW,
        # not to the body after it: 'SELLERS, Justice.1' (ala) parses on the
        # stripped text, so the mark fell past `end` and the caller filed it
        # as an inline paragraph holding just '1'. Strip it, parse, and give
        # the length back when the clause runs to the end of what is left.
        _bare = strip_trailing_mark(text)
        if _bare != text:
            _b = self.parse(_bare)
            if _b is None:
                return None
            _e = _b.end + (len(text) - len(_bare)) \
                if _b.end >= len(_bare) else _b.end
            return Byline(_b.name, _b.title, _b.kind, _e)
        offset = 0
        if self.g.strip_para_marker:
            n = para_marker_len(text)
            offset, text = n, text[n:]
        text = strip_trailing_mark(text)
        if self.g.strip_by_the_court and text.lower().startswith("by the court,"):
            rest = text[len("by the court,"):]
            offset += len(text) - len(rest.lstrip())
            text = rest.strip()
        # Match on SPREAD text (tenn's small-caps bylines carry no space
        # glyphs: 'MARY L.WAGNER,J.,delivered'); every end offset is mapped
        # back to the caller's string before it leaves.
        text, _ins = spread_tight_punctuation(text)
        _back = lambda e: e - bisect_right(_ins, e - 1)  # noqa: E731
        if is_per_curiam(text):
            return Byline("PER CURIAM", "per curiam", None,
                          offset + _back(len(text)))
        # Inline per curiam: 'PER CURIAM.  Appellant …'. The CAPS form may be
        # followed by anything; the TITLECASE form ('Per Curiam:*' — ca5)
        # must be punctuation-anchored so prose ('per curiam review is…')
        # never matches.
        if text.upper().startswith("PER CURIAM"):
            rest = text[len("PER CURIAM"):]
            caps = text[:10] == "PER CURIAM"
            # Footnote stars may sit between the name and its colon
            # ('PER CURIAM**:' — utah; the marks are ** or PUA glyphs).
            stars = 0
            while stars < len(rest) and (rest[stars] in "*†‡∗⁎﹡＊"
                                         or rest[stars].isdigit()
                                         or 0xF000 <= ord(rest[stars]) < 0xF100):
                stars += 1
            rest = rest[stars:]
            # AN EM DASH CLOSES THE BYLINE as surely as a period does —
            # wash opens every inline writing on one ('PER CURIAM1— As
            # explained below…'), and set tight against the name a dash is
            # never prose. Without it a whole per-curiam lead opinion, pages
            # 1-3, rendered INSIDE the headmatter section.
            if rest[:1] in (".", ":", ",", "—", "–") or rest == "" \
                    or (caps and rest[:1] == " "):
                end = (len("PER CURIAM") + stars
                       + (1 if rest[:1] in ".:," else 0))
                return Byline("PER CURIAM", "per curiam", None,
                              offset + _back(end))
        # A PANEL ROSTER opener ('Before Elrod, Chief Judge, and SMITH and
        # WILSON, Circuit Judges' — ca5 prints it before every en banc
        # writing) is never a byline, whatever grammar follows it.
        if text[:7].lower() in ("before ", "before:"):
            return None
        # 'HONORABLE PHILLIP J. SHEPHERD, JUDGE' — the trial judge named in
        # a caption's appeal-from block, never an author.
        if text.lower().startswith(("honorable ", "the honorable ")):
            return None
        if self.g.opinion_by_headings:
            got = self._opinion_by(text)
            if got is not None:
                return Byline(got.name, got.title, got.kind,
                              _back(got.end) + offset)
        if self.g.style == "none":
            return None
        # 'Statement of JUSTICE SOTOMAYOR, with whom …, respecting the
        # denial of certiorari.' — a WRITING head (scotus orders), though its
        # clause carries no concurring/dissenting participle.
        # Terminal punctuation required: the clause wraps ('…respecting the
        # denial' / 'of certiorari.') and accepting a partial line would
        # leak its continuation into the body — the caller's wrap-join
        # assembles the full clause and retries.
        if (text.startswith("Statement of ")
                and text.rstrip().endswith((".", ":"))):
            rest = text[len("Statement of "):].strip()
            # NAME-led statement head: 'Statement of ANNETTE KINGSLAND
            # ZIEGLER, J., with whom …' (wis orders — abbrev grammar).
            mm = re.match(r"^((?:[A-Z][A-Za-z'’.\-]*\s+){0,3}"
                          r"[A-Z][A-Za-z'’\-]+),\s*((?:[A-Z]\.\s*){1,4})",
                          rest)
            if mm and is_caps_name(mm.group(1)):
                return Byline(mm.group(1), mm.group(2).strip(), "statement",
                              offset + _back(len(text)))
            for title in sorted(self.g.rev_titles, key=len, reverse=True):
                if not rest.startswith(title + " "):
                    continue
                nm = []
                for tok in rest[len(title):].split():
                    bare = tok.rstrip(",.:")
                    if is_caps_name(bare, max_tokens=1):
                        nm.append(bare)
                        if tok[-1:] in ",.:":
                            break
                    else:
                        break
                if nm:
                    return Byline(" ".join(nm), title.title(), "statement",
                                  offset + _back(len(text)))
        if self.g.style == "abbrev":
            got = self._abbrev(text)
        elif self.g.style == "reversed":
            got = self._reversed(text)
        else:
            got = self._prose_parse(text)
        if got is None and self.g.also_reversed and self.g.style != "reversed":
            got = self._reversed(text)
        if got is None and self.g.also_abbrev and self.g.style != "abbrev":
            got = self._abbrev(text)
        if got is None and self.g.titlecase_kind_only:
            # clear the flag on the inner grammar, or parse() calls itself
            alt = BylineParser(replace(
                self.g, allow_titlecase_name=True,
                titlecase_kind_only=False)).parse(text)
            if alt is not None and alt.kind and any(
                    k in alt.kind.lower() for k in _KIND_WORDS):
                return alt
        if got is None:
            return None
        # WHO SAT IS NOT WHO WROTE — see _PARTICIPATION.
        if got.kind and _PARTICIPATION.match(got.kind.strip()):
            return None
        return Byline(got.name, got.title, got.kind, _back(got.end) + offset)

    # ---- 'OPINION BY' headings ---------------------------------------------

    # A FOOTNOTE MARK MAY HANG ON THE PAPER'S NAME. pacommwct/passhe_v._plrb
    # sets 'OPINION1 BY JUDGE FIZZANO CANNON' — the court's note about how the
    # panel was constituted, hung on the word 'OPINION' — and with '\s+BY'
    # demanded straight after the noun the heading matched nothing, so the
    # whole byline row stayed in the writing as its first paragraph.
    _OPINION_BY = re.compile(
        r"^(?P<kind>CONCURRING(?:\s*(?:/|AND|&)\s*DISSENTING)?"
        r"|DISSENTING(?:\s*(?:/|AND|&)\s*CONCURRING)?)?\s*"
        r"(?:MEMORANDUM(?:\s+OPINION)?|OPINION|ORDER)"
        r"\s*[\d*†‡]{0,3}"
        r"(?:\s+OF\s+THE\s+COURT)?\s+BY[:\s]\s*"
        r"(?P<rest>.+?)\s*:?$", re.IGNORECASE)

    # 'OPINION' OVER 'PER CURIAM' — the heading with no 'BY' in it, because an
    # unsigned paper has no one to name. pacommwct/g._wilkins_v._pa_oag_oor
    # folds it over two rows, so the joined heading reads 'OPINION PER CURIAM'
    # and the BY-form could not match it: core took 'PER CURIAM' off the second
    # row alone and left the first, so the writing opened on
    # 'OPINION FILED: June 26, 2026 Glue Wilkins…'. Bounded to the whole row,
    # so prose that merely mentions a per curiam opinion cannot match.
    _OPINION_PER_CURIAM = re.compile(
        r"^(?:MEMORANDUM\s+|CONCURRING\s+|DISSENTING\s+)*"
        r"(?:OPINION|MEMORANDUM|ORDER)\s*[\d*†‡]{0,3}"
        r"\s+PER\s+CURIAM\.?$", re.IGNORECASE)

    _OPINION_BY_ES = re.compile(
        r"^Opini[oó]n\s+(?P<kind>disidente|concurrente|de conformidad)?\s*"
        r"(?:del Tribunal\s+)?emitida por\s+(?P<rest>.+?)\s*[.:]?$",
        re.IGNORECASE)
    _ES_TITLE_WORDS = frozenset(
        {"el", "la", "juez", "jueza", "asociado", "asociada", "presidente",
         "presidenta", "señor", "señora", "senor", "senora"})

    def _opinion_by(self, text: str) -> Byline | None:
        """'OPINION OF THE COURT BY GINOZA, J.' / 'OPINION BY JUDGE
        McCULLOUGH' / 'Opinion by Arthur, J.' / 'DISSENTING OPINION BY
        JUSTICE KELLER' — the heading that IS the byline in the haw / ky /
        pacommwct / md families. Also the Spanish form: 'Opinión del
        Tribunal emitida por la Jueza Asociada Rivera García' (prsupreme).
        Bounded: the whole line is the heading."""
        # A 'FILED: JULY 31 2026' ROW-MATE joins the heading's row
        # (pasuperct sets the date flush-right beside the byline) — the
        # wide join gap separates it from the heading's own clause.
        text = re.sub(r"\s+FILED\s*:.*$|\s{2,}FILED\b.*$", "", text.strip(),
                      flags=re.IGNORECASE)
        es = self._OPINION_BY_ES.match(text)
        if es is not None and len(text) <= 110:
            toks = es.group("rest").split()
            while toks and toks[0].lower().strip(".,") in self._ES_TITLE_WORDS:
                toks.pop(0)
            if toks and all(t[:1].isupper() for t in toks[:3]):
                kind = {None: None, "disidente": "dissenting",
                        "concurrente": "concurring",
                        "de conformidad": "concurring"}[
                    (es.group("kind") or "").lower() or None]
                return Byline(" ".join(toks[:4]), "Juez", kind, len(text))
        if self._OPINION_PER_CURIAM.match(text):
            return Byline("PER CURIAM", "per curiam", None, len(text))
        m = self._OPINION_BY.match(text)
        if m is None or len(text) > 90:
            return None
        rest = m.group("rest").strip()
        kind = (m.group("kind") or "").lower() or None
        # 'OPINION BY PER CURIAM' — the announcement form of an unsigned
        # paper, which names no judge because none signed it.
        if is_per_curiam(rest) or rest.upper().rstrip(".") == "PER CURIAM":
            return Byline("PER CURIAM", "per curiam", kind, len(text))
        # Title-led ('JUDGE McCULLOUGH', 'JUSTICE KELLER', 'SENIOR JUDGE X')
        # or name-led ('GINOZA, J.', 'Arthur, J.').
        # 'PRESIDENT JUDGE' IS A BENCH TITLE. Pennsylvania's Commonwealth and
        # Superior Courts are led by a President Judge, and without the word
        # the title-led branch failed on 'OPINION BY PRESIDENT JUDGE COHN
        # JUBELIRER' — pacommwct/z._leger_v._g.l._martin came back with NO
        # author and its heading, its judge and its FILED date all rendered as
        # the opinion's opening paragraph.
        tl = re.match(
            r"(?:THE\s+)?(?P<title>(?:VICE\s+)?"
            r"(?:CHIEF\s+|SENIOR\s+|PRESIDING\s+|PRESIDENT\s+)?"
            r"(?:JUSTICE|JUDGE))\s+(?P<name>.+)$", rest, re.IGNORECASE)
        if tl:
            name = tl.group("name").strip().rstrip(".,:")
            title = tl.group("title").title()
        else:
            name = rest.split(",")[0].strip()
            after = rest[len(name):].lstrip(", ").rstrip().replace(" ", "")
            title = next((full for ab, full in self.g.abbrev_titles
                          if after in (ab.replace(" ", ""),
                                       ab.replace(" ", "").rstrip("."))), "")
            if not title:
                return None
        toks = name.split()
        if not (0 < len(toks) <= 4 and all(
                t[:1].isalpha() and t[:1].isupper() for t in toks)):
            return None
        return Byline(name, title, kind, len(text))

    # ---- prose -------------------------------------------------------------

    def _prose_parse(self, text: str) -> Byline | None:
        m = self._prose.match(text) or self._prose_kindtail.match(text)
        end = len(text)
        if not m:
            m = self._prose_inline.match(text)
            if not m:
                return None
            end = m.end()
            tail = text[end:].lstrip()
            # The inline tail must open like a sentence, not a roster
            # continuation ('…, Chief Judge, and X, Circuit Judges,').
            if tail and not (tail[0].isupper() or tail[0] in "“\"‘'(["):
                return None
            # A DISPOSITION tail is an appeal-history row ('M. Alioth,
            # Judge. Affirmed.' — nebctapp's trial-judge line), not a byline.
            if tail and tail.split()[0].rstrip(".,;") in (
                    "Affirmed", "Reversed", "Vacated", "Dismissed",
                    "Remanded", "Modified", "Exceptions"):
                return None
        name = m.group("name")
        # A judge's SURNAME is never itself a bench word: a wrapped byline
        # continuation opening 'Judge, …' must not read as a byline.
        if name.rstrip(".").lower() in _BENCH_WORDS:
            return None
        # The SHORT title form always terminates its byline ('R. NELSON,
        # J., concurring:'); the unterminated twin is a RUNNING HEAD
        # ('BRANCH, J., Dissenting' — ca11 prints one atop every page of
        # the writing).
        if (m.group("title") == "J." and m.end() >= len(text)
                and not text.rstrip().endswith((":", "."))):
            return None
        # A PLURAL title belongs to a JOINT byline only ('MERRIAM and KAHN,
        # Circuit Judges'); on a single name it is a wrapped roster's tail
        # ('…ROVNER, and JACKSON-' / 'AKIWUMI, Circuit Judges.').
        if m.group("title").rstrip(". ").endswith("s") and " and " not in name:
            return None
        gd = m.groupdict()
        kind = gd.get("kind1") or gd.get("kind2")
        # A designated visitor signs 'David J. NOVAK, United States District
        # Judge for the Eastern District of Virginia, sitting by
        # designation:' — the clause is part of the SIGNATURE, not a kind,
        # and it vouches for the titlecase name.
        sitting = bool(kind) and " ".join(kind.lower().split()).startswith(
            "sitting by designation")
        # The titlecase designated-visitor byline OPENS its opinion and ends
        # ':' ('David J. NOVAK, …, sitting by designation:'); the roster row
        # twin ends '.' ('Tolliver, …, sitting by designation.').
        if sitting and not is_caps_name(name) \
                and not text.rstrip().endswith(":"):
            return None
        if sitting:
            kind = None
        # A prose byline sets its surname in CAPS ('GELPÍ, Circuit Judge.');
        # the titlecase twin is the PANEL roster ('Gelpí, Circuit Judge,').
        # Courts whose prose bylines are titlecase opt out via the grammar —
        # and a PARTICIPLED kind vouches for titlecase anywhere ('Grasz,
        # Circuit Judge, concurring in part…' — a roster row never carries
        # one).
        if not self.g.allow_titlecase_name and not is_caps_name(name):
            # A NOUN IS NOT A PARTICIPLE. The 'concur'/'dissent' stems also
            # match the nouns a court uses to REFER to a writing — idaho's
            # majority cites its own at 'Meyer, J., special concurrence,
            # infra, at 25', mid-paragraph at the body rail — and a
            # titlecase surname vouched for by a noun opens a phantom
            # writing there (39 blocks, on a record the page sets as two).
            if not sitting and not (
                    kind and any(w in kind.lower()
                                 for w in _KIND_PARTICIPLES)):
                return None
        # THIRD-PERSON 'joins' is a joinder announcement ('X, J., joins the
        # opinion of…'), never a byline. The PASSIVE 'joined by' inside a
        # kind is how an en banc writing names its joiners ('MENASHI, Circuit
        # Judge, joined by PARK…, concurring in the denial…') and stays.
        if kind and "joins" in kind.lower() \
                and not kind.lower().startswith("with whom"):
            return None
        # Likewise 'dissents'/'concurs' opening the clause ('Steven J.
        # Menashi, Circuit Judge, dissents by opinion from the denial…') —
        # an announcement of a writing found elsewhere. And a PROSE kind
        # never opens on a deliver verb or third-person past: 'MURPHY, J.,
        # delivered the opinion of the court in which SUTTON…' is ca6's
        # announcement block, not the byline ('MURPHY, Circuit Judge.'
        # follows it).
        kw = [w.strip(".,;:") for w in kind.lower().split()] if kind else []
        if kw and (kw[0] in ("dissents", "concurs", "concurred", "dissented",
                             "dissent", "concur", *_DELIVER_VERBS)
                   # 'joined the opinion' is an announcement; the PASSIVE
                   # 'joined by Y…' is an en banc writing's joiner list.
                   or (kw[0] == "joined" and kw[1:2] != ["by"])):
            return None
        # A 'with whom' clause with NO participle is a byline cut mid-wrap
        # ('BERZON, Circuit Judge, with whom W.' — the joiner list continues
        # on the next line); refusing it here lets the caller's wrap-join
        # find the whole clause.
        if kind and kind.lower().startswith("with whom") and not any(
                w in kind.lower() for w in _KIND_WORDS):
            return None
        # 'FOR THE COURT' / 'FOR THE MAJORITY' is a majority marker, not a
        # kind ('SULLIVAN, JUSTICE, FOR THE COURT:' — miss; 'SEITZ, Chief
        # Justice, for the Majority:' — del).
        if kind and " ".join(kind.upper().split()).rstrip(":.") in (
                "FOR THE COURT", "FOR THE MAJORITY"):
            kind = None
        # A kind that is EXACTLY a second title ('BYBEE, J., Circuit Judge:'
        # — ca9 doubles the short and long form) folds into the title.
        if kind and " ".join(kind.lower().split()) in (
                "circuit judge", "district judge", "chief judge",
                "senior circuit judge", "judge", "justice"):
            kind = None
        # A kind that NAMES the bench with no participle is a roster tail
        # ('LIVINGSTON, Chief Judge, LYNCH and MENASHI, Circuit Judges' —
        # ca2's en banc vote line), never a byline. EXCEPT the en banc
        # majority form 'Duncan, Circuit Judge, joined by Elrod, Chief
        # Judge, …, Circuit Judges:' — 'joined by' opens the clause and the
        # ':' terminal is the byline's own (ca5); the vote-line twin never
        # ends on a colon.
        if kind and not any(w in kind.lower() for w in _KIND_WORDS) \
                and any(w in kind.lower() for w in ("judge", "justice")) \
                and not (kind.lower().startswith("joined by")
                         and (text.rstrip().endswith(":")
                              or (self.g.joined_by_period
                                  and text.rstrip().endswith(".")))):
            return None
        # A kind that IS a caps name ('DEBRA ANN LIVINGSTON, Chief Judge,
        # RAYMOND J…' — the vote line lists the next judge) is a roster too.
        if kind and is_caps_name(kind.replace(",", " ").strip(" .")):
            return None
        return Byline(name, m.group("title"), kind, end)

    # ---- abbrev ------------------------------------------------------------

    def _name_ok(self, name: str) -> bool:
        if is_caps_name(name):
            return True
        if not self.g.allow_titlecase_name:
            return False
        toks = name.split()
        if not toks or len(toks) > 4:
            return False
        return all(t[:1].isupper() and t.rstrip(".").replace("'", "").isalpha()
                   for t in toks)

    def _abbrev(self, text: str) -> Byline | None:
        text = text.replace(" ", " ").strip()
        if "," not in text:
            return None
        # A jointly-signed PANEL LIST byline ('DOW, J., MURRAY, J., and
        # STOKES, A.R.J.' — me sets a conduct matter's opinion under the
        # full list). Every element must be a NAME, DOTTED-TITLE pair —
        # a 'Present:' roster or a 'MEAD, CONNORS, … JJ.' bench list
        # never covers the whole string that way.
        if self._ABBREV_LIST.match(text) and text.count(",") >= 3:
            first_title = re.search(r",\s*((?:[A-Z]\.\s*){1,4})", text)
            return Byline(text.rstrip("., "),
                          first_title.group(1).strip()
                          if first_title else "J.", None, len(text))
        name = text.split(",", 1)[0].strip()
        if not self._name_ok(name):
            return None
        after = text.split(",", 1)[1].lstrip()
        for sfx in ("SR.", "JR.", "SR", "JR", "III", "II", "IV"):
            rest = after[len(sfx):].lstrip()
            if after.startswith(sfx) and rest.startswith(","):
                name = f"{name}, {sfx}"
                after = rest[1:].lstrip()
                break
        # A qualifier may precede the abbrev title ('ROBIE, Acting P. J.'
        # — calctapp signs its acting presiding justice that way).
        _pfx = ""
        for _p in ("Acting ", "Presiding ", "Associate "):
            if after.startswith(_p):
                _pfx, after = _p, after[len(_p):]
                break
        for ab, full in self.g.abbrev_titles:
            if not after.startswith(ab):
                continue
            if _pfx:
                full = _pfx + full
            end = text.find(ab) + len(ab)
            tail = text[end:].lstrip()
            stars = 0
            while stars < len(tail) and tail[stars] in "*†‡∗⁎﹡＊":
                stars += 1
            # A FOOTNOTE REFERENCE ON THE TITLE is set TIGHT against it
            # ('MONTOYA-LEWIS, J.1 (dissenting)' — wash). Spaced off, a
            # numeral is the next thing the row states and not a mark at
            # all, so the digit form is peeled only where the page set no
            # space before it.
            if not stars and text[end:end + 1].isdigit():
                while stars < len(tail) and tail[stars].isdigit():
                    stars += 1
            if stars:
                end += (len(text[end:]) - len(tail)) + stars
                tail = tail[stars:].lstrip()
            low = tail.lower()
            nxt = tail[:1]
            if nxt == ":":
                ci = text.find(":", end)
                return Byline(name, full, None, ci + 1)
            head = tail.lstrip(", (").lower()
            # An ADVERB may precede the participle — 'specially concurring',
            # 'respectfully dissenting', 'partially concurring' are ordinary
            # opinion grammar, not a court's local dialect. Step over one so
            # the clause underneath is read normally.
            # A SEMICOLON PUNCTUATES A VOTE LINE. Stripping only '.' and ','
            # left 'concurred;' as the first word, so the third-person guard
            # below could never match the form New Hampshire prints
            # ('DONOVAN, J., concurred; ABRAMSON, J., …').
            _bare = head
            _PUNCT = ".,;:"
            _w0 = _bare.split()[0].rstrip(_PUNCT) if _bare.split() else ""
            if _w0.endswith("ly") and len(_bare.split()) > 1:
                _bare = _bare.split(None, 1)[1]
            first_word = (_bare.split()[0].rstrip(_PUNCT)
                          if _bare.split() else "")
            # THE PAST TENSE IS AS THIRD-PERSON AS THE PRESENT. New
            # Hampshire closes its opinions with a vote line in the preterite
            # — 'DONOVAN, J., concurred; ABRAMSON, J., retired superior court
            # justice, specially assigned under RSA 490:3, II, concurred.' —
            # and listing only 'concurs'/'dissents' here read the first name
            # as a byline and opened a phantom concurrence whose whole body
            # was the rest of the sentence (nh/atl._anesthesia). The
            # vocabulary was already right in `_JOINER_ROW`, which accepts
            # '(?:s|red|ted)?'; only this guard was short of it. The
            # PARTICIPLES are deliberately absent: 'concurring' IS that
            # writer's own byline.
            if first_word in ("concurs", "dissents",
                              "concurred", "dissented"):
                return None    # third-person: an ANNOUNCEMENT, not a byline
            # 'Brown, J. and DeBoer, J., concur.' — a JOINER ROW, not a
            # byline. The row names the judges who joined the writing above
            # it and closes on a THIRD-PERSON verb; read as a byline it
            # opened a phantom writing credited to the first joiner
            # (indctapp/shirley_e._melton). The participles are left alone,
            # so a joint 'and JONES, J., dissenting.' still reads as one.
            if first_word == "and" and _JOINER_ROW.search(text):
                return None
            if nxt in (",", "(") and any(_bare.startswith(k)
                                         for k in _KIND_WORDS):
                stop = next((k for k in range(end, len(text))
                             if text[k] in ".)"), -1)
                if stop != -1:
                    if (text[stop] == ")" and stop + 1 < len(text)
                            and text[stop + 1] == "."):
                        stop += 1
                    kind = text[end:stop + 1].strip(" .()—–,")
                    return Byline(name, full, kind, stop + 1)
            if nxt == ",":
                if not tail.lstrip(", ").strip():
                    return Byline(name, full, None, len(text))
                after_title = tail.lstrip(", ")
                for sfx in self.g.title_suffixes:
                    if after_title.startswith(sfx):
                        after_title = after_title[len(sfx):].lstrip(", ")
                        break
                if self.g.accept_delivered:
                    verb = (after_title.lower().split() or [""])[0]
                    # 'X, J., filed a separate opinion concurring…' is the
                    # majority's ANNOUNCEMENT of another writing (which
                    # arrives as its own document), not a byline.
                    if verb == "filed" and "separate" in low:
                        return None
                    if verb in _DELIVER_VERBS:
                        # 'delivered the opinion of the Court, in which …
                        # joined. X, J., filed a separate opinion
                        # concurring…' — the announcement NAMES the other
                        # writings; a kind word anywhere in that tail says
                        # nothing about THIS writing, which delivered the
                        # opinion.
                        return Byline(name, full, None, len(text))
                # The 'with whom' form ("D'AURIA, J., with whom MULLINS,
                # C. J., … join, dissenting") is a byline in EVERY abbrev
                # court, not just the delivered-announcement ones.
                if after_title.lower().startswith("with whom") and any(
                        k in low for k in _KIND_WORDS):
                    return Byline(name, full,
                                  text[end:].strip(" ,.—–"), len(text))
                # 'EMFINGER, J., FOR THE COURT:' — a majority marker (miss).
                if " ".join(after_title.upper().split()).rstrip(":.") in (
                        "FOR THE COURT", "FOR THE MAJORITY"):
                    return Byline(name, full, None, len(text))
                return None
            return Byline(name, full, None, end)
        return None

    # ---- reversed (title-first) ---------------------------------------------

    def _reversed(self, text: str) -> Byline | None:
        """'JUSTICE THOMAS, dissenting.' / 'CHIEF JUSTICE ROBERTS delivered
        the opinion of the Court.' / 'JUSTICE JAMES: …'"""
        for title in sorted(self.g.rev_titles, key=len, reverse=True):
            if not text.startswith(title + " "):
                continue
            rest = text[len(title):].strip()
            tokens = rest.split()
            consumed = 0
            saw_colon = False
            for tok in tokens:
                bare = tok.rstrip(",.:")
                # A DATE LABEL fused onto the row is never part of the name
                # ('JUSTICE MUNDY DECIDED: MAY 19, 2026' — pa).
                if bare.upper() in ("DECIDED", "FILED", "ARGUED",
                                    "SUBMITTED"):
                    break
                ok = is_caps_name(bare, max_tokens=1)
                if not ok and self.g.allow_titlecase_name:
                    core = bare.rstrip(".").replace("'", "").replace("’", "")
                    ok = bool(core) and core[0].isupper() and core.isalpha()
                # A middle INITIAL keeps its dot and keeps the walk going
                # ('Katherine M. Bidegaray'); other trailing punctuation ends
                # the name.
                is_initial = len(bare) == 1 and tok.endswith(".")
                if ok:
                    consumed += 1
                    if tok.endswith(":"):
                        saw_colon = True
                    if tok[-1:] in ",:" or (tok.endswith(".") and not is_initial):
                        break
                else:
                    break
            if not consumed:
                return None
            name = " ".join(t.rstrip(",.:") if not (len(t.rstrip(",.:")) == 1
                                                    and t.endswith("."))
                            else t
                            for t in tokens[:consumed])
            after = " ".join(tokens[consumed:]).lstrip(" ,")
            # A GENERATIONAL SUFFIX past the name's comma is part of the
            # name, not a tail clause — the abbrev path already knows this.
            # Without it 'JUSTICE WESLEY G. RUSSELL, JR.' was rejected
            # outright and va read 44-of-50 authorless.
            for _sfx in ("JR.", "SR.", "III", "II", "IV", "JR", "SR"):
                if after.upper().startswith(_sfx) and (
                        len(after) == len(_sfx)
                        or not after[len(_sfx)].isalnum()):
                    name = f"{name}, {after[:len(_sfx)]}"
                    after = after[len(_sfx):].lstrip(" ,")
                    break
            low = after.lower()
            if _ANNOUNCED_WRITING.match(low):
                return None
            # A DATE ROW fused onto the byline ('JUSTICE MUNDY DECIDED:
            # MAY 19, 2026' — pa's two-column byline row) ends the byline
            # at the name; the date is criteria, not authorship.
            if low.startswith(("decided:", "filed:", "argued:",
                               "decided ", "filed ")):
                return Byline(name, title.title(), None,
                              _tail_index(text, title, consumed))
            # The kind clause may carry a modifier ('specially concurring.',
            # 'concurring in part and dissenting in part.') — a SHORT tail
            # containing the participle is the kind; a long prose tail is not,
            # except the 'with whom …' form, which lists joiners at any
            # length ('with whom JUSTICE THOMAS joins, dissenting from the
            # denial of certiorari'). 'Justice Rice dissents.' is an
            # announcement and 'X joins in the dissenting Opinion of Y' a
            # JOINDER — neither is a byline.
            # 'Justice Robinson, for the Court.' (ri) / 'JUSTICE HAGEN,
            # opinion of the Court:' (utah) / 'JUSTICE KING, Opinion of the
            # Court:' (ariz) — majority markers.
            for mk in ("for the court", "opinion of the court"):
                if not low.startswith(mk):
                    continue
                tail = after[len(mk):]
                # The marker must close on its own terminal — the opinion's
                # first sentence may follow INLINE ('Chief Justice Suttell,
                # for the Court.  The defendant…' — ri); bare prose
                # ('for the court to decide') is not a marker.
                if tail and tail[:1] not in ".:":
                    continue
                end = (_tail_index(text, title, consumed)
                       + len(mk) + (1 if tail else 0))
                return Byline(name, title.title(), None, end)
            kind = None
            # The passive 'joined by' lists joiners exactly like 'with whom'
            # ('JUSTICE LEHRMANN, joined by Justice Bland…, dissenting…').
            with_whom = (low.startswith("with whom")
                         or low.startswith("joined by"))
            if ((len(after) < 70 or with_whom)
                    and ("concurring" in low or "dissenting" in low)
                    and not (("join" in low) and not with_whom)):
                kind = "concurring" if "concurring" in low else "dissenting"
            if kind:
                stop = after.find(".")
                if stop == -1:
                    # No terminal period: the WHOLE text is the byline (an
                    # unpunctuated order-list notation, or a wrap the caller
                    # is still assembling) — never cut the author at the
                    # kind clause.
                    return Byline(name, title.title(),
                                  after.strip(" .,"), len(text))
                end = _tail_index(text, title, consumed) + stop + 1
                return Byline(name, title.title(),
                              after[:stop].strip(" .,"), end)
            verb = low.split()[0] if low.split() else ""
            if saw_colon:
                return Byline(name, title.title(), None, text.find(":") + 1)
            if verb in _DELIVER_VERBS or not after:
                return Byline(name, title.title(), None, len(text))
            return None
        return None


# A one-line conformed signature: a NAME, a comma, and a judicial title —
# the whole row and nothing else.
_ONE_LINE_SIG = re.compile(
    # The prefix is part of the NAME — captured outside the group it made
    # 'McCONNELL, P. J.' come back as 'CONNELL'.
    r"^(?P<name>(?:Mc|Mac|St\.\s?)?[A-Z][A-Za-z'’\-]+"
    r"(?:\s+[A-Z][A-Za-z'’\-.]+){0,3}),\s*"
    r"(?P<title>(?:Chief\s+|Presiding\s+|Associate\s+|Acting\s+"
    r"|Senior\s+|Retired\s+)?"
    # …and the period belongs to the ABBREVIATION: 'P. J.' is not 'P. J'.
    r"(?:C\.\s?J\.|P\.\s?J\.|V\.\s?C\.|J\.|Justice|Judge|Chancellor"
    r"|Magistrate(?:\s+in\s+Chancery)?|Commissioner|Master)\.?)$")
_ATTEST_ROW = re.compile(r"^(?:WE|I)\s+(?:CONCUR|DISSENT)", re.I)


def conformed_signature_author(lines_text: list[str]) -> str | None:
    """'/s/ Name' plus its adjacent judicial title line — the author of an
    unsigned order. Also ca10's ORDER AND JUDGMENT signer: 'Entered for the
    Court' / 'Veronica S. Rossman' / 'Circuit Judge' (never the clerk's
    'FOR THE COURT:' attestation — the title line must be judicial)."""
    titles = ("justice", "judge", "chancellor", "magistrate", "commissioner")
    for i, t in enumerate(lines_text):
        t = t.strip()
        # 's/Name' is the same conformed signature as '/s/ Name' — uscfc's
        # special masters sign without the leading slash.
        _pfx = next((p for p in ("/s/", "/s ", "s/")
                     if t.lower().startswith(p)), None)
        if _pfx is None:
            continue
        name = t[len(_pfx):].strip()
        if i + 1 < len(lines_text):
            nxt = lines_text[i + 1].strip()
            if any(w in nxt.lower() for w in titles):
                # the NAME is on the '/s/' line and the title beneath it —
                # keep both ('/s Abigail M. LeGrow' + 'Justice')
                if not name:
                    return nxt
                return f"{name}, {nxt}"
        return name
    # 'JEFFREY W. BATES, J. – OPINION AUTHOR' — moctapp's Southern District
    # names the author in its trailing vote block.
    for t in lines_text:
        mm = re.match(r"^\s*(.+?,\s*(?:C\.? ?J\.|P\.? ?J\.|J\.))\s*[–—-]\s*"
                      r"OPINION AUTHOR\s*$", t, re.IGNORECASE)
        if mm:
            return mm.group(1).strip()
    for i, t in enumerate(lines_text):
        if " ".join(t.split()).lower().rstrip(",:") != "entered for the court":
            continue
        follow = [x.strip() for x in lines_text[i + 1:i + 4] if x.strip()]
        if not follow:
            continue
        name = follow[0]
        if name.lower().startswith(("/s/", "/s ")):
            name = name[3:].strip()
        title = follow[1] if len(follow) > 1 else ""
        if any(w in title.lower() for w in titles):
            return f"{name}, {title}"
        if any(w in name.lower() for w in titles):
            return name
    # An OPINION LETTER is signed at the end by the official who issued it,
    # with no byline anywhere above: mdag/minnag close on 'Anthony G. Brown'
    # / 'Attorney General of Maryland'. The pair is a name line followed by
    # a line naming the OFFICE — read only from the tail, where a signature
    # lives, so a counsel roster's 'Attorney General' cannot pose as one.
    # …and the same shape signs a judicial opinion that carries no byline:
    # vtsuperct closes 'Tomasi' / 'Superior Court Judge'.
    _OFFICES = ("attorney general", "solicitor general", "chief counsel",
                "county attorney", "corporation counsel",
                "superior court judge", "special master", "presiding judge",
                "administrative law judge", "hearing officer")
    _tail = [x.strip() for x in lines_text[-14:] if x.strip()]
    for i, t in enumerate(_tail[:-1]):
        nxt = _tail[i + 1].lower()
        if not any(o in nxt for o in _OFFICES):
            continue
        # the line above must read as a personal NAME, not more prose
        if 2 <= len(t.split()) <= 5 and t[:1].isupper() and not t.endswith(
                (".", ",", ";", ":")):
            return f"{t}, {_tail[i + 1]}"
    # …AND THE SIGNATURE MAY BE THE NAME AND THE TITLE ON ONE LINE, with no
    # '/s/' above it and no office beneath it (queue item 52, diagnosed by
    # the scctapp port). Two courts sign only this way:
    #
    #     McCONNELL, P. J.            calctapp, flush right over 'WE CONCUR:'
    #     Sheldon K. Rennie, Judge    delsuperct, under a graphic signature
    #
    # 10 of delsuperct's 42 records and both papers of calctapp's stapled
    # bates came back with an unauthored writing for want of it.
    #
    # LAST RESORT, and it stops at the attestation: everything below 'WE
    # CONCUR:' is the judges who JOINED, and each of those rows has this
    # same shape ('O’ROURKE, J.', 'DO, J.'). The author signs above it.
    for t in _tail:
        if _ATTEST_ROW.match(t):
            break
        hit = _ONE_LINE_SIG.match(t)
        if hit:
            return f"{hit.group('name')}, {hit.group('title')}"
    return None


def normalize_opinion_type(kind: str | None) -> str:
    if kind is None:
        return "majority"
    k = kind.lower()
    if "concur" in k and "part" in k and "dissent" in k:
        return "concurring-in-part-and-dissenting-in-part"
    if "dissent" in k:
        return "dissent"
    if "concur" in k and "result" in k:
        return "concurrence-in-result"
    if "concur" in k:
        return "concurrence"
    if "per curiam" in k:
        return "per-curiam"
    # A JOINER LIST is not a kind: 'Duncan, Circuit Judge, joined by Elrod,
    # Chief Judge, …, Circuit Judges:' names an en banc MAJORITY and its
    # joiners. Without a concur/dissent participle the writing is the
    # court's opinion, not a separate kind.
    if k.lstrip().startswith(("joined by", "with whom", "in which")):
        return "majority"
    return k.replace(" ", "-")
