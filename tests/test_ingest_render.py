"""The ingest-facing render: what a consumer stores, pinned corpus-free.

`render_opinion_ingest` and the note-carrying `html_inline` exist for one
consumer story — CourtListener stores the blob and draws it with its own
site styles — so what they promise is pinned here on hand-built model
objects: no review furniture, layout stated inline, and footnotes that are
real anchors with nowhere-links ruled out. None of it needs the corpus.
"""

from __future__ import annotations

import centralia
from centralia import model as m
from centralia.render.html import render_opinion_ingest
from centralia.render.facsimile import render_hm_inline
from centralia.render.inline import footnote_slug, inline_to_html, mark_slugs


def _writing() -> m.Opinion:
    return m.Opinion(
        type="dissent",
        author="<strong>LEE</strong>, J., dissenting:",
        blocks=[
            m.Paragraph(text="I dissent.<footnotemark>1</footnotemark>",
                        prov=m.Prov(1)),
            m.Paragraph(text="See <em>Roe</em>.<footnotemark>*</footnotemark>",
                        prov=m.Prov(1)),
        ],
        footnotes=[
            m.Footnote(label="1",
                       blocks=[m.Paragraph(text="A note.", prov=m.Prov(1))]),
            m.Footnote(label="*",
                       blocks=[m.Paragraph(text="Star note.", prov=m.Prov(1))]),
            m.Footnote(label="2",
                       blocks=[m.Paragraph(text="Orphan.", prov=m.Prov(1))]),
        ],
    )


def test_no_review_furniture():
    """The chip is the review page's; an ingest prints its own heading."""
    html = render_opinion_ingest(_writing(), ns="o1")
    assert 'class="chip"' not in html
    assert html.startswith('<div class="opinion">')


def test_footnotes_are_wired_and_namespaced():
    """Mark -> note and note -> mark, under the writing's own namespace."""
    html = render_opinion_ingest(_writing(), ns="o2")
    assert '<sup class="fnmark" id="ref-o2-1"><a href="#fn-o2-1">1</a>' in html
    assert '<div class="fn" id="fn-o2-1"><a class="lbl" href="#ref-o2-1">1</a>' in html


def test_symbol_labels_get_stable_slugs():
    """'*' cannot appear in an id as itself; both ends must still agree."""
    assert footnote_slug("*") == "u42"
    assert footnote_slug("7") == "7"
    html = render_opinion_ingest(_writing(), ns="o1")
    assert 'id="ref-o1-u42"' in html and 'id="fn-o1-u42"' in html


def test_orphan_note_keeps_a_plain_label():
    """A note whose mark was never read must not link to nowhere."""
    html = render_opinion_ingest(_writing(), ns="o1")
    assert '<div class="fn" id="fn-o1-2"><span class="lbl">2</span>' in html
    assert 'href="#ref-o1-2"' not in html


def test_two_writings_cannot_collide():
    """The namespace is the writing's order; same labels, different ids."""
    one = render_opinion_ingest(_writing(), ns="o1")
    two = render_opinion_ingest(_writing(), ns="o2")
    assert 'id="fn-o1-1"' in one and 'id="fn-o2-1"' in two
    assert 'id="fn-o2-1"' not in one


def test_announcement_dedupe_still_applies():
    """The cover's announcement row is not repeated as the byline."""
    op = _writing()
    sig = "".join("LEE, J., dissenting:".split())
    html = render_opinion_ingest(op, ns="o1", hm_sig=sig)
    assert '<div class="byline">' not in html


def test_caption_renders_inline_not_in_classes():
    """A consolidated writing's own caption travels without our CSS."""
    op = _writing()
    op.caption = [m.HmLine(text="No. 22-1234", prov=m.Prov(1),
                           align=m.Align.CENTER)]
    html = render_opinion_ingest(op, ns="o1")
    assert 'class="hmrow' not in html
    assert "text-align:center" in html


def test_hm_inline_converts_the_vocabulary():
    """html_inline used to ship <footnotemark> raw; it is markup now."""
    rows = [m.HmLine(text="Substituted<footnotemark>*</footnotemark>",
                     prov=m.Prov(1))]
    html = render_hm_inline(rows, fn_ns="hm")
    assert "<footnotemark>" not in html
    assert 'id="ref-hm-u42"' in html
    plain = render_hm_inline(rows)
    assert "<footnotemark>" not in plain
    assert '<sup class="fnmark">*</sup>' in plain


def test_mark_slugs_reads_the_model_vocabulary():
    got = mark_slugs(["a<footnotemark>3</footnotemark>",
                      "b<footnotemark>*</footnotemark>", ""])
    assert got == {"3", "u42"}


def test_inline_without_namespace_is_unchanged():
    """The review page's marks stay inert; only an ingest asks for anchors."""
    s = inline_to_html("x<footnotemark>4</footnotemark>")
    assert s == 'x<sup class="fnmark">4</sup>'


def test_version_is_the_installed_version():
    """The literal said 0.0.3 while 0.0.4 shipped; it must never lie again."""
    assert centralia.__version__ not in ("", "0.0.3")
