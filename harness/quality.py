"""Per-file quality grades from mechanical signals in the rendered HTML.

Reads output/<court>/<stem>.html only — no PDF opens, no pipeline re-runs —
so grading the whole corpus takes seconds. Each file gets a score (0 = no
detected defects) and a letter grade A-F; courts roll up to a mean score,
a grade, and the share of A/B files. Results land in
output/notes/quality.json, which the viewer serves at /api/quality.

Signals (all from the emitted markup, so they track exactly what the
reviewer sees):
  warn        pipeline warning chips
  resid       residual CONTENT lines (unaccounted input — the worst signal)
  no_op       zero rendered opinions (and `o` carries the count itself)
  joins       missing-space word joins in visible text (defendantsDennis)
  hyph        hyphen-join artifacts (pro- posed)
  cid         literal (cid:NN) glyphs
  no_atty     no attorneys section while the text shows counsel cues
  decap       a section whose first text character is lowercase
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import OUTPUT_DIR  # noqa: E402

QUALITY = OUTPUT_DIR / "notes" / "quality.json"

_DETAILS = re.compile(r"<details.*?</details>", re.S)
_TAG = re.compile(r"<[^>]+>")
_WARN = re.compile(r'class="chip warn" title="([^"]*)"')
_RESID = re.compile(r"residual · \d+ · (\d+) CONTENT")
_OPINION = re.compile(r'<div class="opinion">')
# The renderer puts a CLASS on every section (`<section class="sec-opinions">`).
# Matching a bare `<section>` matched 1 file in 9,230, so `names` was empty
# everywhere: `decap` could never fire at all, and `no-attorneys` silently
# lost its section test and rested on the criteria chip alone.
_SECTION = re.compile(
    r'<section(?:\s+class="[^"]*")?><h2>([^<]+)</h2>(.*?)</section>', re.S)
_CHIP = re.compile(r'<span class="chip[^"]*">[^<]*</span>')
_LEGEND = re.compile(r'<div class="hm-legend">.*?</div>', re.S)
_JOIN = re.compile(r"[a-z]{3,}[A-Z][a-z]")
_HYPH = re.compile(r"[a-z]- [a-z]")
_CID = re.compile(r"\(cid:\d+\)")
_COUNSEL = re.compile(
    r"argued the cause|on the briefs?\b|attorneys? for the|counsel for the",
    re.I)

# words that legitimately contain an interior capital after 3+ lowercase
_JOIN_OK = re.compile(
    r"(?:Lexis|West|Penn|Volks|Price|Bancorp|Health|Quick|Ameri|Trans|"
    r"Inter|Metro|Path|Farm|Home|Tech|Master|First|Sun|Bank|Net|Care|"
    r"Point|View|Star|Land|Wood|Ridge|Field|Book|Air|Auto)[A-Z]")

# A camel word standing in a CITATION is a party's name set that way on the
# page, not a missing space: the allowlist above can never keep up with the
# corporate register (CitiMortgage, VeroBlue, TrafficSchool.com, ExecuCorp,
# MusclePharm all read as joins). The context decides instead of the spelling.
# the signal may stand a name-head away from the capital ('FCC v. NextWave'
# reads its capital inside 'Next|Wave'), so both windows allow the head.
_CITE_BEFORE = re.compile(
    r"(?:\bv\.?\s+|\bIn\s+re\s+|\bquoting\s+|\bciting\s+|\bsee\s+)"
    r"[A-Za-z.'&-]{0,20}$", re.I)
_CITE_AFTER = re.compile(
    r"^[\w.'&-]{0,30}?(?:,\s*(?:Inc|LLC|L\.L\.C|LLP|L\.P|N\.A|P\.C|PLLC|"
    r"Ltd|Co|Corp|Ass'?n)\b|\s+(?:Corp|Corporation|Co\.|Ltd|Bank|Ass'?n)\b)")


def _text(html: str) -> str:
    return _TAG.sub(" ", html)


_READER_COURTS: set[str] | None = None


def _court_has_reader(path: Path) -> bool:
    """True when this file's court registers a headmatter reader — those are
    the courts whose headmatter is expected to come back identified."""
    global _READER_COURTS
    if _READER_COURTS is None:
        from centralia.resolve.evidence import _DECIDERS
        import centralia.courts  # noqa: F401  (registers the court files)
        _READER_COURTS = {c for (pt, c) in _DECIDERS if pt == "headmatter.read"}
    return path.parent.name in _READER_COURTS


def score_file(path: Path) -> dict:
    html = path.read_text()
    resid = sum(int(m) for m in _RESID.findall(html))
    warns = _WARN.findall(html)
    kept = _DETAILS.sub("", html)          # visible doc, minus removed boxes
    ops = len(_OPINION.findall(kept))
    text = _text(kept)

    # A joined word that RECURS is a name set that way on the page
    # (ShotSpotter, TitleMax); a real missing-space join doesn't repeat.
    join_words: dict[str, int] = {}
    for jm in _JOIN.finditer(text):
        if _JOIN_OK.search(text[max(0, jm.start() - 8):jm.end()]):
            continue
        # the camel word starts at the interior capital the pattern found
        _cap = jm.start() + jm.group(0).index(
            next(c for c in jm.group(0) if c.isupper()))
        if (_CITE_BEFORE.search(text[max(0, _cap - 16):_cap])
                or _CITE_AFTER.search(text[_cap:_cap + 44])):
            continue
        join_words[jm.group(0)] = join_words.get(jm.group(0), 0) + 1
    joins = sum(n for n in join_words.values() if n < 3)
    hyph = len(_HYPH.findall(text))
    cid = len(_CID.findall(text))

    sections = _SECTION.findall(kept)
    names = {n for n, _ in sections}
    # Counsel need not be lifted into a section of its own: a court that
    # prints its appearances in the headmatter renders them there and states
    # them in the criteria box. What matters is that they were READ, not
    # which container they ended up in.
    _atty_crit = re.search(r'chip kind">attorneys</span>\s*[^<\s]', html)
    no_atty = int("attorneys" not in names and not _atty_crit
                  and len(_COUNSEL.findall(text)) >= 2)
    decap = 0
    for name, body in sections:
        # The headmatter legend is RENDER CHROME, not the document's text —
        # it opens 'read as: …' in lower case, so every court with a reader
        # scored a decap on nearly every file the moment the section regex
        # started matching at all (wva 49/50, A 0.15 -> C 2.11).
        first = _text(_LEGEND.sub("", _CHIP.sub("", body))).strip()[:1]
        if first and first.islower():
            decap += 1

    flags: list[str] = []
    score = 0.0
    if resid:
        score += 5 * resid
        flags.append(f"residual×{resid}")
    if not ops:
        score += 8
        flags.append("no-opinions")
    if warns:
        # A SOURCE complaint (the PDF is a scan) is not a parse defect and
        # must not drag a court's grade down — nothing in this repo can fix
        # it, and 100+ files carrying it drowned out the real work.
        _src = [w for w in warns if "scan with OCR" in w
                or "image-only page" in w]
        _parse = [w for w in warns if w not in _src]
        score += 2 * len(_parse)
        if _parse:
            flags.append("warn:" + ";".join(sorted(set(_parse)))[:60])
        if _src:
            flags.append("scanned-source")
    if joins:
        score += min(5.0, 0.5 * joins)
        flags.append(f"joins×{joins}")
    if hyph:
        score += min(5.0, 0.5 * hyph)
        flags.append(f"hyph×{hyph}")
    if cid:
        score += 3 * cid
        flags.append(f"cid×{cid}")
    if no_atty:
        score += 3
        flags.append("no-attorneys")
    if decap:
        score += 2 * decap
        flags.append(f"decap×{decap}")
    # HM-OVERRUN: a missed opinion start dumps the body into headmatter as
    # line-by-line rows (cadc pre-fix had 1041; ri 400). Letterhead-heavy
    # courts legitimately run ~100-190 (mich two mastheads, nj syllabus
    # apparatus) — only a body-sized dump flags.
    hmrows = len(re.findall(r'class="hmrow', kept))
    if hmrows > 220:
        score += 6
        flags.append(f"hm-overrun×{hmrows}")
    # AUTHORLESS majority: a signed-opinion court whose majority writing
    # carries no byline usually means the start anchored past the byline.
    # …only where the document HAS a byline somewhere. The flag catches a
    # start anchored PAST the byline; a court that signs nothing (ca2's
    # summary orders, per curiam dispositions) has no byline to anchor past,
    # and an unsigned writing there is what the page prints.
    _any_byline = 'class="byline"' in kept
    for opm in re.finditer(r'<div class="opinion"><span class="chip">'
                           r'(majority|opinion)</span>(.{0,400})', kept, re.S):
        if _any_byline and 'class="byline"' not in opm.group(2):
            score += 2
            flags.append("authorless")
            break
    # --- review-taxonomy detectors (the 2026-08-17 live-review classes) ---
    # FOLIO LEAK: a bare page number rendered as a body paragraph (ca3).
    fol = len(re.findall(r"<p[^>]*>\s*\d{1,3}\s*</p>", kept))
    if fol:
        score += min(4, fol)
        flags.append(f"folio-leak×{fol}")
    # COUNSEL IN BODY: an appearance block left inside a writing (ca3) —
    # short paragraphs only, prose mentions don't count.
    # …outside the ENDMATTER, where a trailing roster legitimately lives.
    _body_only = re.sub(r'<section class="sec-endmatter".*?</section>', "",
                        kept, flags=re.S)
    cib = sum(1 for pm2 in re.finditer(r"<p[^>]*>([^<]{0,160})</p>", _body_only)
              if any(cu in pm2.group(1).lower() for cu in
                     ("counsel for appell", "counsel for the appell",
                      "[argued]", "on the brief)", "on the briefs)")))
    if cib:
        score += 2
        flags.append(f"counsel-in-body×{cib}")
    # NAKED RAIL: caption rail glyphs rendered as their own rows (del pre-
    # fix); SPLIT LABEL: a date/docket label row with no value (me/nj).
    nr = len(re.findall(r'<div class="hmrow[^>]*>\s*[:§]\s*</div>', kept))
    if nr >= 3:
        score += 3
        flags.append(f"naked-rail×{nr}")
    sl = len(re.findall(
        r'<div class="hmrow[^>]*>\s*(?:Decided|Argued|Submitted|Filed|'
        r"Docket|Decision)\s*:?\s*</div>", kept))
    if sl:
        score += sl
        flags.append(f"split-label×{sl}")
    # HEADMATTER COVERAGE: how much of the block a court reader actually
    # claimed. An untagged row is one nothing identified — the block still
    # renders, but nobody read it, and that is where the parsing work is.
    # Reported only for courts that HAVE a reader (any tagged row at all),
    # so the 200-odd courts without one are not flagged for lacking one.
    # Keyed on the COURT having a reader, not on this file having tags:
    # gating on 'any tagged row' exempted the worst records — the ones a
    # reader failed on entirely — and they graded A while a human marked
    # them failing. Coverage tracks the human verdict closely (files marked
    # bad leave ~62% of the block unread, files marked good ~10%), so it is
    # weighted to matter.
    _hm_rows = re.findall(r'<div class="hmrow[^>]*>', kept)
    if _hm_rows and len(_hm_rows) >= 6 and _court_has_reader(path):
        _hm_tagged = [r for r in _hm_rows if "data-role=" in r]
        _cov = len(_hm_tagged) / len(_hm_rows)
        if _cov < 0.6:
            score += 3 if _cov < 0.2 else 2
            flags.append(f"hm-unread×{len(_hm_rows) - len(_hm_tagged)}")
    # CRITERIA sanity (the criteria box lives in a details block — read
    # the RAW html): a docket that is a term/date/J-number; parties
    # carrying apparatus.
    dk = re.search(r'chip kind">docket</span>([^<]*)', html)
    if dk and re.search(r"\bterm\b|\bfiled\b|^J-", dk.group(1).strip(),
                        re.IGNORECASE):
        score += 2
        flags.append("docket-suspect")
    pr = re.search(r'chip kind">parties</span>([^<]*)', html)
    if pr and re.search(r"Citation:|Issued|Docket|Argued|, for the",
                        pr.group(1)):
        score += 2
        flags.append("parties-noise")
    # HOW MANY WRITINGS THE FILE HAS, carried beside the grade because it is
    # the first thing a reviewer wants to know about a rendering and the
    # grade cannot say it: 0 is a document whose opinion was lost, and 2+ is
    # either a real separate writing or a phantom one made of a headmatter
    # row nobody claimed. Cheap — `ops` is already counted for `no-opinions`.
    return {"s": round(score, 1), "g": _grade(score), "f": flags, "o": ops}


def _grade(score: float) -> str:
    if score == 0:
        return "A"
    if score <= 2:
        return "B"
    if score <= 6:
        return "C"
    if score <= 12:
        return "D"
    return "F"


def _court_grade(mean: float) -> str:
    if mean < 0.5:
        return "A"
    if mean < 2:
        return "B"
    if mean < 5:
        return "C"
    if mean < 10:
        return "D"
    return "F"


_OPCHIP = re.compile(r'<div class="opinion"><span class="chip">'
                     r'(majority|opinion)</span>(.{0,400})', re.S)


def signing_rate(path: Path) -> tuple[int, int]:
    """(majority writings, how many carry a byline) for one file.

    AUTHORLESS IS NOT A DEFECT BY ITSELF — the user's point, 2026-08-19.
    Plenty of courts print unsigned papers on purpose: va's convening
    orders, ca9's memorandum dispositions, ark's clerk hand-down sheet,
    wva's DISMISSAL ORDER. The per-file flag already exempts a document
    that signs nothing, which is right — but it made the opposite failure
    invisible, because a court that signs NOTHING exempts every file one at
    a time. va read 44 of 50 majorities unauthored and never raised a flag;
    the cause was that Virginia announces its author in the caption instead
    of signing, and no file could see that on its own.

    So ask it of the COURT. A court that signs most of its majorities and
    misses a few has a defect in those few; a court that signs none either
    never signs or is not being read — and that is one question for a human,
    once, not fifty silent files."""
    html = path.read_text()
    kept = _DETAILS.sub("", html)
    n = signed = 0
    for m in _OPCHIP.finditer(kept):
        n += 1
        if 'class="byline"' in m.group(2):
            signed += 1
    return n, signed


def run(courts: list[str] | None = None) -> dict:
    files: dict[str, dict] = {}
    rollup: dict[str, dict] = {}
    if QUALITY.exists():           # partial reruns keep other courts' rows
        old = json.loads(QUALITY.read_text())
        files, rollup = old.get("files", {}), old.get("courts", {})
    court_dirs = sorted(
        d for d in OUTPUT_DIR.iterdir()
        if d.is_dir() and d.name not in ("notes", ".pageimg")
        and (not courts or d.name in courts))
    for cd in court_dirs:
        scores = []
        maj = maj_signed = 0
        for p in sorted(cd.glob("*.html")):
            if p.stem == "index":
                continue
            row = score_file(p)
            files[f"{cd.name}/{p.stem}"] = row
            scores.append(row["s"])
            _n, _sg = signing_rate(p)
            maj += _n
            maj_signed += _sg
        if not scores:
            continue
        mean = sum(scores) / len(scores)
        ab = sum(1 for s in scores if s <= 2) / len(scores)
        rollup[cd.name] = {"g": _court_grade(mean), "s": round(mean, 2),
                           "n": len(scores), "ab": round(ab, 2),
                           # what share of this court's MAJORITY writings
                           # carry a byline: 1.0 = every one, 0.0 = the
                           # court signs nothing (fine, or unread — look once)
                           "sign": round(maj_signed / maj, 2) if maj else None}
    QUALITY.parent.mkdir(parents=True, exist_ok=True)
    QUALITY.write_text(json.dumps(
        {"files": files, "courts": rollup}, indent=0, sort_keys=True))
    return rollup


def main(args: list[str]) -> int:
    rollup = run([a for a in args if not a.startswith("-")] or None)
    worst = sorted(rollup.items(), key=lambda kv: -kv[1]["s"])
    print(f"{'court':<14} grade  mean  files  A/B%")
    for court, r in worst:
        print(f"{court:<14} {r['g']:^5} {r['s']:>5} {r['n']:>5}  {int(r['ab']*100):>3}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
