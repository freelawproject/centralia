"""Step 0 of a family port: diff the PAGES before diffing the code.

For a child court and a candidate parent, dump the shape of page 1 for
several records of each and report how much of the parent's opening
sequence the child reproduces. A high score means the port is a COPY plus
a gate change (kanctapp: minutes). A low score means a real port.

    .venv/bin/python harness/pairdiff.py <child> <parent>
    .venv/bin/python harness/pairdiff.py --all      # every candidate pair
"""
from __future__ import annotations
import glob, re, sys, statistics
from collections import Counter

sys.path.insert(0, "/Users/Palin/Code/rewrite")
from centralia.pdfio import build_pdf                        # noqa: E402
from centralia import geometry                               # noqa: E402

ASSETS = "/Users/Palin/Code/centralia/assets"


def _shape(text: str) -> str:
    """A row reduced to its SHAPE: the identity of the words is the one
    thing that differs between two records of the same court, so it is the
    one thing thrown away. Digits and proper names collapse; structure —
    caps, the pivot, role words, rail glyphs — survives."""
    t = " ".join(text.split())
    if not t:
        return ""
    if re.fullmatch(r"v\.?|vs\.?", t, re.I):
        return "<PIVOT>"
    if re.fullmatch(r"[)(\]\[§*|:;]+", t):
        return "<RAIL>"
    low = t.lower().rstrip(".,")
    for w in ("appellant", "appellee", "petitioner", "respondent",
              "plaintiff", "defendant", "movant", "amicus"):
        if low.startswith(w) or low.endswith(w) or low.endswith(w + "s"):
            return "<ROLE>"
    if re.match(r"^(?:case\s+)?nos?\.\s", t, re.I) or re.match(r"^no\.\s*\d", t, re.I):
        return "<DOCKET>"
    if re.search(r"\b(court|division|district|circuit|term)\b", t, re.I) \
            and t == t.upper():
        return "<COURTNAME>"
    if re.search(r"\b(court|division|district|circuit)\b", t, re.I):
        return "<courtname>"
    if re.match(r"^(?:filed|decided|argued|submitted|dated|released)\b", t, re.I):
        return "<DATELINE>"
    if re.search(r"\b(january|february|march|april|may|june|july|august|"
                 r"september|october|november|december)\s+\d{1,2},\s*\d{4}", t, re.I):
        return "<DATE>"
    if re.match(r"^(syllabus|headnotes?|opinion|order|per curiam|before)\b", t, re.I):
        return "<" + t.split()[0].upper() + ">"
    if t == t.upper() and any(c.isalpha() for c in t):
        return "<CAPS>"
    return "<text>"


def profile(court: str, n: int = 6, rows: int = 30) -> list[str]:
    """The court's own opening sequence: the shape most of its records
    agree on, row by row."""
    pdfs = sorted(glob.glob(f"{ASSETS}/{court}/*.pdf"))[:n]
    seqs = []
    for p in pdfs:
        try:
            m = build_pdf(p)
        except Exception:
            continue
        ls = sorted(m.pages[0].lines, key=lambda l: l.top)
        seqs.append([_shape(l.plain) for l in ls if l.plain.strip()][:rows])
    if not seqs:
        return []
    out = []
    for i in range(rows):
        c = Counter(s[i] for s in seqs if len(s) > i)
        if not c:
            break
        shape, hits = c.most_common(1)[0]
        out.append(shape if hits >= max(2, len(seqs) // 2) else "<*>")
    return out


# FILLER. A caption is a variable number of party rows, so aligning two
# courts row-by-row drifts the moment one has three defendants and the
# other has one. The LANDMARKS are what a reader dispatches on, and they
# survive that drift; everything else is noise for this purpose.
_FILLER = {"<text>", "<CAPS>", "<*>", "<courtname>", ""}


def landmarks(seq: list[str]) -> list[str]:
    """The opening reduced to the rows a reader would key on, in order,
    with runs collapsed (three <ROLE> rows and one mean the same thing to
    a dispatch)."""
    out: list[str] = []
    for s in seq:
        if s in _FILLER:
            continue
        if out and out[-1] == s:
            continue
        out.append(s)
    return out


def score(child: list[str], parent: list[str]) -> float:
    """Longest common subsequence over the LANDMARKS, as a fraction of the
    parent's. Order matters — kan and kanctapp differ ONLY in that the
    docket and the masthead are swapped, and that shows up here as one
    dropped landmark rather than a wholesale mismatch."""
    a, b = landmarks(child), landmarks(parent)
    if not a or not b:
        return 0.0
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            dp[i + 1][j + 1] = (dp[i][j] + 1 if a[i] == b[j]
                                else max(dp[i][j + 1], dp[i + 1][j]))
    return dp[len(a)][len(b)] / len(b)


def report(child: str, parent: str) -> tuple[float, list[str], list[str]]:
    c, p = profile(child), profile(parent)
    return score(c, p), c, p


if __name__ == "__main__":
    if sys.argv[1:2] == ["--all"]:
        pairs = [tuple(x.split(":")) for x in sys.argv[2].split(",")]
    else:
        pairs = [(sys.argv[1], sys.argv[2])]
    for child, parent in pairs:
        s, c, p = report(child, parent)
        lc, lp = landmarks(c), landmarks(p)
        verdict = ("COPY + gate change" if s >= 0.80 else
                   "adapt (shared skeleton)" if s >= 0.55 else
                   "cold port")
        print(f"\n=== {child} <- {parent} : {s:.0%}  {verdict} ===")
        print(f"   child landmarks:  {' '.join(lc)}")
        print(f"   parent landmarks: {' '.join(lp)}")
