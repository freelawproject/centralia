"""Web views for browsing/reviewing the extracted corpus."""
import json
import subprocess
import sys
from collections import Counter

from django.conf import settings
from django.core.management import call_command
from django.db.models import Avg, Sum
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
from .models import Court, Document, Opinion

_OUTPUT_DIR = settings.BASE_DIR / "output"


def _rebuild_manifest():
    """Rewrite output/manifest.js from the DB (court → files, suspect flag) so
    the viewer sidebar's counts match after a re-ingest."""
    man = {
        c.court_id: [
            {"n": d.stem, "href": f"{c.court_id}/{d.stem}.html", "s": d.suspect}
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
            return (f'<div class="hmline" style="text-align:{al};'
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
            f"<span>{_inline_to_html(t)}</span> " for _tag, t in f.paragraphs)))
            for f in op.footnotes.all()]
        opinions.append({"op": op, "body": body, "footnotes": fns})
    return render(request, "library/document_detail.html", {
        "doc": doc, "headmatter": headmatter, "syllabus": syllabus,
        "headnotes": headnotes,
        "opinions": opinions, "dropped": doc.dropped, "trailer": doc.trailer,
        "residual": doc.residual})
