"""United States Court of Appeals for the Eighth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class EighthCircuit(FederalCircuitBase):
    court_id = "ca8"
    court_label = "United States Court of Appeals for the Eighth Circuit."
    circuit_phrase = "eighth circuit"

    # Headmatter criteria: typed rules; Submitted/Filed dates on one row.
    parse_criteria_enabled = True
    # CA8 repeats docket-then-caption for a consolidated record and states the
    # court appealed from ONCE below the last of them ('No. 24-3265' / 'United
    # States of America v. Bailey Belt' / 'No. 24-3296' / 'United States of
    # America v. Theodora Belt' / 'Appeal from United States District Court
    # for the District of South Dakota'). Filed against whichever case was
    # still open, every case but the last showed no origin at all — 15 of the
    # 16 petitions consolidated in minnesota_telecom_alliance.
    criteria_shared_tail = True

    def filter_margins(self, obj):
        """INK THE PAGE DOES NOT SHOW IS NOT CONTENT.

        Some CA8 chambers space their headmatter with runs of white-filled
        letters — 84 lowercase 'l's across four bands of page 1 in
        kyle_hane, 42 in permanent_general_assurance, more in
        minnesota_telecom_alliance. They are invisible to the reader and are
        typography, not text, but pdfplumber returns them like any other
        glyph, so they arrived in the middle of party names and case
        captions.

        Keyed on the fill being white, which is what makes them invisible —
        not on the letter, which is an ordinary one."""
        if obj.get("non_stroking_color") == (1.0, 1.0, 1.0):
            return None
        return super().filter_margins(obj)
    gap_tight_max = 10.0
    gap_single_max = 17.0
    gap_double_max = 28.0

    def find_footnote_separator(self, page):
        """A 2-INCH RULE AT THE RAIL — DRAWN AS A RECT BY SOME CHAMBERS AND AS
        A FILLED PATH BY OTHERS.

        The family reader (``_circuit._sep_at``) only ever looks at
        ``page.rects``. Roughly a fifth of this circuit's slips come from a
        producer that emits the very same rule as a filled quadrilateral,
        which pdfplumber returns in ``page.curves`` — the same chambers whose
        headmatter is spaced with white-filled letters (see
        ``filter_margins``). Those documents carry no thin rect anywhere, so
        the separator was never found and every footnote on the page was read
        as prose: twelve of 53 documents, including every 'The Honorable …
        District Judge' designation note and the five substantive notes in
        minnesota_telecom_alliance.

        The two populations were measured over the whole corpus — 1,233 thin
        shapes in 53 documents — and they do not overlap:

          * 125 shapes are 143.9-144.0pt wide starting at exactly x0=72.0,
            the page's own measured rail: 108 rects (0.72pt tall) and 17
            curves (0.84pt). Every one is a real separator — 119 open a
            raised label, the other six open a note carried over from the
            previous page. None shares its y-band with another shape.
          * The rest of the thin ink at the rail is citation underlines, whose
            widths scatter with a clean gap either side of 144: … 138.6,
            141.0, 142.0 | 145.0, 146.2, 149.9 …

        So the width the court actually draws is the whole discriminator, and
        the family's 120-170pt window straddles that gap. On nine pages it
        took an underline for the separator and swallowed the body beneath it
        — angela_kendall's footnote 4 ran to 2,230 characters of opinion, and
        bradley_bolin and kristine_williams each carried a page of prose as an
        unlabelled '?' footnote. Reading the rule the court draws retires
        those too.

        No page-position fence: the rule sits between 0.42 and 0.88 of the
        page and is a separator at every one of those heights."""
        rails = {self.body_baseline_x0}
        rail = self._page_text_rail(page)
        if rail is not None:
            rails.add(rail)
        thin = [s for s in list(page.rects) + list(page.curves) if s["height"] < 2]
        tops = []
        for s in thin:
            if not any(abs(s["x0"] - r) <= 2.0 for r in rails):
                continue
            if abs((s["x1"] - s["x0"]) - 144.0) > 0.75:
                continue
            # An underline broken around an italic run comes in same-y pieces;
            # a separator is alone on its band.
            if any(o is not s and abs(o["top"] - s["top"]) <= 2 for o in thin):
                continue
            tops.append(s["top"])
        return min(tops) if tops else None

    # The Eighth prints NO running header: every continuation page opens with
    # real text at top~73-75 (and the second line at ~91-95), and the folio sits
    # in the bottom margin. The family's blanket 95pt page-2 cutoff therefore
    # deleted the first — often the first TWO — lines of every page after the
    # first, which is where nearly all of this circuit's unplaced text came from.
    page2_header_cutoff = 0.0
