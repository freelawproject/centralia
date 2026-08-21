"""Run the per-court extractors over the asset corpus and load the results
into the database.

  uv run python manage.py ingest               # all courts
  uv run python manage.py ingest ariz ohio     # specific courts
  uv run python manage.py ingest --no-audit    # skip coverage (faster)
"""

import glob
import json
import os
from concurrent.futures import ProcessPoolExecutor

import dataclasses

from django.core.management.base import BaseCommand
from django.db import transaction

from centralia.models import DocType
from centralia.registry import get_extractor


def _extract_pdf(job):
    """Extract one PDF without touching Django or the database.

    Keeping this worker at module scope makes it safe for multiprocessing's
    spawn mode on macOS.  The parent process remains the only database writer,
    so SQLite retains the same per-court transactional guarantees as the
    original sequential command.
    """
    cid, path, do_audit = job
    extractor = get_extractor(cid)
    try:
        doc = extractor.extract(path)
    except Exception as exc:
        return path, None, str(exc), 0.0

    coverage = 0.0
    if do_audit:
        try:
            from centralia.audit import audit_coverage

            result = audit_coverage(doc, path, extractor=extractor)
            coverage = (
                round(100 * result.covered / result.total, 1)
                if result.total
                else 100.0
            )
        except Exception:
            coverage = 0.0
    return path, doc, None, coverage


