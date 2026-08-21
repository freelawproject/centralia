"""Database models mirroring the extractor's ``ExtractedDocument`` contract.

The ``centralia`` package extracts a court PDF into an in-memory
``ExtractedDocument`` (court/headmatter/opinions/footnotes). These models are the
persisted form of that contract so the corpus can be browsed, searched, and
reviewed from the web app. The ``ingest`` management command runs the extractors
and populates these tables.
"""

from __future__ import annotations

from django.db import models


class Court(models.Model):
    """A court id (e.g. 'ariz', 'ca5') and its printed label."""
    court_id = models.SlugField(primary_key=True, max_length=32)
    label = models.CharField(max_length=255, blank=True)
    # Review workflow: notes (from the viewer) and Claude-completed flag.
    notes = models.TextField(blank=True)
    claude_done = models.BooleanField(default=False)

    class Meta:
        ordering = ["court_id"]

    def __str__(self):
        return self.court_id

    @property
    def suspect_count(self):
        return self.documents.filter(suspect=True).count()


class Document(models.Model):
    """One extracted PDF."""
    court = models.ForeignKey(Court, on_delete=models.CASCADE,
                              related_name="documents")
    stem = models.CharField(max_length=255)              # filename without .pdf
    source_path = models.CharField(max_length=512, blank=True)
    doc_type = models.CharField(max_length=32, default="unknown")
    n_pages = models.PositiveIntegerField(default=0)
    layout_ok = models.BooleanField(default=True)

    # Headmatter criteria
    decision_date = models.CharField(max_length=64, blank=True, null=True)
    docket_number = models.CharField(max_length=128, blank=True, null=True)
    parties = models.JSONField(default=list, blank=True)
    judges = models.CharField(max_length=512, blank=True, null=True)
    # Structured headmatter dissection (docket / caption / prior history /
    # panel / publication), shown collapsed in the review detail page.
    criteria = models.JSONField(default=dict, blank=True)
    # Layout-preserved / styled headmatter rows, official syllabus, dropped
    # furniture, trailing matter — kept verbatim as the extractor returned them.
    summary = models.JSONField(default=list, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    attorneys = models.TextField(blank=True, default="")
    headnotes = models.JSONField(default=list, blank=True)
    dropped = models.JSONField(default=list, blank=True)
    trailer = models.JSONField(default=list, blank=True)
    # Completeness safety net: source lines placed in no section, tagged
    # content/furniture. Surfaced in the Removed box. See ExtractedDocument.
    residual = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)

    # Review/diagnostic
    suspect = models.BooleanField(default=False)          # all-headmatter, >2pp
    coverage = models.FloatField(default=0.0)             # audit % (0-100)

    class Meta:
        ordering = ["court", "stem"]
        unique_together = [("court", "stem")]
        indexes = [models.Index(fields=["court", "stem"])]

    def __str__(self):
        return f"{self.court_id}/{self.stem}"


class Opinion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE,
                                 related_name="opinions")
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=64, default="majority")
    author = models.CharField(max_length=255, blank=True)
    # Exact printed byline/announcement or repeated per-writing caption.
    # Kept apart from normalized ``author`` so downstream matching sees a
    # stable concise value while the viewer preserves what the court printed.
    caption = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["document", "order"]

    def __str__(self):
        return f"{self.document} · {self.type} ({self.author})"


class Block(models.Model):
    """A body block: p | blockquote | heading | image | table."""
    opinion = models.ForeignKey(Opinion, on_delete=models.CASCADE,
                                related_name="blocks")
    order = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=16, default="p")
    text = models.TextField(blank=True)                  # inline-marked-up html
    page = models.PositiveIntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)  # image/table data

    class Meta:
        ordering = ["opinion", "order"]


class Footnote(models.Model):
    """A footnote, attached to an opinion or (when opinion is null) headmatter."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE,
                                 related_name="footnotes")
    opinion = models.ForeignKey(Opinion, on_delete=models.CASCADE,
                                related_name="footnotes", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=16, blank=True)
    # Each paragraph is (tag, text); stored as a list of [tag, text].
    paragraphs = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["document", "opinion", "order"]


class GroundTruth(models.Model):
    """Hand-verified truth about a source PDF — never written by the pipeline.

    Deliberately NOT a ForeignKey to ``Document``. ``manage.py ingest`` does a
    full refresh per court (``court.documents.all().delete()``), so anything
    hanging off a Document row is destroyed on the next run; and the truth is a
    fact about the PDF, not about a database row, so it has to outlive a
    rename, a wiped database or a fresh clone. The natural key is the same one
    the corpus uses everywhere else — court id plus file stem.

    ``kind`` leaves room for more than footnotes (opinion count, byline,
    disposition) without another table; ``value`` holds whatever that kind
    means — for 'footnotes' it is the list of labels in document order,
    headmatter notes first, and an empty list is a real answer meaning the
    document prints none.
    """

    court_id = models.CharField(max_length=32, db_index=True)
    stem = models.CharField(max_length=255, db_index=True)
    kind = models.CharField(max_length=32, default="footnotes", db_index=True)
    value = models.JSONField(default=list, blank=True)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("court_id", "stem", "kind")]
        ordering = ["court_id", "stem", "kind"]
        verbose_name_plural = "ground truth"

    def __str__(self):
        return f"{self.court_id}/{self.stem} [{self.kind}] = {self.value}"
