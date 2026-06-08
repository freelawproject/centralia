"""Shared base for the U.S. district courts.

A district-court filing is one ruling by one judge, not the multi-opinion
byline-at-start shape of an appellate decision. So the model differs:

  * The author is taken from the **signature block** at the end — the line
    above a 'United States District Judge' / 'Magistrate Judge' title (the most
    universal signal across districts), or, failing that, from a 'Present: The
    Honorable NAME, ... JUDGE' minute-order line, a 'THE HONORABLE NAME, U.S.D.J.'
    heading, a caption 'Judge NAME' line, or a 'NAME, J.' byline.
  * The opinion begins at the document-type heading ('MEMORANDUM OPINION AND
    ORDER' / 'ORDER' / 'REPORT AND RECOMMENDATION' / ...) — the caption above it
    is headmatter — or, if there is no heading, at the first body paragraph.
  * The whole ruling is one opinion (docket orders included, per the project's
    'treat orders as opinions' rule).

The CM/ECF header band ('Case 1:23-cv-00358 Document #: 111 Filed: ... Page 1
of 16 PageID #:...') sits in the top margin and is already excluded by
``margin_top``; per-district subclasses add any court-specific stamp handling.
No regex (project rule); headings and titles are matched with string sets.
"""

from __future__ import annotations

from .generic import GenericExtractor

# Document-type headings that open a district ruling (lowercased, exact match
# after stripping trailing punctuation). Longest/most-specific are not needed —
# any match marks the opinion start.
_HEADINGS = frozenset(
    {
        "memorandum opinion and order",
        "memorandum opinion",
        "memorandum and order",
        "memorandum order",
        "memorandum decision and order",
        "memorandum decision",
        "memorandum ruling",
        "memorandum",
        "memorandum & order",
        "opinion and order",
        "order and opinion",
        "opinion",
        "order",
        "amended memorandum opinion and order",
        "amended memorandum opinion",
        "report and recommendation",
        "report & recommendation",
        "report and recommendation of the magistrate judge",
        "findings of fact and conclusions of law",
        "findings of fact",
        "decision and order",
        "ruling",
        "judgment",
        "final judgment",
        "order and reasons",
        "memorandum ruling and order",
        "ruling and order",
        "memorandum opinion & order",
    }
)

# Judicial titles that close a signature block; the line above carries the name.
_JUDGE_TITLES = (
    "united states district judge",
    "united states magistrate judge",
    "united states bankruptcy judge",
    "united states circuit judge",
    "senior united states district judge",
    "chief united states district judge",
    "senior united states magistrate judge",
    "u.s. district judge",
    "u.s. magistrate judge",
    "u.s.d.j.",
    "u.s.m.j.",
    "chief united states magistrate judge",
    "chief judge",
    "senior district judge",
    "district judge",
    "magistrate judge",
)
# Lines that sit in a signature block but are not the judge's name.
_SIG_SKIP = (
    "so ordered",
    "it is so ordered",
    "dated",
    "date",
    "entered",
    "signed",
    "s/",
    "/s/",
    "by the court",
)

# Headmatter-facsimile geometry.
_CAPTION_GAP = 8.0  # x-gap (pt) that separates caption runs / the divider
_CAPTION_CHAR_W = 6.0  # monospace column width
_CAPTION_LEFT = 72.0  # left text margin (column 0)


def _is_rule(text: str) -> bool:
    t = text.strip()
    return len(t) >= 3 and all(c in "_-–—" for c in t)


def _strip_sig_prefix(text: str) -> str:
    t = text.strip()
    for p in ("/s/", "s/"):
        if t.lower().startswith(p):
            return t[len(p) :].strip()
    return t