def _jsonable(value):
    """JSON-safe copy of an extraction section.

    Extractors may place rich dataclasses (a ``Block`` moved into the
    trailer — gactapp/kyctapp's clerk-certificate ending matter, images
    included) into sections the DB stores as JSON. Serialize them to their
    dict form instead of crashing the whole ingest run."""
    def conv(x):
        if dataclasses.is_dataclass(x) and not isinstance(x, type):
            return dataclasses.asdict(x)
        if isinstance(x, dict):
            return {k: conv(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [conv(v) for v in x]
        return x

    return [conv(v) for v in (value or [])]

ASSETS = "assets"
NOTES_DIR = "output/notes"


def _load_notes():
    notes, done = {}, {}
    if os.path.isdir(NOTES_DIR):
        for md in glob.glob(f"{NOTES_DIR}/*.md"):
            notes[os.path.basename(md)[:-3]] = open(md, encoding="utf-8").read()
    df = f"{NOTES_DIR}/_done.json"
    if os.path.isfile(df):
        try:
            done = json.load(open(df))
        except Exception:
            done = {}
    return notes, done


class Command(BaseCommand):
    help = "Extract the PDF corpus into the database."

    def add_arguments(self, parser):
        parser.add_argument("courts", nargs="*", help="court ids (default: all)")
        parser.add_argument("--no-audit", action="store_true",
                            help="skip coverage computation")
        parser.add_argument("--no-manifest", action="store_true",
                            help="skip rewriting output/manifest.js")
        parser.add_argument("--pdf", metavar="STEM",
                            help="refresh only this document (PDF stem) "
                                 "instead of the whole court")
        parser.add_argument(
            "--workers",
            type=int,
            default=0,
            help="parallel PDF extraction workers, 0 = auto (cores - 2, max 8). "
                 "Database writes stay serial whatever this is.",
        )

    @staticmethod
    def _auto_workers(n_files: int) -> int:
        """How many extraction workers to use when ``--workers`` is not given.

        Extraction is CPU-bound inside pdfplumber and runs in CHILD processes —
        the parent remains the only database writer, so the pool size has no
        bearing on SQLite. The old default of 1 therefore left a 10-core machine
        idle on nine of them: a 580-document refresh took the better part of an
        hour at ~2.9s per document, against ~3.5 minutes spread across a pool.

        Two cores are left for the parent and the rest of the machine, and the
        pool is capped at 8 — a 194-page slip opinion holds a great many char
        objects, and beyond that the run turns memory-bound rather than
        CPU-bound. Never more workers than there are files to hand them."""
        return max(1, min(8, (os.cpu_count() or 2) - 2, n_files))

    def handle(self, *args, **opts):
        from library.models import (Block, Court, Document, Footnote, Opinion)
        do_audit = not opts["no_audit"]

        courts = opts["courts"] or sorted(
            d for d in os.listdir(ASSETS) if os.path.isdir(f"{ASSETS}/{d}"))
        notes, done = _load_notes()
        n_docs = 0
        # Size the pool against the work actually queued, so a single --pdf
        # re-run from the viewer does not pay to spawn eight interpreters.
        n_files = (
            1
            if opts.get("pdf")
            else sum(len(glob.glob(f"{ASSETS}/{cid}/*.pdf")) for cid in courts)
        )
        workers = max(1, opts["workers"] or self._auto_workers(n_files))
        executor = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
        try:
            for cid in courts:
                files = sorted(glob.glob(f"{ASSETS}/{cid}/*.pdf"))
                only = opts.get("pdf")
                if only:
                    files = [f for f in files
                             if os.path.basename(f)[:-4] == only]
                if not files:
                    continue
                ex = get_extractor(cid)
                label = getattr(ex, "court_label", "") or cid
                court, _ = Court.objects.update_or_create(
                    court_id=cid,
                    defaults={"label": label, "notes": notes.get(cid, ""),
                              "claude_done": bool(done.get(cid))})
                jobs = ((cid, path, do_audit) for path in files)
                extracted = (
                    executor.map(_extract_pdf, jobs)
                    if executor is not None
                    else map(_extract_pdf, jobs)
                )
                with transaction.atomic():
                    if only:
                        court.documents.filter(stem=only).delete()
                    else:
                        court.documents.all().delete()  # full refresh per court
                    for f, d, error, cov in extracted:
                        stem = os.path.basename(f)[:-4]
                        if error is not None:
                            # Every NOT NULL text column has to be given a value
                            # on the ERROR path too — it does not go through the
                            # normal field mapping below, and a missing one
                            # failed the whole re-run ('NOT NULL constraint
                            # failed: library_document.attorneys').
                            Document.objects.create(
                                court=court, stem=stem, source_path=f,
                                doc_type="error", warnings=[error], suspect=True,
                                attorneys="")
                            n_docs += 1
                            continue
                        has_body = any(op.blocks for op in d.opinions)
                        # ``suspect`` means "this came out as all headmatter
                        # and probably should not have". Administrative paper
                        # has no judicial body by definition, so an empty body
                        # is the right answer, not a suspicion — vactapp's
                        # clerk list of appealed cases (4pp, doc_type=notice)
                        # was flagged suspect and the viewer bucketed it
                        # 'missing-opinion' instead of 'non-opinion'.
                        suspect = (
                            (not has_body)
                            and d.n_pages > 2
                            and d.doc_type not in DocType.NO_BODY_EXPECTED
                        )
                        warnings = list(d.warnings)
                        if d.non_digital and not any(
                            "non-born-digital" in warning for warning in warnings
                        ):
                            warnings.append(
                                "non-born-digital (scanned image + OCR text layer); "
                                "not processed"
                            )
                        doc = Document.objects.create(
                            court=court, stem=stem, source_path=f,
                            doc_type=d.doc_type, n_pages=d.n_pages,
                            layout_ok=d.layout_ok, decision_date=d.decision_date,
                            docket_number=d.docket_number, parties=list(d.parties),
                            judges=d.judges, summary=_jsonable(d.summary),
                            syllabus=_jsonable(getattr(d, "syllabus", []) or []),
                        attorneys=getattr(d, "attorneys", "") or "",
                        criteria=getattr(d, "criteria", {}) or {},
                            headnotes=_jsonable(getattr(d, "headnotes", []) or []),
                            dropped=_jsonable(d.dropped),
                            trailer=_jsonable(d.trailer),
                            residual=_jsonable(getattr(d, "residual", []) or []),
                            warnings=warnings,
                            suspect=suspect, coverage=cov)
                        for fn in d.headmatter_footnotes:
                            Footnote.objects.create(
                                document=doc, opinion=None, order=0, label=fn.label,
                                paragraphs=[list(p) for p in fn.paragraphs])
                        for oi, op in enumerate(d.opinions):
                            o = Opinion.objects.create(
                                document=doc, order=oi, type=op.type,
                                author=op.author, caption=_jsonable(op.caption))
                            Block.objects.bulk_create([
                                Block(opinion=o, order=bi, kind=b.kind, text=b.text,
                                      page=b.page, payload=b.payload or {})
                                for bi, b in enumerate(op.blocks)])
                            for fi, fn in enumerate(op.footnotes):
                                Footnote.objects.create(
                                    document=doc, opinion=o, order=fi,
                                    label=fn.label,
                                    paragraphs=[list(p) for p in fn.paragraphs])
                        n_docs += 1
                self.stdout.write(f"  {cid}: {len(files)} docs")
        finally:
            if executor is not None:
                executor.shutdown()
        self.stdout.write(self.style.SUCCESS(
            f"ingested {n_docs} documents across {len(courts)} courts"))
        # The viewer's health chips come from output/manifest.js, not from the
        # DB directly, so an ingest that skips this leaves the homepage
        # describing the PREVIOUS extraction. (manifest.js is also rebuilt on
        # read when it is older than the DB — this keeps the file fresh for
        # anyone reading it without going through Django.)
        if not opts["no_manifest"]:
            from library.manifest import rebuild_manifest
            self.stdout.write(f"manifest: {rebuild_manifest()} documents")
