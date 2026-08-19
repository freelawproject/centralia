"""The single section declaration. Renderers and the audit iterate THIS —
nothing else knows the section list, so adding a section field is two edits:
the Document field and one SectionSpec row (``check_spec`` enforces the
pairing).

``iter_text`` is the one structural walker over the typed variants — it
replaces the old audit's sentinel-sniffing `_chunk`.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterator

from . import model as m


@dataclass(frozen=True)
class SectionSpec:
    name: str                # display name
    attr: str                # Document attribute
    order: int               # canonical render order
    html: str                # renderer style: hm | flow | opinions | footnotes | removed
    casebody: str | None     # casebody XML element, or None (not exported)
    audited: bool            # contributes to the audit's kept haystack


SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec("headmatter", "headmatter", 10, "hm", "headmatter", True),
    # ENDMATTER — counsel a court prints BELOW its writings (ca3's order
    # form). Counsel set inside the headmatter now stays there, so this
    # section carries only the trailing rosters. It is named for where the
    # court put it and rendered in ONE consistent place, directly under the
    # headmatter: not every record of such a court has one, and letting it
    # float to the foot on some files and vanish on others made the document
    # read differently case to case. The casebody element stays `attorneys`.
    SectionSpec("endmatter", "attorneys", 15, "hm", "attorneys", True),
    SectionSpec("headnotes", "headnotes", 20, "flow", "headnotes", True),
    SectionSpec("syllabus", "syllabus", 30, "flow", "syllabus", True),
    SectionSpec("summary", "summary", 35, "flow", "summary", True),
    SectionSpec("headmatter footnotes", "headmatter_footnotes", 45,
                "footnotes", "headnotes-footnotes", True),
    SectionSpec("opinions", "opinions", 50, "opinions", "opinion", True),
    SectionSpec("signature", "signature", 60, "flow", None, True),
    SectionSpec("trailer", "trailer", 70, "flow", None, True),
    # `dropped` is deliberately NOT in the kept haystack: the audit matches it
    # against its own haystack so kept vs removed stay distinguishable.
    SectionSpec("removed", "dropped", 80, "removed", None, False),
    SectionSpec("residual", "residual", 90, "removed", None, True),
)


def check_spec() -> None:
    """Every spec row names a real Document field; every content-bearing
    Document field has a spec row. Run by `harness check`."""
    doc_fields = {f.name for f in fields(m.Document)}
    for spec in SECTIONS:
        if spec.attr not in doc_fields:
            raise AssertionError(f"SECTIONS row {spec.name!r} names missing "
                                 f"Document field {spec.attr!r}")
    covered = {s.attr for s in SECTIONS} | {"meta", "criteria", "warnings"}
    missing = doc_fields - covered
    if missing:
        raise AssertionError(f"Document fields not declared in SECTIONS: "
                             f"{sorted(missing)}")
    orders = [s.order for s in SECTIONS]
    if orders != sorted(orders):
        raise AssertionError("SECTIONS out of order")


def iter_text(item) -> Iterator[str]:
    """Every text string inside any model value — the audit's view of what
    the extraction kept. One walker; new variants extend the match here."""
    match item:
        case None:
            return
        case str():
            if item:
                yield item
        case list() | tuple():
            for x in item:
                yield from iter_text(x)
        case m.Paragraph() | m.Blockquote() | m.Heading() | m.ListItem():
            if item.text:
                yield item.text
        case m.TableBlock():
            for row in item.rows:
                for cell in row:
                    if cell:
                        yield cell
        case m.ImageBlock():
            return
        case m.HmLine():
            if item.text:
                yield item.text
        case m.CaptionBlock():
            yield from iter_text(item.left)
            yield from iter_text(item.right)
        case m.Rule() | m.Divider() | m.Gap():
            return
        case m.Footnote():
            if item.label:
                yield item.label
            yield from iter_text(item.blocks)
        case m.Opinion():
            if item.author:
                yield item.author
            yield from iter_text(item.caption)
            yield from iter_text(item.blocks)
            yield from iter_text(item.footnotes)
            yield from iter_text(item.signature)
        case m.Dropped() | m.Residual():
            if item.text:
                yield item.text
        case _:
            raise TypeError(f"iter_text: unhandled model type {type(item)!r}")


def section_text(doc: m.Document, spec: SectionSpec) -> Iterator[str]:
    yield from iter_text(getattr(doc, spec.attr))


def criteria_text(doc: m.Document) -> Iterator[str]:
    """Criteria values, for the criteria's OWN audit gate — deliberately not
    part of the kept haystack (a caption line absorbed into a scalar must not
    read as 'covered' while being invisible to the reviewer)."""
    c = doc.criteria
    for f in fields(c):
        v = getattr(c, f.name)
        if isinstance(v, str) and v:
            yield v
        elif isinstance(v, list):
            yield from (x for x in v if isinstance(x, str) and x)
