"""Utah Court of Appeals.

Same two-part front matter as the Utah Supreme Court: a title-page authorship
summary ('JUDGE RYAN D. TENNEY authored this Opinion, in which JUDGES ORME and
HARRIS concurred except as to Part I(C) ...') that is left as headmatter, and
the actual opinion byline below it — a name-first colon line, 'TENNEY, Judge:'
(majority) or 'NAME, Judge, concurring:' / '..., dissenting:' (separate
writings). Only the colon byline starts the opinion, so the authorship summary
and its joinder roster don't leak into the body. The surname may be compound
('CHRISTIANSEN FORSTER').
"""

from __future__ import annotations

from ._appellate import StateAppellate


class UtahCourtOfAppeals(StateAppellate):
    court_id = "utahctapp"
    court_label = "Utah Court of Appeals."

    # The running footer ('20250757-CA 4 2026 UT App 101') is the last line of
    # every continuation page, set at body size at the body rail. Measured over
    # the corpus (650 pages): it always prints at top=727.7, while the lowest
    # real content anywhere — a page-1 footnote, which is the only page with no
    # footer — reaches 708.1. A margin band cuts it by position and
    # ``_capture_margin_band`` surfaces it in the Removed box. Without this the
    # footer sits INSIDE the footnote zone and is glued onto the note above it.
    margin_bottom = 718

    def find_footnote_separator(self, page):
        """Utah draws its footnote rule across the FULL text column, and the
        family base fences the separator to the bottom half of the page. A note
        long enough to fill most of a page pushes its own rule above that fence
        (christensen p11: rule at y=350.5 of 792) and the whole note reads as
        body prose.

        The fence is unnecessary here because the rule's shape is measured, not
        assumed: it must start at the page's own text rail and run the exact
        width of that page's text column — a signature nothing else on a Utah
        page has. Guarded by the same rule the base uses: a divider with an
        opinion byline beneath it is not a terminal footnote separator."""
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        lines = [l for l in page.extract_text_lines() if (l.get("text") or "").strip()]
        if not lines:
            return None
        counts: dict[int, int] = {}
        for l in lines:
            key = round(l["x0"])
            counts[key] = counts.get(key, 0) + 1
        rail, hits = max(counts.items(), key=lambda kv: (kv[1], -kv[0]))
        if hits < 3:
            return None
        column = [l for l in lines if round(l["x0"]) == rail]
        width = max(round(l["x1"]) for l in column) - rail
        if width <= 0:
            return None
        sep = self.footnote_sep_fixed_left_rule(
            page, width=float(width), tol=6.0, x0_max=rail + 4
        )
        if sep is None:
            return None
        for l in lines:
            if l["top"] > sep and self.parse_author_line((l.get("text") or "").strip()):
                return None
        return sep

    def build_footnote(self, label, lines):
        """Lift the printed 'N. ' off the note's first paragraph.

        ``Footnote.label`` is a separate field the renderers draw in their own
        column; the base already does this when the label is a raised glyph (it
        strips the ``<footnotemark>`` span). Utah's label is body-size literal
        text, so it has to come off here or every note reads '1. 1. "On
        appeal ...'."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label.isdigit():
            tag, text = fn.paragraphs[0]
            prefix = f"{label}. "
            if text.startswith(prefix):
                fn.paragraphs[0] = (tag, text[len(prefix) :].lstrip())
        return fn

    def detect_footnote_label(self, line):
        """Utah's footnote labels are set at BODY size — '1. "On appeal from a
        bench trial, ..."' — so the base's raised-glyph test never fires and
        every note in the zone merged into one unlabelled blob.

        Inside a separator-delimited footnote zone the opening shape is
        unambiguous: a short run of digits, a period, then a space. Bounded to
        two digits so a wrapped citation line opening on a year or a pin cite
        ('2023 UT App 141. ...') cannot masquerade as a label, and the label
        run must be followed by prose on the same line."""
        label = super().detect_footnote_label(line)
        if label is not None:
            return label
        chars = line.get("chars") or []
        if not chars:
            return None
        text = self.line_plain_text(line).lstrip()
        digits = ""
        for ch in text:
            if not ch.isdigit():
                break
            digits += ch
        if not digits or len(digits) > 2:
            return None
        rest = text[len(digits) :]
        if not rest.startswith(". "):
            return None
        if not rest[2:].strip():
            return None
        return digits

    def _uca_byline(self, text: str):
        """Parse the colon body byline 'NAME, Judge[, kind]:' -> (name, title,
        kind), else None. The 'JUDGE X authored ... in which ...' authorship
        summary has no such form, so it stays headmatter."""
        t = text.strip()
        if not t.endswith(":") or "," not in t:
            return None
        name, rest = (s.strip() for s in t[:-1].split(",", 1))
        toks = name.split()
        if not toks or len(toks) > 3:
            return None
        if not all(
            k.replace("'", "").replace("-", "").isalpha() and k.isupper() for k in toks
        ):
            return None
        role = rest.lower()
        if not role.startswith("judge"):
            return None
        role = role[len("judge") :].lstrip(", ")
        if "concur" in role and "dissent" in role:
            kind = "concurring in part and dissenting in part"
        elif "concur" in role:
            kind = "concurring"
        elif "dissent" in role:
            kind = "dissenting"
        else:
            kind = None
        return name, "Judge", kind

    def parse_author_line(self, text):
        r = self._uca_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)
