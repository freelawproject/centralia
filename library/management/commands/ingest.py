"""Run the per-court extractors over the asset corpus and load the results
into the database.

  uv run python manage.py ingest               # all courts
  uv run python manage.py ingest ariz ohio     # specific courts
  uv run python manage.py ingest --no-audit    # skip coverage (faster)
"""

import glob
import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from restatement.registry import get_extractor

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

    def handle(self, *args, **opts):
        from library.models import (Block, Court, Document, Footnote, Opinion)
        do_audit = not opts["no_audit"]
        if do_audit:
            from restatement.audit import audit_coverage

        courts = opts["courts"] or sorted(
            d for d in os.listdir(ASSETS) if os.path.isdir(f"{ASSETS}/{d}"))
        notes, done = _load_notes()
        n_docs = 0
        for cid in courts:
            files = sorted(glob.glob(f"{ASSETS}/{cid}/*.pdf"))
            if not files:
                continue
            ex = get_extractor(cid)
            label = getattr(ex, "court_label", "") or cid
            court, _ = Court.objects.update_or_create(
                court_id=cid,
                defaults={"label": label, "notes": notes.get(cid, ""),
                          "claude_done": bool(done.get(cid))})
            with transaction.atomic():
                court.documents.all().delete()       # full refresh per court
                for f in files:
                    stem = os.path.basename(f)[:-4]
                    try:
                        d = ex.extract(f)
                    except Exception as e:
                        Document.objects.create(
                            court=court, stem=stem, source_path=f,
                            doc_type="error", warnings=[str(e)], suspect=True)
                        n_docs += 1
                        continue
                    has_body = any(op.blocks for op in d.opinions)
                    cov = 0.0
                    if do_audit:
                        try:
                            r = audit_coverage(d, f)
                            cov = round(100 * r.covered / r.total, 1) if r.total else 100.0
                        except Exception:
                            cov = 0.0
                    doc = Document.objects.create(
                        court=court, stem=stem, source_path=f,
                        doc_type=d.doc_type, n_pages=d.n_pages,
                        layout_ok=d.layout_ok, decision_date=d.decision_date,
                        docket_number=d.docket_number, parties=list(d.parties),
                        judges=d.judges, summary=list(d.summary),
                        syllabus=list(getattr(d, "syllabus", []) or []),
                        dropped=list(d.dropped), trailer=list(d.trailer),
                        warnings=list(d.warnings),
                        suspect=(not has_body) and d.n_pages > 2, coverage=cov)
                    for fn in d.headmatter_footnotes:
                        Footnote.objects.create(
                            document=doc, opinion=None, order=0, label=fn.label,
                            paragraphs=[list(p) for p in fn.paragraphs])
                    for oi, op in enumerate(d.opinions):
                        o = Opinion.objects.create(
                            document=doc, order=oi, type=op.type, author=op.author)
                        Block.objects.bulk_create([
                            Block(opinion=o, order=bi, kind=b.kind, text=b.text,
                                  page=b.page, payload=b.payload or {})
                            for bi, b in enumerate(op.blocks)])
                        for fi, fn in enumerate(op.footnotes):
                            Footnote.objects.create(
                                document=doc, opinion=o, order=fi, label=fn.label,
                                paragraphs=[list(p) for p in fn.paragraphs])
                    n_docs += 1
            self.stdout.write(f"  {cid}: {len(files)} docs")
        self.stdout.write(self.style.SUCCESS(
            f"ingested {n_docs} documents across {len(courts)} courts"))
