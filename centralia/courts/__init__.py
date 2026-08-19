"""The court registry: court_id -> CourtProfile. Data only.

Unknown courts get a generic profile — the engine is measured-first, so a
generic profile is a real attempt, not a stub.
"""

from __future__ import annotations

from dataclasses import replace

from ..profile import CourtProfile
from ..resolve.bylines import DEFAULT_ABBREV, BylineGrammar
from ..resolve.footnotes import FootnoteConfig

PROFILES: dict[str, CourtProfile] = {}


def register(profile: CourtProfile) -> CourtProfile:
    if profile.court_id in PROFILES:
        raise ValueError(f"duplicate profile {profile.court_id!r}")
    PROFILES[profile.court_id] = profile
    return profile


def get_profile(court_id: str) -> CourtProfile:
    if court_id in PROFILES:
        return PROFILES[court_id]
    return CourtProfile(court_id=court_id, court_label=court_id)


# ---- pilot profiles ---------------------------------------------------------

register(CourtProfile(
    "mont", "Supreme Court of Montana",
    byline=BylineGrammar(style="reversed",
                         rev_titles=("Justice", "Chief Justice"),
                         allow_titlecase_name=True),
    rollout="migrated",
))

# ala's profile lives in courts/ala.py, beside its headmatter reader.

# ---- Phase 7b: state courts (grammar facts mined from the old repo) -------

register(CourtProfile(
    "alaska", "Supreme Court of the State of Alaska",
    byline=BylineGrammar(style="prose", titles=("Justice",)),
))
register(CourtProfile(
    "alaskactapp", "Court of Appeals of the State of Alaska",
    byline=BylineGrammar(style="prose", titles=("Judge",)),
))
# ariz sets a title-led CAPS byline ('JUSTICE KING, Opinion of the Court:')
# and abbreviated separate-writing bylines ('BOLICK, J., dissenting.').
# BOTH forms are declared: `reversed` alone saw only the lead opinion, so
# every separate writing in the corpus — 'TIMMER, C.J., Dissenting.',
# 'LOPEZ, V. C. J., joined by …' — was invisible (ported 2026-08-18).
register(CourtProfile(
    "ariz", "Supreme Court of the State of Arizona",
    byline=BylineGrammar(style="abbrev", also_reversed=True,
                         abbrev_titles=(("V.C.J.", "Vice Chief Justice"),
                                        ("V. C. J.", "Vice Chief Justice"),
                                        ("C.J.", "Chief Justice"),
                                        ("C. J.", "Chief Justice"),
                                        ("J.", "Justice")),
                         rev_titles=("VICE CHIEF JUSTICE", "CHIEF JUSTICE",
                                     "JUSTICE")),
))
register(CourtProfile(
    "arizctapp", "Arizona Court of Appeals",
    # 'Vice Chief Judge' is a real bench title here and its absence left
    # three lead opinions unbylined ('E P P I C H, Vice Chief Judge:').
    byline=BylineGrammar(style="prose",
                         titles=("Judge", "Presiding Judge", "Chief Judge",
                                 "Vice Chief Judge")),
))
register(CourtProfile(
    "ark", "Supreme Court of Arkansas",
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice",
                                 "Associate Justice", "Special Justice")),
))
register(CourtProfile(
    "arkctapp", "Arkansas Court of Appeals",
    byline=BylineGrammar(style="prose", titles=("Judge", "Chief Judge")),
))
register(CourtProfile(
    "dc", "District of Columbia Court of Appeals",
    byline=BylineGrammar(style="prose",
                         titles=("Associate Judge", "Senior Judge",
                                 "Chief Judge", "Judge")),
))
register(CourtProfile(
    "fladistctapp", "Florida District Court of Appeal",
    byline=BylineGrammar(style="abbrev"),
))
register(CourtProfile(
    "ga", "Supreme Court of Georgia",
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice",
                                 "Presiding Justice")),
))
register(CourtProfile(
    "gactapp", "Court of Appeals of Georgia",
    byline=BylineGrammar(style="prose",
                         titles=("Judge", "Presiding Judge", "Chief Judge")),
))

