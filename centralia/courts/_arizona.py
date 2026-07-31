"""Shared layout mechanics for the Arizona courts (ariz / arizctapp).

Both the Supreme Court and the Court of Appeals print the same page furniture
and body style, so the mechanics live here once:

  * a top-margin running header on continuation pages (short caption + opinion
    identifier) — page furniture, detected by the gap before the body and
    dropped (the cover page keeps its title block);
  * ¶-numbered body paragraphs, re-grouped on the bold pilcrow markers because
    the generous line spacing otherwise splits every wrapped line;
  * bold standalone section headings ('OPINION', 'BACKGROUND', 'DISCUSSION',
    roman numerals, lettered subheads) tagged and merged across wraps;
  * page-aware headmatter so content spanning the cover and the first opinion
    page keeps document order, with underscore rules kept as horizontal lines.

What differs per court — the byline form and how opinion boundaries are found —
stays in ``ariz.py`` / ``arizctapp.py``.
"""

from __future__ import annotations

import re
from collections import Counter
from statistics import median

from ..models import Block

_ROMAN = {
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
}
_TAG = re.compile(r"<[^>]+>")
# Running-header identifiers that mark a (new) opinion. 'Opinion of the Court'
# is the lead opinion; a justice/judge byline header marks a separate writing.
_OPINION_HEADER = (
    "JUSTICE",
    "CHIEF JUSTICE",
    "VICE CHIEF JUSTICE",
    "JUDGE",
    "PRESIDING JUDGE",
    "CHIEF JUDGE",
)


def _strip_tags(s: str) -> str:
    return _TAG.sub("", s)


def _is_bold_only(text: str) -> bool:
    """True if the whole line is bold, allowing italic text inside it."""
    t = text.strip()
    t = t.replace("<em>", "").replace("</em>", "")
    # PDF font runs can produce adjacent strong spans on one visually uniform
    # heading (roman + italic case name + roman suffix).
    while "</strong><strong>" in t or "</strong> <strong>" in t:
        t = t.replace("</strong><strong>", "").replace("</strong> <strong>", " ")
    if not (t.startswith("<strong>") and t.endswith("</strong>")):
        return False
    return "<" not in t[len("<strong>") : -len("</strong>")]


def _is_heading_label(plain: str) -> bool:
    """True if a bold row starts a section heading: an all-caps title
    ('OPINION'/'BACKGROUND'), a roman numeral ('I.'), or a capital letter
    ('A.'). Continuation rows of a wrapped heading return False."""
    p = plain.strip()
    if not p:
        return False
    letters = [c for c in p if c.isalpha()]
    if letters and p == p.upper() and len(p) <= 50:
        return True
    first = p.split()[0].rstrip(".")
    if first in _ROMAN:
        return True
    if len(first) == 1 and first.isupper() and first.isalpha():
        return True
    return False


