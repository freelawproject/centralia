"""A/B comparison against a frozen baseline.

Both sides are reduced to the same neutral summary shape (the baseline record
schema from `_freeze_old.py`); the new pipeline gets an adapter producing that
shape from a typed Document (Phase 6). Comparison happens on NORMALIZED text
(centralia.audit.norm), so representation differences can't masquerade as
content differences.

Every diff is bucketed and the triage is persisted, so reviewing it is
resumable:
    regression          — new lost content/structure the old system had
    intentional-fix     — a known, documented improvement
    representation-only — same content, different shape
Buckets start as 'untriaged'; `triage.json` per court records human verdicts.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.audit import norm  # noqa: E402


@dataclass
class FileDiff:
    stem: str
    kind: str          # opinion-count | section-words | footnote-labels | doc-type
    detail: str
    bucket: str = "untriaged"


@dataclass
class CourtDiff:
    court: str
    diffs: list[FileDiff] = field(default_factory=list)
    files_compared: int = 0

    @property
    def clean(self) -> bool:
        return not self.diffs


# Sections excluded from the strict word-mass gate: criteria growth is the
# INTENTIONAL fix (old system extracted ~none; it has its own gate), and the
# Removed box is surfaced junk whose representation legitimately changed —
# content loss is caught by the residual gate and the body/headmatter mass.
_MASS_EXEMPT = {"criteria", "dropped"}


# The new system deliberately re-homes counsel and syllabus out of the old
# headmatter dump; movement WITHIN the front matter is attribution by design.
# Movement between FRONT and BODY is the Connecticut failure and stays hot.
_FRONT = {"headmatter", "attorneys", "syllabus", "headnotes"}


def _section_words(rec: dict) -> dict[str, int]:
    out = {"front": 0}
    for name, chunks in rec.get("sections", {}).items():
        if name in _MASS_EXEMPT:
            continue
        mass = sum(len(norm(c)) for c in chunks)  # normalized char mass
        if name in _FRONT:
            out["front"] += mass
            continue
        out[name] = mass
    body = 0
    for op in rec.get("opinions", []):
        body += sum(len(norm(t)) for t in op.get("blocks_text", []))
        body += sum(len(norm(t)) for t in op.get("footnotes_text", []))
        body += sum(len(norm(t)) for t in op.get("signature_text", []))
    # Signature vs body is ATTRIBUTION (the DATED line moved home), not
    # content: one bucket.
    body += out.pop("signature", 0)
    out["body"] = body
    return out


def _labels(rec: dict) -> list[str]:
    labels = list(rec.get("headmatter_footnote_labels", []))
    for op in rec.get("opinions", []):
        labels.extend(op.get("footnote_labels", []))
    return labels


def compare_records(stem: str, old: dict, new: dict,
                    word_tolerance: float = 0.02) -> list[FileDiff]:
    """Compare two neutral records. Tolerance is fractional on normalized
    character mass per section — the Connecticut gate: misfiled content moves
    mass BETWEEN sections even when total coverage stays perfect."""
    diffs: list[FileDiff] = []
    if old.get("doc_type") != new.get("doc_type"):
        diffs.append(FileDiff(stem, "doc-type",
                              f"{old.get('doc_type')} -> {new.get('doc_type')}"))
    n_old, n_new = len(old.get("opinions", [])), len(new.get("opinions", []))
    if n_old != n_new:
        diffs.append(FileDiff(stem, "opinion-count", f"{n_old} -> {n_new}"))
    ow, nw = _section_words(old), _section_words(new)
    for name in sorted(set(ow) | set(nw)):
        a, b = ow.get(name, 0), nw.get(name, 0)
        if a == b:
            continue
        base = max(a, b)
        # Absolute floor: a row the new system keeps as printed while the old
        # relocated it into a scalar (docket/citation, ~10–20 normalized
        # chars) is representation, not content movement.
        if base and abs(a - b) / base > word_tolerance and abs(a - b) > 40:
            diffs.append(FileDiff(stem, "section-words", f"{name}: {a} -> {b}"))
    la, lb = _labels(old), _labels(new)
    if la != lb:
        diffs.append(FileDiff(stem, "footnote-labels", f"{la} -> {lb}"))
    return diffs


def new_record(result) -> dict:
    """A new-pipeline ExtractionResult reduced to the neutral baseline record
    shape, via the SECTION_SPEC walker."""
    from centralia.sections import SECTIONS, criteria_text, section_text

    doc = result.document
    sections = {}
    for spec in SECTIONS:
        if spec.attr in ("opinions", "headmatter_footnotes", "residual"):
            continue
        name = {"headmatter": "headmatter", "removed": "dropped"}.get(
            spec.name, spec.attr)
        sections[name] = list(section_text(doc, spec))
    sections["criteria"] = list(criteria_text(doc))
    ops = []
    for op in doc.opinions:
        blocks_text = [t for b in op.blocks
                       for t in ([b.text] if hasattr(b, "text") and b.text else [])]
        ops.append({
            "type": op.type,
            "author": op.author,
            "words": sum(len(t.split()) for t in blocks_text),
            "blocks_text": blocks_text,
            "footnote_labels": [fn.label for fn in op.footnotes],
            "footnotes_text": [t for fn in op.footnotes for b in fn.blocks
                               for t in ([b.text] if getattr(b, "text", "") else [])],
            "caption_text": [],
            "signature_text": [getattr(b, "text", "") for b in op.signature
                               if getattr(b, "text", "")],
        })
    return {
        "doc_type": str(doc.meta.doc_type),
        "n_pages": doc.meta.n_pages,
        "non_digital": doc.meta.doc_type == "scan",
        "sections": sections,
        "headmatter_footnote_labels": [fn.label for fn in doc.headmatter_footnotes],
        "headmatter_footnotes_text": [t for fn in doc.headmatter_footnotes
                                      for b in fn.blocks
                                      for t in ([b.text] if getattr(b, "text", "") else [])],
        "opinions": ops,
        "residual": [{"page": r.prov.page, "kind": r.kind, "text": r.text}
                     for r in doc.residual],
        "warnings": list(doc.warnings),
    }


def compare_courts(court: str, old_files: dict, new_files: dict) -> CourtDiff:
    result = CourtDiff(court=court)
    for stem in sorted(set(old_files) | set(new_files)):
        if stem not in new_files:
            result.diffs.append(FileDiff(stem, "missing", "not extracted by new"))
            continue
        if stem not in old_files:
            continue  # new corpus file since freeze; nothing to compare
        result.files_compared += 1
        result.diffs.extend(compare_records(stem, old_files[stem], new_files[stem]))
    return result
