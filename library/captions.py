"""A gallery of the case-caption styles in the corpus, rendered as ASCII.

Different courts open an opinion in strikingly different ways — a centered stack,
a boxed two-column docket, a bilingual panel, a workers'-comp filing stamp. This
module curates the distinct families, with a real ASCII rendering of a
representative caption (positioned by each word's true x-coordinate, so the
layout you see is the layout on the page). Served at ``/captions``.
"""

from __future__ import annotations

from django.conf import settings

_ASSETS = settings.BASE_DIR / "assets"
_CHAR_W = 6.4   # pt per monospace column
_WIDTH = 86     # hard wrap


def render_caption(court: str, filename: str, top_max: float = 360.0) -> str:
    """ASCII rendering of a PDF's page-1 caption region: every word placed at
    its real (x0, top), so two-column boxes and centered stacks both survive."""
    import pdfplumber

    path = _ASSETS / court / filename
    if not path.exists():
        return f"[missing: {court}/{filename}]"
    with pdfplumber.open(str(path)) as pdf:
        page = pdf.pages[0]
        words = [
            w
            for w in page.extract_words(use_text_flow=False)
            if w["top"] < top_max and (w.get("text") or "").strip()
        ]
    words.sort(key=lambda w: (round(w["top"]), w["x0"]))
    rows, cur, ctop = [], [], None
    for w in words:
        if ctop is None or abs(w["top"] - ctop) <= 5:
            cur.append(w)
            ctop = ctop if ctop is not None else w["top"]
        else:
            rows.append(cur)
            cur, ctop = [w], w["top"]
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        line = ""
        for w in sorted(r, key=lambda w: w["x0"]):
            col = max(len(line) + (1 if line else 0), round((w["x0"] - 70) / _CHAR_W))
            line += " " * (col - len(line)) + w["text"]
        out.append(line[:_WIDTH].rstrip())
    return "\n".join(out).strip("\n")