# Alabama's intermediate courts share the Supreme Court's template; only
# the bench title differs ('WELCH, Judge.' / 'BOWDEN, Presiding Judge.').

_CIRCUIT_GRAMMAR = BylineGrammar(
    style="prose",
    # 'J.' covers the circuits' short form on separate writings
    # ('R. NELSON, J., concurring:' — ca9 sets the full title only on the
    # majority).
    titles=("Circuit Judge", "Judge", "District Judge", "Justice",
            "Chief Judge", "Circuit Justice", "J."))

for _cid, _label in (
):
    register(CourtProfile(_cid, _label, byline=_CIRCUIT_GRAMMAR))

register(CourtProfile(
    "akd", "United States District Court for the District of Alaska",
    byline=BylineGrammar(style="none"),   # unsigned orders; /s/ signature
))

register(CourtProfile(
    "conn", "Supreme Court of Connecticut",
    byline=BylineGrammar(style="abbrev"),
    footnotes=FootnoteConfig(reject_underlines=False),
))

# Same Law Journal slip format as the Supreme Court.
register(CourtProfile(
    "connappct", "Connecticut Appellate Court",
    byline=BylineGrammar(style="abbrev"),
    footnotes=FootnoteConfig(reject_underlines=False),
))

_TENN_GRAMMAR = BylineGrammar(
    style="abbrev", accept_delivered=True,
    # A Special Workers' Compensation Appeals Panel is convened out of
    # SENIOR judges, and the byline says so BEFORE the abbreviated title:
    # 'W. MARK WARD, SR. J., delivered the opinion of the court…'.
    # `title_suffixes` strips only what FOLLOWS the title, so without this
    # the panel slips assemble with no author at all.
    abbrev_titles=(("SR. J.", "Senior Judge"),
                   ("SR.J.", "Senior Judge")) + DEFAULT_ABBREV,
    title_suffixes=("W.S.", "M.S.", "E.S."))

register(CourtProfile("tenn", "Supreme Court of Tennessee",
                      byline=_TENN_GRAMMAR))
# The intermediates print the same 'delivered' announcement byline.
register(CourtProfile("tennctapp", "Tennessee Court of Appeals",
                      byline=_TENN_GRAMMAR))
register(CourtProfile("tenncrimapp", "Tennessee Court of Criminal Appeals",
                      byline=_TENN_GRAMMAR))

register(CourtProfile(
    "utah", "Supreme Court of Utah",
    # Abbrev separate-writing bylines plus the reversed majority form
    # ('JUSTICE HAGEN, opinion of the Court:').
    byline=BylineGrammar(style="abbrev", also_reversed=True,
                         rev_titles=("ASSOCIATE CHIEF JUSTICE",
                                     "CHIEF JUSTICE", "JUSTICE")),
    # Utah repeats a star label across its front-matter notes; consecutive
    # duplicates are one label.
    footnotes=FootnoteConfig(dedupe_labels=True),
))

register(CourtProfile(
    "utahctapp", "Utah Court of Appeals",
    byline=BylineGrammar(style="abbrev", also_reversed=True,
                         rev_titles=("PRESIDING JUDGE", "JUDGE")),
))

register(CourtProfile(
    "coloctapp", "Colorado Court of Appeals",
    # The caption announces the author ('Opinion by JUDGE BROWN').
    byline=BylineGrammar(style="prose", opinion_by_headings=True,
                         titles=("Judge", "Chief Judge", "JUDGE")),
))


# ---- Phase 7b: remaining states (grammar facts mined from the old repo) ----

_JUDGE_PROSE = BylineGrammar(
    style="prose", titles=("Judge", "Chief Judge", "Presiding Judge",
                           "Senior Judge", "J."))

register(CourtProfile(
    "del", "Supreme Court of the State of Delaware",
    byline=BylineGrammar(style="prose",
                         titles=("Chief Justice", "Justice"))))
