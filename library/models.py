"""Database models mirroring the extractor's ``ExtractedDocument`` contract.

The ``restatement`` package extracts a court PDF into an in-memory
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
    # Layout-preserved / styled headmatter rows, official syllabus, dropped
    # furniture, trailing matter — kept verbatim as the extractor returned them.
    summary = models.JSONField(default=list, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    dropped = models.JSONField(default=list, blank=True)
    trailer = models.JSONField(default=list, blank=True)
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