# The curated families. ``courts`` is representative, not exhaustive.
STYLES = [
    {
        "id": "centered-stack",
        "title": "The Centered Stack",
        "tag": "most state supreme & appellate courts",
        "courts": "kan · ark · iowa · minn · mont · nd · neb · nh · nm · ohio · "
        "ri · sc · tenn · utah · vt · wash · wis · wyo",
        "sample": ("kan", "king_v._schwert.pdf", 415),
        "blurb": [
            "The workhorse. Everything is centered and stacked: the court banner, "
            "the docket number, then the parties — appellant on top, a centered "
            "<i>v.</i>, appellees below — with each party's <b>status line</b> "
            "(<i>Appellant,</i> / <i>Appellees.</i>) set in italics.",
            "That italic status line is the tell the extractor keys on: the "
            "<b>last italic line is the end of the caption</b>. What follows is a "
            "centered, all-caps title — here <code>SYLLABUS BY THE COURT</code> — "
            "and from there it's syllabus, then opinion. No left margin to anchor "
            "to; alignment is the whole game.",
        ],
    },
    {
        "id": "boxed-docket",
        "title": "The Boxed Docket (with a pleading gutter)",
        "tag": "federal district courts",
        "courts": "caed · cand · nysd · txsd · ilnd · … (the 90 districts)",
        "sample": ("caed", "gov.uscourts.caed.477689.6.0.pdf", 300),
        "blurb": [
            "Federal trial courts file on numbered pleading paper: a column of "
            "line numbers (1–28) runs down the left margin, and an ECF stamp rides "
            "the very top. The caption is a two-column box — parties on the left, "
            "<code>Case No.</code> on the right, split by a vertical rule.",
            "Those left-margin line numbers are pure furniture; the extractor "
            "finds the vertical rule and drops everything left of it, so "
            "<code>8(a)</code> in the body survives but the gutter <code>8</code> "
            "does not. The author isn't in the caption at all — it's the signature "
            "block at the end.",
        ],
    },
    {
        "id": "bilingual-box",
        "title": "The Bilingual Two-Column Box",
        "tag": "Puerto Rico",
        "courts": "prapp (Tribunal de Apelaciones)",
        "sample": ("prapp", "andr-s_antonio_torres_matos_y_otros_v._geovannie_morales_cintr-n.pdf", 330),
        "blurb": [
            "Puerto Rico opinions are in Spanish and the caption is a true two "
            "columns: the parties and their posture (<i>Recurrido</i>, "
            "<i>Peticionario</i>) on the left, and the court of origin and case "
            "numbers (<code>Civil Núm.</code>, <code>Sobre:</code> the subject) on "
            "the right.",
            "The author is the <b><i>ponente</i></b> — the reporting judge — named "
            "just below the panel (<code>Cintrón Cintrón, Jueza Ponente</code>). "
            "These print on legal-size (8.5×14) paper, so the page is 1008pt tall, "
            "not 792.",
        ],
    },
    {
        "id": "sjc-reporter",
        "title": "The Reporter Slip + Panel",
        "tag": "Massachusetts SJC & Appeals Court",
        "courts": "mass · massappct",
        "sample": ("mass", "banevicius_v._barnstable.pdf", 360),
        "blurb": [
            "Massachusetts leads with a boilerplate <b>NOTICE</b> (slip opinions "
            "subject to revision), then a tight reporter caption: "
            "<code>NAME vs. NAME.</code>, the county and the "
            "<b>argued–decided</b> date pair, and a <code>Present: …, JJ.</code> "
            "panel roster.",
            "Below the panel comes a block of reporter <b>headnotes</b> — "
            "subject-matter topic phrases — which the extractor lifts into the "
            "syllabus field, leaving the procedural history and counsel as "
            "headmatter.",
        ],
    },
    {
        "id": "crim-app-stack",
        "title": "The Discretionary-Review Stack",
        "tag": "Texas Court of Criminal Appeals",
        "courts": "texcrimapp",
        "sample": ("texcrimapp", "young_martin_v._the_state_of_texas.pdf", 545),
        "blurb": [
            "Texas's highest criminal court stacks the court name, the "
            "<code>PD-</code> docket, <code>THE STATE OF TEXAS v. NAME, "
            "Appellee</code>, and the posture (<code>ON … PETITION FOR "
            "DISCRETIONARY REVIEW FROM THE … COURT OF APPEALS</code>).",
            "Then a single bold <b>announcement byline</b> does double duty as the "
            "lineup card: who delivered the opinion, who joined, who concurred, and "
            "who filed separately — even though those separate writings are filed "
            "as their own PDFs.",
        ],
    },
    {
        "id": "michigan-masthead",
        "title": "The Masthead + Justice Roster",
        "tag": "Michigan Supreme Court",
        "courts": "mich",
        "sample": ("mich", "carlonda_naishe_swoope_v._citizens_insurance_co_of_the_midwest.pdf", 470),
        "blurb": [
            "Michigan frames the opinion like letterhead: a right-hand masthead "
            "lists the Chief Justice and Justices, and the caption sits in a box "
            "headed by a letter-spaced <code>S T A T E   O F   M I C H I G A N / "
            "SUPREME COURT</code>.",
            "The roster and the <code>FILED</code> stamp repeat on the syllabus "
            "title page and the opinion's first page — page furniture the extractor "
            "drops. The opinion opens after <code>BEFORE THE ENTIRE BENCH</code> at "
            "a non-bold byline, <code>BOLDEN, J.</code>",
        ],
    },
    {
        "id": "in-the-matter-order",
        "title": "The “In the Matter of” Order",
        "tag": "disciplinary & clerk's orders",
        "courts": "kan · mich · wva · mass (single-justice)",
        "sample": ("kan", "in_re_janoski.pdf", 200),
        "blurb": [
            "When there's no authored opinion, the caption shrinks: court banner, "
            "docket, <code>In the Matter of NAME,</code> and an italic "
            "<i>Respondent.</i> — then a centered, all-caps document type "
            "(<code>ORDER</code>).",
            "There's no byline to find, so the extractor treats the centered type "
            "line as the start of the body and authors it <b>PER CURIAM</b>. The "
            "italic status line is, again, the end of the caption.",
        ],
    },
    {
        "id": "workers-comp",
        "title": "The “Below” Posture + Filing Stamp",
        "tag": "WV Intermediate Court of Appeals",
        "courts": "wvactapp",
        "sample": ("wvactapp", "brandon_carter_v._seven_rivers_design_build_llc.pdf", 260),
        "blurb": [
            "West Virginia's intermediate court spells out each party's posture "
            "below — <code>Claimant Below, Petitioner</code> / <code>Employer "
            "Below, Respondent</code> — around a <code>v.)</code> line carrying the "
            "ICA docket and the workers'-comp claim number, with a "
            "<code>FILED</code> clerk stamp boxed on the right.",
            "Most of these are per-curiam <b>MEMORANDUM DECISIONS</b> (Rule 21 "
            "affirmances): a bold, centered header opens the body with no byline at "
            "all.",
        ],
    },
    {
        "id": "conn-reporter",
        "title": "The Officially-Released Reporter",
        "tag": "Connecticut",
        "courts": "conn · connappct",
        "sample": ("conn", "state_v._baez.pdf", 360),
        "blurb": [
            "Connecticut brackets an <b>officially-released</b> notice in rows of "
            "asterisks, repeats the short case name as a running header on every "
            "page, and prints a long official <code>Syllabus</code> before the "
            "argued/decided panel.",
            "The syllabus spans pages, so the extractor orders the headmatter "
            "page-aware (a y-only sort would interleave them) and captures the "
            "<code>Syllabus</code> block separately from the opinion.",
        ],
    },
]


_CACHE: dict = {}


def gallery() -> list:
    """The styles with their ASCII captions rendered (memoized per process)."""
    out = []
    for s in STYLES:
        court, fn, top = s["sample"]
        key = (court, fn, top)
        if key not in _CACHE:
            try:
                _CACHE[key] = render_caption(court, fn, top)
            except Exception as exc:  # never let one bad PDF break the page
                _CACHE[key] = f"[render error: {exc}]"
        out.append({**s, "ascii": _CACHE[key], "sample_label": f"{court}/{fn}"})
    return out