register(CourtProfile(
    "haw", "Supreme Court of the State of Hawaiʻi",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile(
    "hawapp", "Intermediate Court of Appeals of Hawaiʻi",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile(
    "idaho", "Supreme Court of the State of Idaho",
    # The corpus carries Court of Appeals papers ('LORELLO, Judge') and
    # signs every separate writing with the abbreviated title ('ZAHN, J.,
    # dissenting.'); idahoctapp already ships this grammar.
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice",
                                 "Pro Tem Justice", "Justice Pro Tem",
                                 "Judge", "Chief Judge", "Judge Pro Tem",
                                 "J."))))
register(CourtProfile(
    "idahoctapp", "Idaho Court of Appeals",
    byline=BylineGrammar(style="prose",
                         titles=("Judge", "Chief Judge", "Judge Pro Tempore",
                                 "Judge Pro Tem", "J."))))
# ill: profile lives in `courts/ill.py` beside its reader — it declares
# strip_para_marker (ill NUMBERS its separate-writing bylines) and ALL-CAPS
# rev_titles, without which all 10 separate writings in the corpus are lost.
register(CourtProfile(
    "illappct", "Illinois Appellate Court",
    byline=BylineGrammar(style="reversed", allow_titlecase_name=True,
                         rev_titles=("JUSTICE", "PRESIDING JUSTICE",
                                     "Justice", "Presiding Justice"))))
