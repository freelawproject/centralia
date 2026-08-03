"""Fill in Document.coverage from an ecosystem-audit results.json.

``ingest --no-audit`` is far faster because it skips ``audit_coverage`` per
document, but it leaves every ``coverage`` at 0.0, which reads in the viewer as
total failure rather than "not measured". The ecosystem audit already computes
covered/total for exactly the same documents, so the number can be copied
across instead of being computed a second time.

    uv run python manage.py backfill_coverage
    uv run python manage.py backfill_coverage --results output/ecosystem-audit/results.json
"""

import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Copy per-document coverage from the ecosystem audit into the DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--results", default="output/ecosystem-audit/results.json"
        )
        parser.add_argument("courts", nargs="*", help="court ids (default: all)")

    def handle(self, *args, **opts):
        from library.models import Document

        path = Path(opts["results"])
        if not path.exists():
            self.stderr.write(f"no results file at {path}")
            return
        data = json.loads(path.read_text(encoding="utf-8"))

        wanted = set(opts["courts"]) or None
        # (court, stem) -> coverage %, mirroring how ingest derives it.
        cov = {}
        for court, rows in data.get("files", {}).items():
            if wanted and court not in wanted:
                continue
            for r in rows:
                total = r.get("total_lines") or 0
                covered = r.get("covered_lines") or 0
                stem = os.path.splitext(r.get("file", ""))[0]
                cov[(court, stem)] = (
                    round(100 * covered / total, 1) if total else 100.0
                )

        qs = Document.objects.select_related("court")
        if wanted:
            qs = qs.filter(court__court_id__in=wanted)
        updated, missed = [], 0
        for doc in qs:
            value = cov.get((doc.court.court_id, doc.stem))
            if value is None:
                missed += 1
                continue
            if doc.coverage != value:
                doc.coverage = value
                updated.append(doc)
        Document.objects.bulk_update(updated, ["coverage"], batch_size=500)
        self.stdout.write(
            f"coverage set on {len(updated)} documents "
            f"({missed} had no audit row)"
        )
