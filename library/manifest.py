"""The review viewer's manifest: output/manifest.js, built from the DB.

This lives outside ``views.py`` because it is not a view. The homepage viewer
reads its per-document health chips from this file, so ANY path that changes
what the DB holds has to rewrite it — the web ``reprocess`` endpoint and the
``ingest`` management command alike. When only the endpoint rebuilt it, a plain
``manage.py ingest`` left the homepage showing a snapshot of the old
extraction: akd/gov.uscourts.akd.67200.99.0 sat at "footnote sequence breaks:
missing 19, 20, 21, …" for a day after the run that gave it a complete 1-181.
"""
import json
from pathlib import Path

from django.conf import settings

_OUTPUT_DIR = settings.BASE_DIR / "output"

_NON_OPINION_TYPES = {"certificate-of-judgment", "filing", "notice", "order"}


def document_quality(d):
    """Return the viewer color bucket and its plain-language diagnosis.

    Keep mutually useful failures separate here: a raster scan is not a parser
    bug, an unreadable font map is not a scan, and an intentionally
    non-opinion document is not a missing opinion.  The first matching bucket
    is the document's most actionable diagnosis; the hover text supplies the
    detail.
    """
    warnings = [str(w) for w in (d.warnings or [])]
    warning_text = " ".join(warnings)
    warning_lower = warning_text.lower()
    has_opinions = d.opinions.exists()

    if d.doc_type == "error":
        return "error", "extractor crashed" + (f": {warnings[0]}" if warnings else "")

    if (
        "unreadable text layer" in warning_lower
        or "unmapped (cid:n)" in warning_lower
        or "cid glyph" in warning_lower
    ):
        return "text-layer", "unreadable PDF text layer (missing character map)"

    if (
        "non-born-digital" in warning_lower
        or "scanned image-only" in warning_lower
        or "needs ocr" in warning_lower
    ):
        return "scan", "scanned PDF; OCR/extraction work required"

    if d.residual and any(
        not isinstance(r, dict) or r.get("kind") != "furniture"
        for r in d.residual
    ):
        return "unplaced", "authored content remains unplaced"

    if not has_opinions and (d.suspect or d.doc_type == "opinion"):
        detail = "no opinion body parsed"
        if d.suspect:
            detail += "; multi-page content landed in headmatter"
        return "missing-opinion", detail

    if d.doc_type == "unknown":
        return "unclassified", "born-digital document type is still unknown"

    if not has_opinions:
        if d.doc_type in _NON_OPINION_TYPES:
            return "non-opinion", f"{d.doc_type}; no judicial opinion expected"
        return "missing-opinion", "no opinion body parsed"

    layout_reasons = []
    if d.coverage and d.coverage < 100:
        layout_reasons.append(f"source coverage {d.coverage:g}%")
    if not d.layout_ok:
        layout_reasons.append("layout does not match the expected court format")
    if layout_reasons:
        return "layout", "; ".join(layout_reasons)

    # The certificate warning records an intentional parser choice, not a
    # failure. Any other warning gets its own review color.
    actionable_warnings = [
        w for w in warnings
        if not w.startswith("body not parsed for doc_type=certificate-of-judgment")
    ]
    if actionable_warnings:
        # "warning" was one undifferentiated bucket of 708 documents, which is
        # not a worklist. It is four separate problems, so name them: 574 were
        # an unplaced image, 128 were footnotes, 22 were body text sitting in
        # the headmatter, 20 were everything else. The diagnosis string still
        # carries every warning verbatim; only the headline changes. Ordered
        # most-actionable first — a document with both a footnote fault and an
        # unplaced image is a footnote job.
        detail = "; ".join(actionable_warnings)
        low = " ".join(actionable_warnings).lower()
        if "misfiled as headmatter" in low:
            return "misfiled", detail
        if "footnote" in low:
            return "footnotes", detail
        if "embedded image" in low:
            return "images", detail
        return "warning", detail

    return "clean", "clean extraction"


def rebuild_manifest():
    """Rewrite output/manifest.js from the DB, including review-facing health.

    ``q`` names a specific extraction outcome so the static viewer can give
    scans, text-layer failures, parser failures, and intentional non-opinions
    visibly different treatments.

    Returns the number of documents written, so callers can report it.
    """
    from .models import Court

    man = {
        c.court_id: [
            {"n": d.stem, "href": f"{c.court_id}/{d.stem}.html",
             "s": d.suspect, "q": diagnosis[0], "qd": diagnosis[1]}
            for d in c.documents.all().order_by("stem")
            for diagnosis in [document_quality(d)]
        ]
        for c in Court.objects.all().order_by("court_id")
    }
    (_OUTPUT_DIR / "manifest.js").write_text(
        "const MANIFEST=" + json.dumps(man) + ";\n"
    )
    return sum(len(v) for v in man.values())


_STAMP = _OUTPUT_DIR / ".manifest.stamp"


def _db_stamp():
    """A cheap fingerprint of everything the chips are computed from.

    NOT file mtimes. The database is in WAL mode, and closing a connection
    checkpoints the log — which stamps db.sqlite3 with a time LATER than the
    manifest that connection just wrote. An mtime test therefore reports
    "stale" forever and rebuilds on every single request.

    These aggregates are one indexed pass over the document table plus a row
    count, and they move if any input to ``document_quality`` moves: the
    warning and residual text, coverage, the flags, the type, the row set, and
    whether opinions exist. Two different corpora colliding on all of them at
    once is not a failure mode worth a hash of every row.
    """
    from django.db import connection

    with connection.cursor() as c:
        c.execute(
            "SELECT COUNT(*), COALESCE(MAX(id),0), COALESCE(SUM(LENGTH(warnings)),0),"
            "       COALESCE(SUM(LENGTH(residual)),0), COALESCE(SUM(coverage),0),"
            "       COALESCE(SUM(suspect),0), COALESCE(SUM(layout_ok),0),"
            "       COALESCE(SUM(LENGTH(doc_type)),0), COALESCE(SUM(LENGTH(stem)),0)"
            "  FROM library_document"
        )
        doc = c.fetchone()
        c.execute("SELECT COUNT(*) FROM library_opinion")
        ops = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM library_court")
        courts = c.fetchone()[0]
    return json.dumps([list(doc), ops, courts])


def rebuild_manifest_if_stale():
    """Rebuild output/manifest.js when the DB no longer matches it.

    This is the backstop that makes the viewer's health chips correct no matter
    HOW the data changed — the ingest command, the reprocess endpoint, a
    ``manage.py shell`` session, or a hand-edited row. Write paths can be added
    without remembering to rewrite the manifest; the read path notices.

    Returns the document count when it rebuilt, else None.
    """
    stamp = _db_stamp()
    if (_OUTPUT_DIR / "manifest.js").exists():
        try:
            if _STAMP.read_text(encoding="utf-8") == stamp:
                return None
        except OSError:
            pass
    n = rebuild_manifest()
    _STAMP.write_text(stamp, encoding="utf-8")
    return n
