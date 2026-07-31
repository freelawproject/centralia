"""Web views for browsing/reviewing the extracted corpus."""
import json
import re
import subprocess
import sys
from collections import Counter

from django.conf import settings
from django.core.management import call_command
from django.db.models import Avg, Count, Sum
from django.http import (
    FileResponse,
    Http404,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from centralia.registry import EXTRACTORS
from centralia.render.html import _inline_to_html
from .families import family_of, similar_courts
from .models import Block, Court, Document, Footnote, Opinion

_OUTPUT_DIR = settings.BASE_DIR / "output"


def _rebuild_manifest():
    """Rewrite output/manifest.js from the DB, including review-facing health.

    ``q`` is intentionally small and stable because the static viewer only
    needs to choose a color and explain it on hover:
    clean, unplaced, no-opinions, or issue.
    """
    def quality(d):
        if d.doc_type == "error":
            return "issue", "extraction error"
        if d.residual and any(
            not isinstance(r, dict) or r.get("kind") != "furniture"
            for r in d.residual
        ):
            return "unplaced", "unplaced content"
        if not d.opinions.exists():
            return "no-opinions", (
                "no opinions parsed" + ("; suspect extraction" if d.suspect else "")
            )
        reasons = []
        if d.coverage and d.coverage < 100:
            reasons.append(f"coverage {d.coverage:g}%")
        if not d.layout_ok:
            reasons.append("layout mismatch")
        if d.warnings:
            reasons.append("extractor warning")
        if d.suspect:
            reasons.append("suspect extraction")
        return ("issue", "; ".join(reasons)) if reasons else ("clean", "good")

    man = {
        c.court_id: [
            {"n": d.stem, "href": f"{c.court_id}/{d.stem}.html",
             "s": d.suspect, "q": quality(d)[0], "qd": quality(d)[1]}
            for d in c.documents.all().order_by("stem")
        ]
        for c in Court.objects.all().order_by("court_id")
    }
    (_OUTPUT_DIR / "manifest.js").write_text(
        "const MANIFEST=" + json.dumps(man) + ";\n"
    )


@csrf_exempt
def reprocess(request, court_id):
    """Re-run the extractor for one court with the latest code, regenerate its
    HTML, re-ingest the DB, and rebuild the manifest. The extraction runs as a
    fresh subprocess so edits to the court's .py are picked up even if this
    server process hasn't reloaded yet. Local review tool — CSRF-exempt."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    assets = settings.BASE_DIR / "assets" / court_id
    if court_id not in EXTRACTORS and not assets.is_dir():
        return JsonResponse({"ok": False, "error": f"unknown court {court_id!r}"}, status=404)
    if not assets.is_dir():
        return JsonResponse(
            {"ok": False, "error": f"no assets/{court_id}/ directory"}, status=404
        )
    # Optional single-PDF mode (?pdf=<stem> or form field): re-run just one
    # document — much faster than the whole court when iterating on one file.
    stem = (request.POST.get("pdf") or request.GET.get("pdf") or "").strip()
    if stem:
        if "/" in stem or "\\" in stem or stem.startswith("."):
            return JsonResponse({"ok": False, "error": "bad pdf name"}, status=400)
        if not (assets / f"{stem}.pdf").is_file():
            return JsonResponse(
                {"ok": False, "error": f"no assets/{court_id}/{stem}.pdf"},
                status=404,
            )
        # no --index: a single-file run must not rewrite the court index
        cmd = [
            sys.executable, "-m", "centralia.cli", court_id,
            f"assets/{court_id}/{stem}.pdf", "--html", "--output",
        ]
    else:
        cmd = [
            sys.executable, "-m", "centralia.cli", court_id,
            f"assets/{court_id}", "--html", "--output", "--index",
        ]
    try:
        proc = subprocess.run(
            cmd, cwd=str(settings.BASE_DIR),
            capture_output=True, text=True, timeout=900,
        )
    except subprocess.TimeoutExpired:
        return JsonResponse({"ok": False, "error": "extraction timed out"}, status=504)
    if proc.returncode != 0:
        return JsonResponse(
            {"ok": False, "error": "extraction failed",
             "log": (proc.stderr or proc.stdout or "")[-2000:]},
            status=500,
        )
    summary = (proc.stdout or "").strip().splitlines()
    summary = summary[-1] if summary else ""
    # Re-ingest + refresh the manifest so the DB-backed views and sidebar match.
    try:
        if stem:
            call_command("ingest", court_id, "--no-audit", pdf=stem)
        else:
            call_command("ingest", court_id, "--no-audit")
        _rebuild_manifest()
    except Exception as exc:  # html is already regenerated; report the rest
        return JsonResponse(
            {"ok": True, "court": court_id, "summary": summary, "pdf": stem,
             "warn": f"ingest/manifest: {exc}"}
        )
    return JsonResponse(
        {"ok": True, "court": court_id, "summary": summary, "pdf": stem}
    )


def viewer(request):
    """Serve the JavaScript review viewer (output/viewer.html) as the homepage.
    Its assets — manifest.js, notes.js, and the per-court <court>/<stem>.html
    documents loaded into the iframe — are served from output/ by the static
    routes in webconfig/urls.py; the notes panel talks to the notes server."""
    f = _OUTPUT_DIR / "viewer.html"
    if not f.exists():
        raise Http404("viewer.html not found — run the CLI with --output first")
    return FileResponse(f.open("rb"), content_type="text/html")

# Sidebar grouping (mirrors the static viewer).
_CIRCUITS = set("ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11 cadc cafc".split())
_DISTRICTS = set(("akd almd alnd alsd ared arwd azd cacd caed cand casd cod ctd "
    "ded dcd flmd flnd flsd gamd gand gasd hid iand iasd idd ilcd ilnd ilsd innd "
    "insd ksd kyed kywd laed lamd lawd mad mdd med mied miwd mnd moed mowd msnd "
    "mssd mtd nced ncmd ncwd ndd ned nhd njd nmd nvd nyed nynd nysd nywd ohnd "
    "ohsd oked oknd okwd ord paed pamd pawd rid scd sdd tned tnmd tnwd txed txnd "
    "txsd txwd utd vaed vawd vtd waed wawd wied wiwd wvnd wvsd wyd").split())


_MISC = set((
    "acca afcca armfor asbca bia bap1 bap6 bap8 bap9 bap10 cavc cit guam mspb "
    "nmariana nmcca olc tax ttab uscfc uscgcoca virginislands "
    "nyfamct nycivct nysupct nysurct njtaxct vtsuperct pacommwct "
    "ortc pasuperct minnag mdag texag").split())


def _group(cid):
    if cid in _DISTRICTS:
        return ("District courts", 0)
    if cid in _CIRCUITS:
        return ("Federal circuits", 1)
    if cid in _MISC:
        return ("Misc / specialized", 3)
    return ("State courts", 2)


def court_list(request):
    courts = list(Court.objects.all())
    for c in courts:
        c.grp = _group(c.court_id)
    courts.sort(key=lambda c: (c.grp[1], c.court_id))
    return render(request, "library/court_list.html", {"courts": courts})


@csrf_exempt
def review_marks(request):
    """Durable store for the viewer's review marks, served by the same Django
    process as the viewer (no separate notes-server dependency). Persists to
    output/notes/_marks.json (per-court 5-tier rating: nay → some → good →
    almost → yay), _filemarks.json (per-PDF),
    and _done.json (per-court done). GET returns all three; POST replaces whichever
    of {marks, filemarks, done} the body supplies."""
    notes = _OUTPUT_DIR / "notes"

    def _load(name):
        f = notes / name
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(name, data):
        notes.mkdir(parents=True, exist_ok=True)
        (notes / name).write_text(
            json.dumps(data, indent=0, sort_keys=True), encoding="utf-8"
        )

    if request.method == "GET":
        return JsonResponse({
            "marks": _load("_marks.json"),
            "filemarks": _load("_filemarks.json"),
            "done": _load("_done.json"),
        })
    if request.method == "POST":
        try:
            body = json.loads(request.body or b"{}")
        except Exception:
            return JsonResponse({"error": "bad json"}, status=400)
        rating = ("yay", "almost", "good", "some", "nay")
        if isinstance(body.get("marks"), dict):
            _save("_marks.json", {k: v for k, v in body["marks"].items() if v in rating})
        if isinstance(body.get("filemarks"), dict):
            _save("_filemarks.json",
                  {k: v for k, v in body["filemarks"].items() if v in rating})
        if isinstance(body.get("done"), dict):
            _save("_done.json", {k: True for k, v in body["done"].items() if v})
        return JsonResponse({"ok": True})
    return HttpResponseNotAllowed(["GET", "POST"])


def captions(request):
    """A long-form field guide to the distinct case-caption *line styles* —
    how courts draw the dividers, rules, brackets and arrows — recreated in
    ASCII, with facet tags and the parsing signal each one gives us."""
    from .caption_catalog import FACETS, STYLES

    order = [
        ("one-column", "One-Column Styles", "no party columns — centered stacks"),
        ("two-column", "Two-Column Styles", "parties on the left, metadata on the right"),
        ("three-column", "Three-Column Styles", "a third column splits the metadata"),
    ]
    groups, n = [], 0
    for col, label, blurb in order:
        items = []
        for s in STYLES:
            if s.get("tags", {}).get("columns") != col:
                continue
            tags = s["tags"]
            pairs = [(f, tags[f]) for f in FACETS if tags.get(f) and tags[f] != "—"]
            n += 1
            items.append({**s, "tag_list": pairs, "num": n})
        if items:
            groups.append({"col": col, "label": label, "blurb": blurb, "items": items})
    return render(
        request, "library/captions.html", {"groups": groups, "total": n}
    )


def styles(request):
    """Group every document by the headmatter *style family* of its court — the
    extractor base class that parses its headmatter/byline. Courts in one group
    are parsed alike, so this is the place to spot a court that should behave
    like its siblings but doesn't. One DB pass, aggregated in Python."""
    from collections import defaultdict

    from .families import COURT_FAMILY

    # fam -> court_id -> [n_docs, n_suspect]; fam -> doc_type Counter.
    fam_courts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    fam_types = defaultdict(Counter)
    for cid, dt, susp in Document.objects.values_list(
        "court_id", "doc_type", "suspect"
    ):
        fam = COURT_FAMILY.get(cid)
        if not fam:
            continue
        fam_courts[fam][cid][0] += 1
        if susp:
            fam_courts[fam][cid][1] += 1
        fam_types[fam][dt] += 1

    families = []
    for fam, courts in fam_courts.items():
        rows = [
            {"id": cid, "n": v[0], "suspect": v[1]}
            for cid, v in sorted(courts.items())
        ]
        families.append(
            {
                "name": fam,
                "courts": rows,
                "n_courts": len(rows),
                "n_docs": sum(r["n"] for r in rows),
                "suspect": sum(r["suspect"] for r in rows),
                "types": sorted(
                    fam_types[fam].items(), key=lambda x: (-x[1], x[0])
                ),
            }
        )
    families.sort(key=lambda f: -f["n_docs"])
    return render(request, "library/styles.html", {"families": families})


def court_detail(request, court_id):
    court = get_object_or_404(Court, court_id=court_id)
    docs = list(court.documents.all())
    # File-type breakdown + corpus stats (auto-derived from the documents).
    agg = court.documents.aggregate(pages=Sum("n_pages"), cov=Avg("coverage"))
    stats = {
        "n_docs": len(docs),
        "types": sorted(
            Counter(d.doc_type for d in docs).items(), key=lambda x: (-x[1], x[0])
        ),
        "pages": agg["pages"] or 0,
        "coverage": round(agg["cov"] or 0, 1),
        "suspect": sum(1 for d in docs if d.suspect),
        "opinions": Opinion.objects.filter(document__court=court).count(),
    }
    fam = family_of(court_id)
    siblings = similar_courts(court_id)
    return render(
        request,
        "library/court_detail.html",
        {
            "court": court,
            "documents": docs,
            "family": fam,
            "similar": siblings,
            "stats": stats,
        },
    )


def _row_html(row):
    """Render a headmatter/syllabus summary row (str | dict) to HTML."""
    if isinstance(row, dict):
        if row.get("__hm__"):
            al = {"C": "center", "L": "left", "R": "right"}.get(row.get("align"), "left")
            # 'ind' = the row's offset from the caption's own left edge, in pt.
            ind = row.get("ind")
            pad = f"padding-left:{ind}pt;" if ind else ""
            zones = row.get("zones")
            if zones and len(zones) > 1:
                # Separate columns on one baseline: keep each on its own side.
                cells = "".join(
                    '<div style="text-align:{}">{}</div>'.format(
                        "right" if z.get("align") == "r" else "left",
                        _inline_to_html(str(z.get("h", ""))))
                    for z in zones)
                return (f'<div class="hmline" style="{pad}display:flex;'
                        f'justify-content:space-between;column-gap:1rem;'
                        f'font-size:{row.get("rel", 1)}em">{cells}</div>')
            return (f'<div class="hmline" style="{pad}text-align:{al};'
                    f'font-size:{row.get("rel", 1)}em">'
                    f'{_inline_to_html(str(row.get("html", "")))}</div>')
        if row.get("__caption__"):
            def _cell(x):
                if isinstance(x, dict):  # faithful cell: {'h': html, 'ind': pt}
                    return _inline_to_html(str(x.get("h", "")))
                return _inline_to_html(str(x))
            left = "".join(f'<div>{_cell(x)}</div>' for x in row.get("left", []))
            right = "".join(f'<div>{_cell(x)}</div>' for x in row.get("right", []))
            return (f'<div class="caption-cols"><div class="cl">{left}</div>'
                    f'<div class="cdiv"></div>'
                    f'<div class="cr">{right}</div></div>')
        return f'<div class="rawline">{_inline_to_html(str(row))}</div>'
    if str(row).strip() == "__DIVIDER__":
        return '<hr class="divider">'
    return f'<div class="rawline">{_inline_to_html(str(row))}</div>'


def _block_html(b):
    if b.kind == "heading":
        return f"<h3>{_inline_to_html(b.text)}</h3>"
    if b.kind == "blockquote":
        return f"<blockquote>{_inline_to_html(b.text)}</blockquote>"
    if b.kind == "image":
        src = b.payload.get("src", "")
        return f'<img src="{src}" alt="figure">' if src else ""
    return f"<p>{_inline_to_html(b.text)}</p>"


def document_detail(request, court_id, stem):
    doc = get_object_or_404(Document, court__court_id=court_id, stem=stem)
    headmatter = mark_safe("".join(_row_html(r) for r in doc.summary))
    syllabus = mark_safe("".join(_row_html(r) for r in doc.syllabus))
    headnotes = mark_safe("".join(_row_html(r) for r in doc.headnotes))
    opinions = []
    for op in doc.opinions.all():
        body = mark_safe("".join(_block_html(b) for b in op.blocks.all()))
        fns = [(f.label, mark_safe("".join(
            # A ('table', markup) paragraph is a table printed inside the
            # footnote; its cells are already escaped, so emit it verbatim.
            str(t) if tag == "table" else f"<span>{_inline_to_html(t)}</span> "
            for tag, t in f.paragraphs)))
            for f in op.footnotes.all()]
        opinions.append({"op": op, "body": body, "footnotes": fns})
    return render(request, "library/document_detail.html", {
        "doc": doc, "headmatter": headmatter, "syllabus": syllabus,
        "headnotes": headnotes,
        "opinions": opinions, "dropped": doc.dropped, "trailer": doc.trailer,
        "residual": doc.residual})


def audit(request):
    """Corpus-wide extraction audit — what still needs work, right now.

    Ranked by severity, because the three things that get conflated when you
    eyeball a Removed box are not equally urgent:

    * **no writing returned** — a document that produced no opinion at all.
      The worst outcome, and counted ONLY where a writing was expected: a
      scanned image has nothing to parse, and some doc types deliberately
      carry no body. Counting scans as failures made Nevada look like 18
      broken files when 17 were image PDFs the extractor was right to skip.
    * **unplaced CONTENT** — real text the parse could not place. The to-do.
    * **unplaced furniture** — a rail glyph, a folio, a running head. Already
      identified; only needs confirming, so it is never highlighted.

    Also rolled up per extractor FAMILY, because that is how fixes travel: a
    change in a shared base moves every court beneath it at once.
    """
    from collections import defaultdict

    from .families import COURT_FAMILY

    def footnote_gap_documents():
        """Return documents whose body marks have no returned footnote.

        This is intentionally the same conservative signal used by the
        ecosystem audit: only numeric marks are reported, and scans / document
        types that are not expected to contain an opinion are excluded.
        """
        no_body = {"certificate-of-judgment", "notice", "order"}
        docs = {
            d["id"]: d
            for d in Document.objects.values("id", "court_id", "stem",
                                              "doc_type", "warnings")
        }
        bodies = defaultdict(list)
        for doc_id, text in Block.objects.filter(
            opinion__isnull=False
        ).values_list("opinion__document_id", "text"):
            if text:
                bodies[doc_id].append(text)
        returned = defaultdict(set)
        for doc_id, label in Footnote.objects.filter(
            opinion__isnull=False
        ).values_list("opinion__document_id", "label"):
            if label:
                returned[doc_id].add(label)

        gaps = defaultdict(list)
        mark_re = re.compile(r"<footnotemark>\s*(\d+)\s*</footnotemark>")
        for doc_id, texts in bodies.items():
            d = docs[doc_id]
            warnings = " ".join(d["warnings"] or [])
            if "non-born-digital" in warnings or "cid" in warnings.lower():
                continue
            if d["doc_type"] in no_body:
                continue
            marks = {m for text in texts for m in mark_re.findall(text)}
            missing = sorted(marks - returned[doc_id], key=lambda x: int(x))
            if missing:
                gaps[d["court_id"]].append({
                    "stem": d["stem"], "labels": ", ".join(missing[:8]),
                })
        return gaps

    _NO_BODY = {"certificate-of-judgment", "notice", "order"}
    per = defaultdict(
        lambda: {
            "files": 0, "content": 0, "furniture": 0, "noop": 0,
            "scans": 0, "cov": [], "worst": None, "noop_stems": [],
        }
    )
    for r in (
        Document.objects.annotate(nops=Count("opinions"))
        .values("court_id", "stem", "doc_type", "nops", "residual",
                "warnings", "coverage")
    ):
        d = per[r["court_id"]]
        d["files"] += 1
        warn = " ".join(r["warnings"] or [])
        scan = "non-born-digital" in warn or "cid" in warn.lower()
        if scan:
            d["scans"] += 1
        res = r["residual"] or []
        n_content = sum(
            1 for x in res if isinstance(x, dict) and x.get("kind") != "furniture"
        )
        d["content"] += n_content
        d["furniture"] += len(res) - n_content
        if n_content and (d["worst"] is None or n_content > d["worst"][1]):
            d["worst"] = (r["stem"], n_content)
        if r["nops"] == 0 and not scan and (r["doc_type"] or "") not in _NO_BODY:
            d["noop"] += 1
            if len(d["noop_stems"]) < 3:
                d["noop_stems"].append(r["stem"])
        if r["coverage"] is not None:
            d["cov"].append(r["coverage"])

    footnote_gaps = footnote_gap_documents()
    courts = []
    for c in Court.objects.all():
        d = per.get(c.court_id)
        if not d or not d["files"]:
            continue
        content, noop = d["content"], d["noop"]
        fn_rows = footnote_gaps.get(c.court_id, [])
        courts.append({
            "court_id": c.court_id,
            "grp": _group(c.court_id)[0],
            "family": COURT_FAMILY.get(c.court_id, "—"),
            "files": d["files"],
            "content": content,
            "furniture": d["furniture"],
            "noop": noop,
            "scans": d["scans"],
            "coverage": (round(sum(d["cov"]) / len(d["cov"]), 1)
                         if d["cov"] else None),
            "worst": d["worst"][0] if d["worst"] else "",
            "worst_n": d["worst"][1] if d["worst"] else 0,
            "noop_stems": d["noop_stems"],
            "footnote_gaps": len(fn_rows),
            "footnote_stems": [r["stem"] for r in fn_rows[:3]],
            # A document with NO writing outranks any number of stray lines.
            "score": noop * 1000 + content,
            "tier": ("noop" if noop else ("content" if content else "clean")),
            "clean": not content and not noop,
        })
    courts.sort(key=lambda c: (-c["score"], c["court_id"]))
    worst_content = max([c["content"] for c in courts] or [1]) or 1
    for c in courts:
        # Bar width relative to the worst court, so scale is visible at a glance.
        c["bar"] = int(round(100.0 * c["content"] / worst_content)) if c["content"] else 0
        # Heat buckets, so a row's colour carries the MAGNITUDE and not just the
        # kind of problem. Bucketed rather than continuous: five steps read as
        # a scale, a per-row gradient just reads as noise.
        n = c["content"]
        c["heat"] = (
            0 if not n else 1 if n <= 5 else 2 if n <= 25 else 3 if n <= 100 else 4
        )
        m = c["noop"]
        c["nheat"] = 0 if not m else 1 if m == 1 else 2 if m <= 3 else 3

    fams = defaultdict(lambda: {"courts": 0, "files": 0, "content": 0, "noop": 0,
                                "clean": 0})
    for c in courts:
        f = fams[c["family"]]
        f["courts"] += 1
        f["files"] += c["files"]
        f["content"] += c["content"]
        f["noop"] += c["noop"]
        f["clean"] += 1 if c["clean"] else 0
    families = sorted(
        ({"name": k, **v} for k, v in fams.items()),
        key=lambda f: (-(f["noop"] * 1000 + f["content"]), f["name"]),
    )

    totals = {
        "courts": len(courts),
        "clean": sum(1 for c in courts if c["clean"]),
        "needs": sum(1 for c in courts if not c["clean"]),
        "files": sum(c["files"] for c in courts),
        "content": sum(c["content"] for c in courts),
        "furniture": sum(c["furniture"] for c in courts),
        "noop": sum(c["noop"] for c in courts),
        "scans": sum(c["scans"] for c in courts),
        "noop_courts": sum(1 for c in courts if c["noop"]),
        "content_courts": sum(1 for c in courts if c["content"] and not c["noop"]),
    }
    return render(request, "library/audit.html", {
        "courts": courts,
        "flagged": [c for c in courts if not c["clean"]],
        "families": families,
        "totals": totals,
        "footnote_gaps": footnote_gaps,
    })