def _looks_like_name(text: str) -> bool:
    """A judge name in a signature block: 2–5 tokens, each capitalized
    (all-caps 'ROY K. ALTMAN' or title-case 'Shalina D. Kumar'), allowing
    initials, 'Jr.'/'III', hyphens."""
    t = _strip_sig_prefix(text).rstrip(",")
    toks = t.split()
    if not (2 <= len(toks) <= 6):
        return False
    for tok in toks:
        core = tok.rstrip(".,").replace("-", "").replace("'", "")
        if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
            continue
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class DistrictBase(GenericExtractor):
    drop_notice_in_body = False

    # ----------------------------------------- pleading-paper line numbers
    def page_lines(self, page):
        """On pleading paper (California etc.), a left gutter carries the
        sequential line numbers 1-28, set off from the body by a vertical margin
        rule; pdfplumber merges each number onto its line ('1 However ...'). When
        that rule is present, drop the chars left of it so the body reads cleanly
        without the line numbers. Gated on the rule, so ordinary CM/ECF filings
        (no gutter) are untouched."""
        gx = self._pleading_gutter_x(page)
        if gx is not None:
            page = page.filter(lambda c: c["x0"] >= gx - 1)
        return super().page_lines(page)

    @staticmethod
    def _pleading_gutter_x(page):
        """X of the pleading margin rule that separates the line-number gutter
        from the body, or None. A tall, thin vertical rule in the left gutter
        zone (x≈50-130) spanning most of the page."""
        tall = page.height * 0.6
        xs = [
            r["x0"]
            for r in page.rects
            if (r["x1"] - r["x0"]) < 3
            and (r["bottom"] - r["top"]) > tall
            and 45 < r["x0"] < 130
        ]
        xs += [
            l["x0"]
            for l in page.lines
            if abs(l["x1"] - l["x0"]) < 3
            and abs(l["bottom"] - l["top"]) > tall
            and 45 < l["x0"] < 130
        ]
        return max(xs) if xs else None

    def extract_page_tables(self, page):
        """Completeness-first: don't lift tables into separate structures.
        District rulings embed fee schedules / claim charts / exhibits whose
        rows would otherwise be excluded from the body (their bbox is skipped)
        and lost. Leaving them as body lines keeps every row in the output."""
        return []

    # NOTE: removal of page furniture (running footers, bates) and footnote /
    # opinion-start tuning are intentionally NOT in this shared base — they are
    # per-court, so tuning one district can't regress another. A court that
    # needs them defines them in its own file (see ``akd.py`` for the model).

    # ----------------------------------------------- headmatter facsimile
    # District captions put parties on the left and case numbers on the right,
    # usually separated by a stacked column of punctuation (')' / ']' / ':') or
    # just whitespace. Render the headmatter as a whitespace-preserved facsimile
    # — each line's runs placed at their real x — so those columns line up.
    # Splitting is by x-gap, so any divider glyph works; every glyph is kept
    # (each row is one positioned string), so coverage is unaffected. Not every
    # district has a column caption, but where it does this is a clear win and
    # it is harmless (a single-column caption just renders at its x) elsewhere.
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        items = []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                continue
            for line in seg:
                if not self.line_plain_text(line).strip():
                    continue
                top = round(line.get("top", 0), 1)
                for x0, text in self._caption_runs(line):
                    items.append((top, x0, text))
        rows = self._layout_rows(items)
        if rows:
            out["summary"] = rows
        return out

    def _caption_runs(self, line):
        """Split a line into (x0, text) runs at the wide x-gaps that separate
        caption columns (the divider, the case-number column), leaving ordinary
        word spacing within a run intact."""
        chars = line.get("chars") or []
        if not chars:
            return []
        runs, cur = [], [chars[0]]
        for c in chars[1:]:
            if c["x0"] - cur[-1]["x1"] > _CAPTION_GAP:
                runs.append(cur)
                cur = [c]
            else:
                cur.append(c)
        runs.append(cur)
        out = []
        for run in runs:
            text = self.line_plain_text({"chars": run}).strip()
            if text:
                out.append((round(run[0]["x0"], 1), text))
        return out

    @staticmethod
    def _layout_rows(items):
        """Place runs that share a row (same top) on one line, positioned by x0
        in a monospace grid, so vertical columns (the divider) line up."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1]))
        rows, segs, cur_top = [], [], None

        def emit(parts):
            line = ""
            for x0, text in sorted(parts, key=lambda p: p[0]):
                col = max(
                    len(line) + (1 if line else 0),
                    int((x0 - _CAPTION_LEFT) / _CAPTION_CHAR_W),
                )
                line += " " * (col - len(line)) + text
            return line

        for top, x0, text in items:
            if cur_top is not None and abs(top - cur_top) > 3:
                rows.append(emit(segs))
                segs = []
            segs.append((x0, text))
            cur_top = top
        if segs:
            rows.append(emit(segs))
        return rows

    # ---------------------------------------------------------------- author
    def _signature_author(self, all_segments):
        """The judge named just above a 'United States District Judge' (etc.)
        title line — scanning from the end, where the signature block sits."""
        lines = [
            self.line_plain_text(l).strip() for _p, seg, _k in all_segments for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            low = lines[i].lower().strip().rstrip(".")
            title = next(
                (
                    t
                    for t in _JUDGE_TITLES
                    if low == t.rstrip(".") or low.endswith(" " + t.rstrip("."))
                ),
                None,
            )
            if title is None:
                continue
            # Walk back over rules / 'SO ORDERED' / 'Dated:' to the name line.
            for j in range(i - 1, max(-1, i - 5), -1):
                cand = lines[j]
                clow = cand.lower()
                if _is_rule(cand) or any(clow.startswith(s) for s in _SIG_SKIP):
                    if clow.startswith(("s/", "/s/")) and _looks_like_name(cand):
                        return _strip_sig_prefix(cand).rstrip(",")
                    continue
                if _looks_like_name(cand):
                    return _strip_sig_prefix(cand).rstrip(",")
            # Title on the same line as the name ('Dated: ... District Judge')?
        return None

    def _present_author(self, all_segments):
        """Minute-order author: 'Present: The Honorable NAME, ... JUDGE'."""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                key = "the honorable "
                if "present:" in low and key in low and "judge" in low:
                    after = t[low.find(key) + len(key) :]
                    name = after.split(",")[0].strip()
                    if name:
                        return name
        return None

    # A surname + abbreviated/spelled-out judge title that opens the opinion
    # ('Rufe, J.' / 'Smith, Chief Judge.').
    _BYLINE_TITLES = (
        "Chief Judge",
        "Senior Judge",
        "District Judge",
        "Magistrate Judge",
        "Circuit Judge",
        "Judge",
        "C.J.",
        "J.",
        "U.S.D.J.",
        "U.S.M.J.",
    )

    _ABBREV_TITLES = ("J.", "C.J.", "P.J.", "U.S.D.J.", "U.S.M.J.")

    def _byline_author(self, all_segments, limit=12):
        """A 'NAME, <title>' byline near the top (e.g. Pennsylvania-E 'Rufe, J.
        February 27, 2026'). Scans only the opening segments so a mid-opinion
        citation can't masquerade as the author."""
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                if "," not in t or len(t) > 60:
                    continue
                name, rest = t.split(",", 1)
                name, rest = name.strip(), rest.strip()
                toks = name.replace("-", " ").split()
                if not (
                    1 <= len(toks) <= 3
                    and all(w[:1].isupper() and w.rstrip(".").isalpha() for w in toks)
                ):
                    continue
                first = rest.split()[0] if rest.split() else ""
                # 'Rufe, J.' / 'Rufe, J. <date>' or a spelled-out judge title.
                if (
                    first in self._ABBREV_TITLES
                    or rest.rstrip(".") in self._BYLINE_TITLES
                    or any(
                        rest.startswith(tt)
                        for tt in self._BYLINE_TITLES
                        if tt[0].isalpha() and len(tt) > 3
                    )
                ):
                    return name
        return None

    def _caption_judge(self, all_segments, limit=14):
        """A caption author tag: 'Judge NAME' / 'Hon. NAME' / 'Honorable NAME'
        sitting in the caption column."""
        tags = ("judge ", "hon. ", "honorable ")
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for tag in tags:
                    if low.startswith(tag):
                        name = t[len(tag) :].split(",")[0].strip()
                        if _looks_like_name(name):
                            return name
        return None

    # ------------------------------------------------------------- opinion start
    def _is_heading(self, line) -> bool:
        """True if ``line`` is an exact document-type heading phrase
        ('MEMORANDUM OPINION AND ORDER' / 'ORDER' / ...)."""
        low = self.line_plain_text(line).strip().rstrip(".:").lower()
        return low in _HEADINGS

    def find_authors(self, all_segments) -> list:
        # Author, in order of reliability: signature block, minute-order
        # 'Present:' line, a 'NAME, J.' opening byline, a caption 'Judge NAME'.
        self._district_author = (
            self._signature_author(all_segments)
            or self._present_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        # Opinion start: the document-type heading; else the first body segment.
        # (Courts whose ruling opens differently — e.g. an ALL-CAPS heading after
        # a ruled caption box — override this in their own file; see akd.py.)
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._is_heading(seg[0]):
                start = i
                break
        if start is None:
            for i, (_p, seg, kind) in enumerate(all_segments):
                if kind == "body":
                    start = i
                    break
        if start is None:
            return []
        return [start]

    def split_author_line(self, line):
        """The opinion-start line is a heading, not a byline; the author comes
        from the signature block / minute line. Return (author, [heading-as-body]).
        When no structured author was found, leave it empty — guessing from the
        opening line would grab the caption banner ('UNITED STATES DISTRICT
        COURT') on a signature-less order."""
        author = getattr(self, "_district_author", None)
        return (author or "", [line])

    def classify_document_type(self, all_segments, author_indices, n_pages):
        from ..models import DocType

        if author_indices:
            return DocType.OPINION
        return super().classify_document_type(all_segments, author_indices, n_pages)
