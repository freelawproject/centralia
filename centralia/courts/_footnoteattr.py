"""Give a footnote to the writing whose body carries its mark.

Page ownership decides which writing a page's footnote zone belongs to
(``base.extract`` splits the pages at each writing's FIRST segment). That is
right whenever a writing starts at the top of a page, and wrong whenever one
starts in the middle of one: the notes printed at the foot of that page were
called by the writing ABOVE the split, and they follow the page to the writing
below it.

Two courts show the same failure from opposite ends:

  * ``pacommwct`` closes every opinion with a conformed signature and then
    prints the ORDER on its own page. The signature parses as a byline, so the
    order writing opens on the majority's LAST page and takes that page's
    footnote zone with it — the majority's final note, in 8 of 30 documents
    (``city_of_philadelphia`` 18 of 18, ``carlino`` 10 and 11).
  * ``ark`` runs a concurrence's opening sentence inline with its byline and
    starts the dissent partway down the concurrence's last page; the
    concurrence's own notes were delivered under the dissent
    (``rodney_bunch`` 1 and 2, ``state_v._ramirez`` 3).

The mark settles it without any geometry: ``line_inline_text`` has already
wrapped the raised label in ``<footnotemark>`` wherever the body calls the
note. A writing that holds a note it never calls, when exactly one other
writing calls it and does not already hold one by that label, is holding
someone else's footnote.

Nothing moves on a guess: the label has to be claimed by exactly ONE other
writing, and a writing that calls the note itself always keeps it.
"""

from __future__ import annotations

from ..base import BaseExtractor


def _label_of(footnote) -> str:
    return str(getattr(footnote, "label", "") or "").strip()


def _unlabelled(footnote) -> bool:
    return _label_of(footnote) in ("", "?")


def _insert_in_order(notes: list, footnote) -> None:
    """Keep a writing's notes in printed order — numerically where the court
    numbers them, appended otherwise."""
    label = _label_of(footnote).rstrip(".")
    if label.isdigit():
        value = int(label)
        for i, other in enumerate(notes):
            text = _label_of(other).rstrip(".")
            if text.isdigit() and int(text) > value:
                notes.insert(i, footnote)
                return
    notes.append(footnote)


def reattribute_footnotes_by_mark(doc) -> int:
    """Move mis-attributed footnotes between writings. Returns how many moved."""
    ops = list(doc.opinions)
    if len(ops) < 2:
        return 0
    marks = []
    for op in ops:
        called: set = set()
        for block in op.blocks:
            called.update(BaseExtractor._footnote_marks(block.text or ""))
        marks.append(called)
    held = [{_label_of(fn) for fn in op.footnotes} for op in ops]

    moved = 0
    for i, src in enumerate(ops):
        if not src.footnotes:
            continue
        keep, plan = [], []
        for fn in src.footnotes:
            label = _label_of(fn)
            if not label or label == "?" or label in marks[i]:
                keep.append(fn)
                continue
            claimants = [
                j
                for j in range(len(ops))
                if j != i and label in marks[j] and label not in held[j]
            ]
            if len(claimants) != 1:
                keep.append(fn)
                continue
            plan.append((claimants[0], fn))
        if not plan:
            continue

        # An UNLABELLED note at the head of the list is the tail of a footnote
        # that began on the previous page — pacommwct even prints '(Footnote
        # continued on next page…)' at the break. It carried over with the
        # page, so it travels with the notes that are going back and rejoins
        # the note it continues. Only from a writing that calls no note of its
        # own, so a writing with footnotes of its own is never unstitched.
        target = ops[plan[0][0]]
        if not marks[i] and target.footnotes:
            while keep and _unlabelled(keep[0]):
                tail = keep.pop(0)
                last = target.footnotes[-1]
                last.paragraphs = list(last.paragraphs) + list(tail.paragraphs)
                moved += 1

        src.footnotes = keep
        for j, fn in plan:
            _insert_in_order(ops[j].footnotes, fn)
            held[j].add(_label_of(fn))
            moved += 1

    if moved:
        # The two footnote warnings were raised while the notes were still on
        # the wrong writing; re-state them against the corrected document, or a
        # fixed file keeps reporting itself broken.
        doc.warnings[:] = [
            w
            for w in doc.warnings
            if not w.startswith("footnote referenced but never built")
            and not w.startswith("footnote sequence breaks")
        ]
        BaseExtractor._warn_orphan_footnote_refs(doc)
        BaseExtractor._warn_footnote_gaps(doc)
    return moved
