"""Supreme Court of Kentucky.

The lead opinion is an opinion-of-the-court heading naming the author after the
title: 'OPINION OF THE COURT BY JUSTICE CONLEY' / 'OPINION OF THE COURT BY CHIEF
JUSTICE BISIG' / 'CONCURRING OPINION BY JUSTICE KELLER'. Like Hawaiʻi's 'OPINION
OF THE COURT BY GINOZA, J.' form, but Kentucky carries the spelled-out title
('JUSTICE'/'CHIEF JUSTICE') before the surname, which is stripped to the name.

Separate writings are signed differently — an ALL-CAPS surname, an abbreviated
title, the kind, and a colon, running inline with the opinion text: 'NICKELL,
J., DISSENTING: Respectfully, I dissent ...' / 'THOMPSON, J., CONCURRING BY
SEPARATE OPINION: ...' / 'BISIG, J., CONCURRING IN PART, DISSENTING IN PART:
...'. The ALL-CAPS surname distinguishes the byline from the lead opinion's
lowercase announcement of it ('Nickell, J., dissents by separate opinion ...').
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, is_caps_name

# Longest-first so the part/dissent compound wins over the bare forms.
_KY_BYLINES = (
    (
        "CONCURRING IN PART AND DISSENTING IN PART OPINION BY",
        "concurring in part and dissenting in part",
    ),
    ("CONCURRING IN RESULT OPINION BY", "concurring in result"),
    ("CONCURRING OPINION BY", "concurring"),
    ("DISSENTING OPINION BY", "dissenting"),
    ("OPINION OF THE COURT BY", None),
    ("OPINION AND ORDER BY", None),
    ("OPINION BY", None),
)
_KY_TITLES = ("CHIEF JUSTICE", "JUSTICE")


class KentuckySupreme(StateSupreme):
    court_id = "ky"
    court_label = "Supreme Court of Kentucky."

    # Kentucky sets the body DOUBLE-spaced (~28pt) and block quotes single
    # (~14pt), indented to 108 with the right margin pulled in to ~504. That
    # 14pt leading falls under ``gap_tight_max`` (16), so a quote classifies as
    # 'notice' on gaps alone and never reaches the body. Let the both-margins
    # indent overrule the gap band — the quote's own geometry is unambiguous,
    # and it is the only thing that separates a quote from a body first line,
    # which indents to the same x0=108.
    blockquote_by_indent = True

    def extract_page_images(self, page) -> list:
        """Kentucky slip opinions carry a court-seal watermark image centered
        on every page (the same 'Im2' object, 363x294 at x≈124/top≈249). The
        body text is drawn over it, so cropping the image region rasterizes
        that text back in — making the harvested 'image' look like page
        content. The full text layer is intact, so don't render any image
        back: drop them all."""
        return []

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Kentucky's caption is The Flush-Right Status: the party name sits at
        the left margin and its status label is pinned against the right margin
        ('ADAM WHEELER; COURTNEY L. ........ APPELLANTS'), with the docket
        floating between the two on the 'V.' row. Nothing is drawn — the
        alignment IS the structure.

        pdfplumber merges each pair onto one line, so the styled headmatter
        emits 'ADAM WHEELER; COURTNEY L. APPELLANTS' as a single left-aligned
        row: the label collides with the party name and loses the right margin
        that says which side it labels. Re-split those rows into the
        three-zone ``__hmrow__`` form so each zone keeps its own alignment."""
        d = super().extract_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._ky_flush_right_rows(d["summary"], headmatter_segs)
        return d

    @staticmethod
    def _ky_flat(s: str) -> str:
        import re as _re

        return " ".join(_re.sub(r"<[^>]+>", "", str(s)).split())

    def _ky_flush_right_rows(self, summary, headmatter_segs) -> list:
        """Rebuild the multi-zone caption rows from the page-1 line runs.

        Keyed off the page's own margins rather than fixed x values: a run
        reaching the right margin is the status label, one starting at the left
        margin is the party, anything between is the docket. Rows that split
        into fewer than two zones are left exactly as the base styled them."""
        lines = [
            l
            for seg in headmatter_segs
            for l in seg
            if (((l.get("chars") or [{}])[0].get("page_number", 1)) or 1) == 1
        ]
        runs_by_line = [(l, self._split_line_runs(l)) for l in lines]
        xs = [r for _l, rs in runs_by_line for r in rs if r.get("x0") is not None]
        if not xs:
            return summary
        lmargin = min(r["x0"] for r in xs)
        rmargin = max(r["x1"] for r in xs)

        zoned = {}
        for l, rs in runs_by_line:
            if len(rs) < 2:
                continue
            cells = {"l": [], "c": [], "r": []}
            for r in rs:
                if r["x1"] > rmargin - 15 and r["x0"] > lmargin + 30:
                    k = "r"
                elif r["x0"] < lmargin + 30:
                    k = "l"
                else:
                    k = "c"
                cells[k].append(self.line_inline_text({"chars": r["chars"]}).strip())
            if sum(1 for k in cells if cells[k]) < 2:
                continue
            zoned[self._ky_flat(self.line_plain_text(l))] = {
                "__hmrow__": True,
                "l": " ".join(cells["l"]),
                "c": " ".join(cells["c"]),
                "r": " ".join(cells["r"]),
            }
        if not zoned:
            return summary

        out = []
        for row in summary:
            if isinstance(row, dict) and row.get("__hm__"):
                hit = zoned.get(self._ky_flat(row.get("html", "")))
                if hit is not None:
                    out.append(hit)
                    continue
            out.append(row)
        return out

    # ------------------------------------------------------- byline parsing
    def parse_author_line(self, text):
        t = text.strip().rstrip(".")
        up = t.upper()
        for prefix, kind in _KY_BYLINES:
            if not up.startswith(prefix):
                continue
            name = t[len(prefix):].strip()
            upn = name.upper()
            for title in _KY_TITLES:
                if upn.startswith(title + " "):
                    name = name[len(title) + 1:].strip()
                    break
            name = name.split(",")[0].strip()
            if name:
                return name, "Justice", kind
        sep = self._ky_separate(text)
        if sep is not None:
            return sep[0], "Justice", sep[1]
        return super().parse_author_line(text)

    @staticmethod
    def _ky_separate(text: str):
        """Parse an in-body separate-writing byline ('NICKELL, J., DISSENTING:')
        -> (name, kind, byline_end_index), or None. The surname must be ALL-CAPS
        (the lowercase 'Nickell, J., dissents ...' announcement is not a byline)
        and the title abbreviated ('J.' / 'C.J.')."""
        ci = text.find(":")
        if ci == -1:
            return None
        parts = [p.strip() for p in text[:ci].split(",")]
        if len(parts) < 3:
            return None
        name, title = parts[0], parts[1].replace(".", "").upper()
        if title not in ("J", "CJ") or not is_caps_name(name):
            return None
        kind_text = " ".join(parts[2:]).upper()
        has_c, has_d = "CONCURRING" in kind_text, "DISSENTING" in kind_text
        if has_c and has_d:
            kind = "concurring in part and dissenting in part"
        elif has_d:
            kind = "dissenting"
        elif has_c:
            kind = "concurring"
        else:
            return None
        return name, kind, ci + 1

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        sep = self._ky_separate(text)
        if sep is not None:
            end = sep[2]
            return text[:end], text[end:].strip()
        return super()._byline_split(line)