register(CourtProfile(
    "ind", "Indiana Supreme Court",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Justice", "Chief Justice"))))
register(CourtProfile(
    "indctapp", "Court of Appeals of Indiana",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Judge", "Chief Judge", "Senior Judge"))))
# The BANKRUPTCY APPELLATE PANELS sign with a titlecase surname and the
# panel's full designation ('Bailey, U.S. Bankruptcy Appellate Panel
# Judge.'). Undeclared, every one of their opinions read as headmatter.
# bap8 declares its own (a typed-ladder cover) in centralia/courts/bap8.py,
# bap10 and bap1 their own (bap1 a centred ladder) in their own files,
# bap9 its own (a shelved cover) in centralia/courts/bap9.py.
# bap6 declares its own (the Sixth Circuit's rail-and-fence slip) in
# centralia/courts/bap6.py.
register(CourtProfile(
    # The tax court signs ABBREV ('WELCH, Special J.'), unlike Indiana's
    # supreme and appellate courts, and seats special/senior judges.
    "indtc", "Indiana Tax Court",
    byline=BylineGrammar(style="abbrev",
                         abbrev_titles=(("Special J.", "Special Judge"),
                                        ("Senior J.", "Senior Judge"),
                                        ("C.J.", "Chief Judge"),
                                        ("J.", "Judge")))))
register(CourtProfile(
    "iowa", "Supreme Court of Iowa",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Justice", "Chief Justice"))))
register(CourtProfile("iowactapp", "Iowa Court of Appeals",
                      byline=_JUDGE_PROSE))
register(CourtProfile("kan", "Supreme Court of the State of Kansas",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile("kanctapp", "Kansas Court of Appeals",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "ky", "Supreme Court of Kentucky",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile(
    "kyctapp", "Kentucky Court of Appeals",
    byline=BylineGrammar(style="prose",
                         titles=("JUDGE", "CHIEF JUDGE", "SENIOR JUDGE",
                                 "Judge", "Chief Judge"))))
register(CourtProfile(
    "la", "Supreme Court of Louisiana",
    # 'WEIMER, Chief Justice*' on the opinion; 'GUIDRY, J.' on separates.
    byline=BylineGrammar(style="prose",
                         titles=("Chief Justice", "Justice",
                                 "Justice ad hoc", "J."))))
register(CourtProfile("lactapp", "Louisiana Court of Appeal",
                      byline=_JUDGE_PROSE))
# mass: profile lives in `courts/mass.py` beside its reader.
register(CourtProfile("massappct", "Massachusetts Appeals Court",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "md", "Supreme Court of Maryland",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile(
    "mdctspecapp", "Appellate Court of Maryland",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile("me", "Maine Supreme Judicial Court",
                      byline=BylineGrammar(style="abbrev")))
# mich: profile lives in `courts/mich.py` beside its reader.
register(CourtProfile("michctapp", "Michigan Court of Appeals",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "minn", "Supreme Court of Minnesota",
    byline=BylineGrammar(style="prose", titles=("Justice", "Chief Justice"))))
register(CourtProfile("minnctapp", "Minnesota Court of Appeals",
                      byline=_JUDGE_PROSE))
register(CourtProfile(
    "miss", "Supreme Court of Mississippi",
    byline=BylineGrammar(style="prose",
                         titles=("JUSTICE", "PRESIDING JUSTICE",
                                 "CHIEF JUSTICE", "Justice"))))
register(CourtProfile(
    "missctapp", "Mississippi Court of Appeals",
    byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "mo", "Supreme Court of Missouri",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Judge", "Chief Justice", "Special Judge",
                                 "JUDGE"))))
register(CourtProfile(
    "moctapp", "Missouri Court of Appeals",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Judge", "Chief Judge", "Special Judge",
                                 "Presiding Judge", "JUDGE", "J.",
                                 "C.J.", "P.J."))))
register(CourtProfile("ncctapp", "North Carolina Court of Appeals",
                      byline=_JUDGE_PROSE))
register(CourtProfile(
    "nd", "North Dakota Supreme Court",
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Justice", "Chief Justice",
                                 "District Judge", "Surrogate Judge"))))
register(CourtProfile(
    "neb", "Nebraska Supreme Court",
    byline=BylineGrammar(style="abbrev", allow_titlecase_name=True)))
register(CourtProfile(
    "nebctapp", "Nebraska Court of Appeals",
    # 'Bishop, Judge.' — spelled title on a titlecase surname.
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         titles=("Judge", "Chief Judge", "District Judge",
                                 "J."))))
register(CourtProfile(
    "nev", "Supreme Court of the State of Nevada",
    byline=BylineGrammar(style="abbrev", strip_by_the_court=True)))
register(CourtProfile(
    "nevapp", "Nevada Court of Appeals",
    byline=BylineGrammar(style="abbrev", strip_by_the_court=True)))
register(CourtProfile("nh", "Supreme Court of New Hampshire",
                      byline=BylineGrammar(style="abbrev")))
# nj: profile lives in `courts/nj.py` beside its reader.
register(CourtProfile(
    "njsuperctappdiv", "New Jersey Superior Court, Appellate Division",
    byline=BylineGrammar(
        style="abbrev",
        abbrev_titles=(("C.J.A.D.", "Chief Judge, Appellate Division"),
                       ("J.A.D.", "Judge, Appellate Division"),
                       *DEFAULT_ABBREV))))
register(CourtProfile(
    "nm", "Supreme Court of the State of New Mexico",
    byline=BylineGrammar(style="prose", titles=("Justice", "Chief Justice"))))
register(CourtProfile("nmctapp", "New Mexico Court of Appeals",
                      byline=_JUDGE_PROSE))
register(CourtProfile("nysupct", "Supreme Court of the State of New York",
                      byline=BylineGrammar(style="none")))
# ohio: profile lives in `courts/ohio.py` beside its reader.
register(CourtProfile("ohioctapp", "Ohio Court of Appeals",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile("or", "Supreme Court of the State of Oregon",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile("orctapp", "Oregon Court of Appeals",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "pa", "Supreme Court of Pennsylvania",
    byline=BylineGrammar(style="reversed",
                         rev_titles=("JUSTICE", "CHIEF JUSTICE"))))
register(CourtProfile(
    "pasuperct", "Pennsylvania Superior Court",
    # 'OPINION BY BENDER, P.J.E.:' / 'MEMORANDUM BY BENDER, P.J.E.:'
    byline=BylineGrammar(
        style="prose", opinion_by_headings=True,
        titles=("Judge", "Chief Judge", "Presiding Judge", "Senior Judge",
                "J."),
        abbrev_titles=(("P.J.E.", "President Judge Emeritus"),
                       *DEFAULT_ABBREV))))
register(CourtProfile(
    "pacommwct", "Commonwealth Court of Pennsylvania",
    byline=BylineGrammar(style="abbrev", opinion_by_headings=True)))
register(CourtProfile(
    "ri", "Supreme Court of Rhode Island",
    byline=BylineGrammar(style="reversed", allow_titlecase_name=True,
                         rev_titles=("Justice", "Chief Justice"))))
register(CourtProfile(
    "sc", "The Supreme Court of South Carolina",
    byline=BylineGrammar(style="reversed",
                         rev_titles=("JUSTICE", "CHIEF JUSTICE",
                                     "ACTING JUSTICE"))))
register(CourtProfile("scctapp", "South Carolina Court of Appeals",
                      byline=_JUDGE_PROSE))
register(CourtProfile(
    "sd", "Supreme Court of South Dakota",
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice",
                                 "Retired Justice"))))
# tex: profile lives in `courts/tex.py` beside its reader.
register(CourtProfile("texapp", "Texas Court of Appeals",
                      byline=BylineGrammar(style="none")))
register(CourtProfile(
    "texcrimapp", "Texas Court of Criminal Appeals",
    byline=BylineGrammar(style="abbrev", accept_delivered=True)))
# va: profile moved into `courts/va.py`, beside the reader that needs its
# measured `para_indent_min`. The grammar was already correct — Virginia
# does not SIGN its majorities, it ANNOUNCES the author in the caption.
register(CourtProfile(
    "vactapp", "Court of Appeals of Virginia",
    byline=BylineGrammar(style="prose", opinion_by_headings=True,
                         titles=("Judge", "Chief Judge", "Senior Judge"))))
register(CourtProfile(
    "vt", "Supreme Court of Vermont",
    byline=BylineGrammar(style="abbrev", strip_para_marker=True)))
register(CourtProfile(
    "wash", "Washington Supreme Court",
    # Washington seats justices PRO TEMPORE and signs them with the full
    # designation ('MADSEN, J.P.T.* (dissenting)—'). Under the default list
    # the bare 'J.' matched first, the kind clause was never reached, and
    # every J.P.T. separate writing typed as a MAJORITY with 'P.T.*' leading
    # its first sentence. Both spellings are declared: the parser spreads
    # tight punctuation, so 'J.P.T.' reaches the match as 'J. P. T.'.
    byline=BylineGrammar(style="abbrev", abbrev_titles=(
        ("C.J.P.T.", "Chief Justice Pro Tempore"),
        ("C. J. P. T.", "Chief Justice Pro Tempore"),
        ("J.P.T.", "Justice Pro Tempore"),
        ("J. P. T.", "Justice Pro Tempore"),
    ) + DEFAULT_ABBREV)))
register(CourtProfile("washctapp", "Washington Court of Appeals",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "wva", "Supreme Court of Appeals of West Virginia",
    # THREE signing forms: 'JUSTICE WOOTON delivered the Opinion of the
    # Court.', 'TRUMP, Justice:' and 'Justice Wooton, dissenting:'. The
    # third is admitted only with a kind clause — see titlecase_kind_only.
    byline=BylineGrammar(style="prose", also_reversed=True,
                         titlecase_kind_only=True,
                         titles=("Justice", "Chief Justice", "Judge",
                                 "Chief Judge"),
                         rev_titles=("CHIEF JUSTICE", "JUSTICE",
                                     "CHIEF JUDGE", "JUDGE",
                                     "Chief Justice", "Justice",
                                     "Chief Judge", "Judge"))))
register(CourtProfile(
    "wvactapp", "Intermediate Court of Appeals of West Virginia",
    byline=BylineGrammar(style="prose", also_reversed=True,
                         rev_titles=("CHIEF JUDGE", "JUDGE"),
                         titles=("Judge", "Chief Judge"))))
register(CourtProfile(
    "wis", "Supreme Court of Wisconsin",
    byline=BylineGrammar(style="abbrev", strip_para_marker=True)))
register(CourtProfile(
    "wisctapp", "Wisconsin Court of Appeals",
    byline=BylineGrammar(style="abbrev", strip_para_marker=True)))
register(CourtProfile(
    "wyo", "The Supreme Court, State of Wyoming",
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice",
                                 "District Judge"))))
register(CourtProfile("guam", "Supreme Court of Guam",
                      byline=BylineGrammar(style="abbrev")))
register(CourtProfile(
    "nmariana",
    "Supreme Court of the Commonwealth of the Northern Mariana Islands",
    byline=BylineGrammar(style="abbrev", allow_titlecase_name=True)))
register(CourtProfile(
    "prsupreme", "Supreme Court of Puerto Rico",
    # 'Opinión del Tribunal emitida por la Jueza Asociada Rivera García'
    byline=BylineGrammar(style="none", opinion_by_headings=True)))
register(CourtProfile("prapp", "Puerto Rico Court of Appeals",
                      byline=BylineGrammar(style="none")))
register(CourtProfile(
    "virginislands", "Supreme Court of the Virgin Islands",
    # The opinion of the Court is signed in PROSE ('HODGE, Chief Justice.';
    # 'SWAN, Associate Justice'); separate writings use the ABBREV form
    # ('HODGE, C.J., with whom CABRET, J. joins, concurring in part.').
    # Declared abbrev-only, 30 of 32 majorities were credited to the clerk.
    byline=BylineGrammar(style="prose", titles=("Justice", "Judge"),
                         also_abbrev=True)))

# ---- Phase 8 hard tail ------------------------------------------------------

# cal's profile moved into `courts/cal.py` with its reader: the page-1
# AUTHORSHIP SUMMARY that this grammar was written to parse is headmatter,
# not a byline, and reading it as one opened a phantom writing per sentence.
register(CourtProfile(
    "calctapp", "Court of Appeal of California",
    # Signature at the END ('CHUNG, J.' + 'WE CONCUR:' roster).
    byline=BylineGrammar(style="abbrev")))


# --------------------------------------------------------------------------
# FRONT MATTER — what each court prints BEFORE the opinion, declared as a
# court FACT. A court absent from this table prints neither a syllabus nor a
# staff summary, so front prose there is the opinion body: the engine must
# never invent a section for it.
#
#   'syllabus' — a court-published syllabus, part of the official report
#                (scotus's Reporter syllabus, conn's, nj's clerk syllabus,
#                mich's Reporter syllabus, the state supremes' headnote
#                syllabi).
#   'summary'  — a staff summary that is expressly NOT part of the opinion
#                (ca9's 'SUMMARY**').
# --------------------------------------------------------------------------
_FRONT_MATTER = {
    "conn": ("syllabus",), "connappct": ("syllabus",),
    "nj": ("syllabus",),
    "mich": ("syllabus",), "michctapp": ("syllabus",),
    "kan": ("syllabus",), "kanctapp": ("syllabus",),
    "neb": ("syllabus",), "nebctapp": ("syllabus",),
    "ohio": ("syllabus",), "ohioctapp": ("syllabus",),
    "mont": ("syllabus",),
    # ca9 declares its own ('summary') in centralia/courts/ca9.py, which is
    # imported after this table is applied.
}

for _cid, _fm in _FRONT_MATTER.items():
    _p = PROFILES.get(_cid)
    if _p is not None:
        PROFILES[_cid] = replace(_p, front_matter=_fm)

# --------------------------------------------------------------------------
# COURT FILES — a court whose own typesetting decides something owns a module
# of its own (profile + deciders, nothing else). Imported last, so `register`
# and this table exist; flat, so no court file can reach another.
# --------------------------------------------------------------------------
from . import ca1                                             # noqa: E402,F401
from . import ca11                                            # noqa: E402,F401
from . import ca2                                             # noqa: E402,F401
from . import ca3                                             # noqa: E402,F401
from . import ca4                                             # noqa: E402,F401
from . import ca5                                             # noqa: E402,F401
from . import ca6                                             # noqa: E402,F401
from . import ca7                                             # noqa: E402,F401
from . import ca8                                             # noqa: E402,F401
from . import cadc                                            # noqa: E402,F401
from . import ca9                                             # noqa: E402,F401
from . import ca10                                            # noqa: E402,F401
from . import cafc                                            # noqa: E402,F401
from . import scotus                                          # noqa: E402,F401
from . import bap8                                            # noqa: E402,F401
from . import fla                                             # noqa: E402,F401
from . import bap10                                           # noqa: E402,F401
from . import bap6                                            # noqa: E402,F401
from . import bap1                                            # noqa: E402,F401
from . import bap9                                            # noqa: E402,F401
from . import ala                                             # noqa: E402,F401
from . import ark                                             # noqa: E402,F401
from . import ariz                                            # noqa: E402,F401
from . import alaska                                          # noqa: E402,F401
from . import cal                                             # noqa: E402,F401
from . import alacivapp                                       # noqa: E402,F401
from . import alacrimapp                                      # noqa: E402,F401
from . import arkctapp                                        # noqa: E402,F401
from . import arizctapp                                       # noqa: E402,F401
from . import mo                                              # noqa: E402,F401
from . import virginislands                                   # noqa: E402,F401
from . import alaskactapp                                     # noqa: E402,F401
from . import idaho                                           # noqa: E402,F401
from . import wva                                             # noqa: E402,F401
from . import tenn                                            # noqa: E402,F401
from . import wash                                            # noqa: E402,F401
from . import va                                              # noqa: E402,F401
from . import mass                                            # noqa: E402,F401
from . import ga                                            # noqa: E402,F401
from . import tex                                           # noqa: E402,F401
from . import ohio                                            # noqa: E402,F401
from . import ill                                             # noqa: E402,F401
from . import mich                                            # noqa: E402,F401
from . import nj                                              # noqa: E402,F401
from . import nd                                              # noqa: E402,F401
from . import kyed                                            # noqa: E402,F401
from . import massappct                                       # noqa: E402,F401
from . import haw                                           # noqa: E402,F401
from . import iowa                                          # noqa: E402,F401
from . import fladistctapp                                  # noqa: E402,F401
from . import michctapp                                     # noqa: E402,F401
from . import gactapp                                       # noqa: E402,F401
from . import njsuperctappdiv                               # noqa: E402,F401
from . import texcrimapp                                    # noqa: E402,F401
from . import moctapp                                       # noqa: E402,F401
from . import kan                                           # noqa: E402,F401
from . import md                                            # noqa: E402,F401
from . import kanctapp                                      # noqa: E402,F401
from . import nc                                             # noqa: E402,F401
from . import ind                                            # noqa: E402,F401
from . import tennctapp                                      # noqa: E402,F401
from . import coloctapp                                      # noqa: E402,F401
from . import me                                             # noqa: E402,F401
from . import minn                                           # noqa: E402,F401
from . import ky                                             # noqa: E402,F401
from . import miss                                           # noqa: E402,F401
from . import nh                                             # noqa: E402,F401
from . import mont                                           # noqa: E402,F401

from . import conn                                           # noqa: E402,F401

# COURTS WHOSE ID IS A PYTHON KEYWORD. 'del' (Delaware) and 'or' (Oregon)
# have perfectly legal FILENAMES — centralia/courts/del.py, or.py, the same
# convention as every other court — but `from . import del` is a syntax
# error, so they are imported the long way. The court id on the decider is
# what dispatch uses; the module name never mattered to it.
import importlib as _importlib                               # noqa: E402
for _kw in ("del", "or"):
    try:
        _importlib.import_module(f".{_kw}", __name__)
    except ModuleNotFoundError:
        pass
from . import dc                                             # noqa: E402,F401
from . import nev                                            # noqa: E402,F401
from . import la                                             # noqa: E402,F401
from . import neb                                            # noqa: E402,F401
from . import nm                                             # noqa: E402,F401