class ArizonaStyle:
    """Mixin providing the shared Arizona page mechanics. Combined with a court
    base (``StateSupreme`` / ``StateAppellate``) in the per-court class."""

    # Top-margin running-header band on pages 2+ (the cover keeps its title
    # block). The band is the run of tightly-spaced top lines (caption +
    # opinion identifier, which may wrap); it ends at the wider gap before the
    # body. Detected by that gap, not a fixed cutoff.
    header_top_max = 80.0
    # Header line-spacing is ~15pt; a byline or body line below the header sits
    # 21pt+ down. 18 separates the header's own lines from the first content
    # line (e.g. a byline printed directly under the header).
    header_gap_break = 18.0
    header_band_max = 96.0

    # ----------------------------------------------------------------- extract
    def extract(self, pdf_path: str):
        self._page_header = {}  # page_number -> opinion identifier text
        self._op_type = {}  # all_segments index -> opinion type
        self._header_dropped = []  # running-header lines, for the Removed box
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            op.blocks = self._regroup_body(op.blocks)
        return doc

    def _sweep_residual(self, doc, source_pages):
        """Surface the running header instead of discarding it.

        ``page_lines`` filters the header band off every continuation page but
        used to drop it on the floor, leaving the completeness sweep to decide
        what it was. The sweep only recognises a repeated line as furniture
        once it appears on enough pages, so a header belonging to a SHORT
        separate writing falls under the threshold and reads as lost content —
        'CHIEF JUSTICE TIMMER, Concurring' runs on two pages of
        state_v._fuster_melendez and is reported unplaced, while
        'JUSTICE BOLICK, Concurring' on five pages is not. Recording the band
        here makes it identified junk on every page, independent of how many
        times it happens to repeat (CLAUDE.md 3). Flushed before the sweep so
        it counts as placed."""
        extra = list(dict.fromkeys(getattr(self, "_header_dropped", []) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def correct_page_geometry(self, page) -> None:
        """Snap a glyph run drawn on its OWN offset baseline onto the row it
        belongs to.

        Arizona's PDFs occasionally emit a fragment on a baseline of its own:
        an 8pt hyphenation dash 3.8pt below its line (arizctapp
        judicial_watch p.3, splitting 'work-product'), or a stray '¶ 17.' cite
        set in a different face 4pt above the next line (ariz marner/haniffa
        p.13). Against a ~15pt body lead nothing that close is a line of its
        own — but left standing it splits the paragraph's segment, and the REAL
        line beside it is dropped along with it.

        Done here rather than in ``page_lines`` because the completeness audit
        reads the page through this hook too. Correcting it downstream leaves
        the audit comparing against the uncorrected split rows, so the repaired
        line matches nothing and still reads as lost. Measured against the
        page's own leading, since the two courts set different measures."""
        super().correct_page_geometry(page)
        rows = {}
        for char in page.chars:
            rows.setdefault(round(char.get("top", 0), 1), []).append(char)
        tops = sorted(rows)
        if len(tops) < 3:
            return
        gaps = [b - a for a, b in zip(tops, tops[1:]) if b - a > 5]
        if not gaps:
            return
        limit = median(gaps) * 0.45
        for above, below in zip(tops, tops[1:]):
            if below - above >= limit:
                continue
            # The smaller run is the stray; move it onto the larger row.
            src, dst = (
                (below, above)
                if len(rows[below]) <= len(rows[above])
                else (above, below)
            )
            anchor = rows[dst][0]
            delta = anchor["top"] - rows[src][0]["top"]
            for char in rows[src]:
                char["top"] += delta
                char["bottom"] += delta
                char["doctop"] = char.get("doctop", char["top"]) + delta
                if "y0" in char:
                    char["y0"] -= delta
                if "y1" in char:
                    char["y1"] -= delta

    def page_lines(self, page):
        lines = super().page_lines(page)
        if page.page_number <= 1 or not lines:
            return lines
        ordered = sorted(lines, key=lambda l: l.get("top", 0))
        if ordered[0].get("top", 0) > self.header_top_max:
            return lines  # no running header
        band = [ordered[0]]
        for prev, cur in zip(ordered, ordered[1:]):
            if cur.get("top", 0) >= self.header_band_max:
                break
            if cur.get("top", 0) - prev.get("top", 0) >= self.header_gap_break:
                break  # gap before the body
            band.append(cur)
        texts = [t for t in ((l.get("text") or "").strip() for l in band) if t]
        ids = [
            t
            for t in texts
            if t.startswith(_OPINION_HEADER)
            or t.lower().startswith("opinion of the court")
        ]
        hid = (
            ids[0]
            if ids
            else (texts[1] if len(texts) > 1 else (texts[0] if texts else ""))
        )
        if hid:
            self._page_header[page.page_number] = hid
        if getattr(self, "_header_dropped", None) is None:
            self._header_dropped = []
        self._header_dropped.extend(texts)
        band_ids = {id(l) for l in band}
        return [l for l in lines if id(l) not in band_ids]

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        t = self._op_type.get(op_start)
        if t:
            op.type = t
        return op

    def split_body_paragraphs(self, seg) -> list:
        """Split Arizona's numbered paragraphs before applying indentation.

        Division One often places a real ``¶N`` at the margin and starts the
        prose farther right on that same PDF line. The line's reported x0 is
        therefore the marker column, not the prose indent, so indentation alone
        cannot see the paragraph boundary. Division Two's raster markers are
        converted to the same line-leading form by ``arizctapp``.

        Requiring the digit to immediately follow the pilcrow distinguishes a
        structural marker (``¶10``) from a wrapped citation (``¶ 10``).
        """
        chunks = []
        current = []
        for line in seg:
            text = (line.get("text") or "").lstrip()
            numbered_start = (
                len(text) > 1 and text[0] == "¶" and text[1].isdigit()
            )
            if numbered_start and current:
                chunks.append(current)
                current = []
            current.append(line)
        if current:
            chunks.append(current)

        paragraphs = []
        for chunk in chunks:
            paragraphs.extend(super().split_body_paragraphs(chunk))
        return paragraphs

    # ----------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Style-preserving, page-aware headmatter.

        Each line keeps its inline markup (bold/italic/underline), relative font
        size, and alignment, so the rendered headmatter mirrors the printed
        hierarchy (large bold court name, italic posture lines, etc.). The
        section-separator rules — vector lines (``page1_rules``) or underscore
        text — are emitted as ``__DIVIDER__`` rows at their y-position. Ordering
        is by (page, top) so a page-2 line near the top never merges with a
        page-1 line at the same y."""
        page1_rules = page1_rules or []
        rows = []  # (page, top, x0, payload-dict)
        notice = []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                size, _font, _bold = self.line_meta(line)
                if self.notice_max_size is not None and size <= self.notice_max_size:
                    notice.append(t)
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                top = round(line["top"], 1)
                x0 = round(line["x0"], 1)
                if all(c in "_-—–" for c in t):
                    rows.append((pno, top, x0, {"divider": True}))
                    continue
                rows.append(
                    (
                        pno,
                        top,
                        x0,
                        {
                            "html": self.line_inline_text(line),
                            "size": size,
                            "align": self.line_alignment(line, 612),
                        },
                    )
                )
        for rt in page1_rules:  # vector section rules
            rows.append((1, round(rt, 1), -1.0, {"divider": True}))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))

        sizes = [p["size"] for _, _, _, p in rows if "size" in p]
        base = Counter(round(s) for s in sizes).most_common(1)[0][0] if sizes else 12
        summary = []
        for _pno, _top, _x0, p in rows:
            if p.get("divider"):
                summary.append("__DIVIDER__")
            else:
                summary.append(
                    {
                        "__hm__": True,
                        "html": p["html"],
                        "rel": round(p["size"] / base, 3),
                        "align": p["align"],
                    }
                )
        return {
            "court": self.court_label or self.court_id,
            "summary": summary,
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [" ".join(notice)] if notice else [],
        }

    # ------------------------------------------------ ¶-marker body re-grouping
    def _regroup_body(self, blocks) -> list:
        """Join wrapped body lines into whole paragraphs on the ¶ markers and
        merge wrapped heading rows. A new paragraph opens only at a bold ¶; a
        bold label row opens a heading; everything else continues the row
        above."""
        out: list = []
        cur = None
        cur_kind = None

        def flush():
            nonlocal cur, cur_kind
            if cur is not None:
                out.append(cur)
            cur, cur_kind = None, None

        for b in blocks:
            if b.kind not in ("p", "heading"):
                flush()
                out.append(b)
                continue
            plain = _strip_tags(b.text).strip()
            bold_only = _is_bold_only(b.text)
            if b.text.lstrip().startswith("<strong>¶"):
                flush()
                cur = Block(kind="p", text=b.text, page=b.page)
                cur_kind = "p"
            elif bold_only and _is_heading_label(plain):
                flush()
                cur = Block(kind="heading", text=b.text, page=b.page)
                cur_kind = "heading"
            elif cur_kind == "heading" and bold_only:
                cur.text += " " + b.text
            elif cur_kind == "heading":
                flush()
                cur = Block(kind="p", text=b.text, page=b.page)
                cur_kind = "p"
            elif cur_kind == "p":
                cur.text += " " + b.text
            else:
                flush()
                cur = Block(kind="p", text=b.text, page=b.page)
                cur_kind = "p"
        flush()
        return out
