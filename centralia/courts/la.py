"""Supreme Court of Louisiana.

Two-part layout. Page 1 is a Clerk's news-release cover ('FOR IMMEDIATE NEWS
RELEASE ... FROM: CLERK OF SUPREME COURT OF LOUISIANA'), announcing the author in
a mixed-case 'BY McCallum, J.:' line and listing the docket, disposition, and any
separate writings ('Hughes, J., dissents ...'). The opinion proper begins on page
2 with a centered caption ('SUPREME COURT OF LOUISIANA / No. ... / parties / On
Writ of Certiorari ...') followed by the author byline.

That byline is an ALL-CAPS surname and an *abbreviated* title — 'MCCALLUM, J.',
'WEIMER, Chief Justice*', 'PENZATO, Justice Pro Tempore1' — often carrying a
footnote mark ('*' or a superscript digit) in place of the period. Two things
defeat the base byline parser here: the title is the abbreviated 'J.' rather than
the spelled-out 'Justice'/'Judge', and the bold face is encoded as an embedded
subset font ('CIDFont+F2', no 'Bold' in the name) so the base bold test misses
it. The override below recognises the byline structurally instead. The mixed-case
cover lines ('McCallum', 'Hughes') fail the ALL-CAPS name test, so the opinion
correctly starts at the page-2 byline and the cover + caption stay in headmatter.

Printed on legal-size paper (height 1008): the body and a half-width footnote
block (12pt text under an 8pt superscript number, set off by a thin left-aligned
rule) run down to ~937, with the centered page number lower still at ~945. The
default bottom margin would chop the lower quarter of every page, so it is raised
to keep all content while cutting the page number.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name


# Abbreviated Louisiana judicial titles that open an opinion byline. 'Justice Pro
# Tempore' and 'Chief Justice' precede the bare 'Justice'/'J.' so the longest
# match is tested first (startswith on a tuple matches any, but order documents
# intent).
_LA_TITLE_STARTS = (
    "Chief Justice",
    "Justice Pro Tempore",
    "Justice",
    "Judge",
    "C. J.",
    "C.J.",
    "J.",
    "A.H.J.",
)


class LouisianaSupreme(StateSupreme):
    court_id = "la"
    court_label = "Supreme Court of Louisiana."
    # Legal-size page: keep body + bottom footnotes (down to ~937), cut the
    # centered page number (~945).
    margin_bottom = 940.0

    def find_authors(self, all_segments) -> list:
        # Newer disciplinary opinions announce a title-case author on the
        # news-release cover (``BY Guidry, J.:``) and repeat that same
        # title-case byline on the opinion page.  Record the announced name so
        # only that exact title-case surname can pass the otherwise all-caps
        # Louisiana grammar.
        self._la_announced_names = set()
        for _p, seg, _kind in all_segments:
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip()
            if text.startswith("BY ") and "," in text:
                self._la_announced_names.add(text[3:].split(",", 1)[0].strip())
        starts = super().find_authors(all_segments)
        # A news-release cover can say ``PER CURIAM:`` before repeating the
        # actual per-curiam byline on the opinion page.  When both exist, the
        # cover announcement is metadata, not a first opinion.
        per = [
            i
            for i in starts
            if self._la_per_curiam(
                self.line_plain_text(all_segments[i][1][0]).strip()
            )
        ]
        if len(per) >= 2:
            later_pages = {all_segments[i][0] for i in per if all_segments[i][0] > 1}
            if later_pages:
                starts = [
                    i
                    for i in starts
                    if not (i in per and all_segments[i][0] == 1)
                ]
        return starts

    def _byline_split(self, line):
        """Louisiana byline: ALL-CAPS surname, comma, an abbreviated judicial
        title ('J.', 'Chief Justice', 'Justice Pro Tempore'), optionally trailed
        by a footnote mark ('*' or a superscript digit). The byline stands alone
        (the opinion body begins on the next line), so the body half is always
        empty. Recognised structurally — the bold face is a subset font the base
        'Bold'-in-fontname test cannot see, and the title is abbreviated.

        The byline is kept EXACTLY as printed, footnote mark included ('COLE,
        J.*', 'CRAIN, J.1'). The mark is not decoration: it anchors the
        assignment footnote at the page foot ('* Judge Allison H. Penzato …
        appointed Justice pro tempore'), and cleaning it off silently dropped
        the only printed link to that footnote — the byline row then matched
        nothing in the output and read as lost content."""
        text = self.line_plain_text(line).strip()
        if self._la_per_curiam(text):
            return text, ""
        parsed = self._la_byline(text)
        if parsed is None:
            return None
        return text, ""

    def _la_byline(self, text: str):
        """Parse a Louisiana author byline; return (cleaned, name, title) or None.
        ``cleaned`` is the byline with any trailing footnote mark stripped (so the
        stored author reads 'MCCALLUM, J.', not 'MCCALLUM, J.*'); a separate
        writing keeps its disposition clause so the kind can be read from it. Two
        comma placements occur: 'GRIFFIN, J., ...' (after the surname) and
        'GRIFFIN J., ...' (after the abbreviated title attached to the surname)."""
        text = (text or "").strip()
        if not text or "," not in text:
            return None
        head, after = text.split(",", 1)
        head, after = head.strip(), after.lstrip()
        cleaned = text.rstrip("*0123456789 ").rstrip()
        # Form A: 'SURNAME, <title>[, disposition]'.
        if _is_byline_name(head) or head in getattr(self, "_la_announced_names", set()):
            core = after.rstrip("*0123456789 ").rstrip()
            if core.startswith(_LA_TITLE_STARTS):
                return cleaned, head, core.split(",")[0].strip()
        # Form B: the abbreviated title rides with the surname ('GRIFFIN J.,')
        # and the comma opens the disposition clause.
        toks = head.split()
        if len(toks) >= 2:
            name = " ".join(toks[:-1])
            tcore = toks[-1].replace(".", "").rstrip("*0123456789").upper()
            if _is_byline_name(name) and tcore in ("J", "CJ", "PJ"):
                return cleaned, name, toks[-1]
        return None

    def parse_author_line(self, text):
        """Recover (name, title, kind) for a Louisiana byline the base regex
        grammar misses (abbreviated 'J.' title, footnote marks). The kind is read
        from the disposition clause of a separate writing so the opinion type is
        classified correctly; the bare main byline yields kind=None (majority)."""
        base = super().parse_author_line(text)
        if base is not None:
            return base
        if self._la_per_curiam(text):
            return "PER CURIAM", "per curiam", None
        parsed = self._la_byline(text)
        if parsed is None:
            return None
        byline, name, title = parsed
        low = byline.lower()
        kind = None
        if "concur" in low and "dissent" in low:
            kind = "concurring in part and dissenting in part"
        elif "dissent" in low:
            kind = "dissenting"
        elif "concur" in low and "result" in low:
            kind = "concurring in the result"
        elif "concur" in low:
            kind = "concurring"
        return name, title, kind

    @staticmethod
    def _la_per_curiam(text: str) -> bool:
        t = (text or "").strip().rstrip("0123456789*†‡:. ")
        return " ".join(t.split()).upper() == "PER CURIAM"

    # ------------------------------------------------------------- footnotes
    def detect_footnote_label(self, line):
        """The assignment footnote is marked with a '*' set at the SAME size as
        its 12pt text, not as a raised superscript, so the base 'smaller char'
        test cannot see it and the footnote came back labelled '?'. Read the
        leading star run as the label."""
        text = (line.get("text") or "").lstrip()
        if text.startswith("*"):
            return text[: len(text) - len(text.lstrip("*"))]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the leading star marker off the footnote text — it is the
        label, which the renderer draws in its own column."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and set(label) == {"*"}:
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            if stripped.startswith(label):
                fn.paragraphs[0] = (tag, stripped[len(label) :].lstrip())
        return fn
