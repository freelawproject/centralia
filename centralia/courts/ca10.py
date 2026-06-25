"""United States Court of Appeals for the Tenth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


def _bold(c) -> bool:
    return "bold" in (c.get("fontname", "") or "").lower()


class TenthCircuit(FederalCircuitBase):
    court_id = "ca10"
    court_label = "United States Court of Appeals for the Tenth Circuit."
    circuit_phrase = "tenth circuit"
    # ca10 has no centered 'No. <docket>' running header; the body opens at
    # top~75 while the only top-margin furniture (the 'Appellate Case: …
    # Document: … Date Filed: …' CM/ECF band) sits at top~23. The inherited
    # 95pt cutoff would crop the first body line of every page, so lower it to
    # sit between the band and the body.
    page2_header_cutoff = 50.0
    # A follow-on opinion (concurrence / dissent) starts at the TOP of a new
    # page with a '<docket>, <case name>' header — '23-6210, United States v.
    # Watkins' / 'No. 25-2009, Sanchez, et al. v. Torrez, et al.' — then the
    # bold ALL-CAPS byline on the next line. The header is furniture marking the
    # opinion start; drop it (else it is captured as a stray opinion body).
    running_header_docket = True
    running_header_max_top = 100.0

    def is_docket_line(self, text) -> bool:
        t = (text or "").strip()
        if t.lower().startswith("no."):
            t = t[3:].strip()
        head = t.split(",", 1)[0].strip()  # the leading '<digits>-<digits>' token
        parts = head.split("-")
        return (
            len(parts) == 2
            and all(p.isdigit() for p in parts)
            and " v. " in t.lower()
        )

    # The clerk's e-filing stamp ('FILED / United States Court of Appeals /
    # Tenth Circuit / <clerk> / Clerk of Court') is set in 12pt bold Times; the
    # centered court banner is 13pt, so this drops the stamp and keeps the banner.
    efile_stamp_font = "TimesNewRomanPS-BoldMT"
    efile_stamp_size = 12.0

    def _byline_split(self, line):
        """ca10 opens each opinion with a bold, ALL-CAPS judge name; the bench
        title and any concurrence/dissent kind suffix follow in regular weight:

            **McHUGH**, Circuit Judge.                                (majority)
            **FEDERICO**, Circuit Judge, concurring in part and       (a partial
            dissenting in part.                                        dissent)

        The base form grammar finds the majority (terminator right after the
        title) but misses the dissent, whose kind suffix sits between the title
        and the '.'. Key on the font instead: a bold ALL-CAPS leading name with
        byline form is an opinion start; the regular-weight panel roster
        ('Before PHILLIPS, McHUGH, and FEDERICO, Circuit Judges.') and body
        lines are not bold-led, so they're rejected. The body opens on the next
        line, so the whole line is the byline. 'PER CURIAM' defers to the base."""
        text = (line.get("text") or "").strip()
        if not text:
            return None
        up = text.upper()
        if up.startswith("PER CURIAM") or up.startswith("BY THE COURT"):
            return super()._byline_split(line)
        chars = line.get("chars") or []
        # Leading word: the judge surname. Require it bold and (mostly) caps —
        # 'FEDERICO' / 'McHUGH' (the 'c' in 'Mc' keeps it from being str.isupper).
        lead = []
        for c in chars:
            t = c.get("text", "")
            if not any(ch.isalnum() for ch in t):
                if lead:
                    break  # name ends at its trailing comma
                continue
            lead.append(c)
            if t.endswith((",",)):
                break
        word = "".join(c.get("text", "") for c in lead).strip().rstrip(",")
        if not word or not any(_bold(c) for c in lead):
            return None
        letters = [ch for ch in word if ch.isalpha()]
        if not letters or sum(ch.isupper() for ch in letters) < len(letters) - 1:
            return None  # not an ALL-CAPS (allow one lowercase, e.g. 'McHUGH')
        if not self._has_byline_form(text):  # inherited from FederalCircuitBase
            return None
        return text, ""

    def build_opinion(self, op_start, op_end, **kwargs):
        """An 'Order and Judgment' carries no top byline, so the base labels it
        PER CURIAM. But ca10 signs such orders 'Entered for the Court / <Name> /
        <Circuit Judge>' — when that signer is present, use the named judge as
        the author rather than defaulting to PER CURIAM."""
        op = super().build_opinion(op_start, op_end, **kwargs)
        if op.author == "PER CURIAM":
            signer = self._entered_for_court_signer(op.blocks)
            if signer:
                op.author = signer
        return op

    def _entered_for_court_signer(self, blocks):
        """The judge named in an 'Entered for the Court / <Name> / <title>'
        signature, formatted '<Name>, <title>', or None. The name and bench
        title may share the block ('Bobby R. Baldock Circuit Judge') or fall on
        the line right after 'Entered for the Court'."""
        for i, b in enumerate(blocks):
            if b.text.strip().lower().startswith("entered for the court"):
                tail = b.text.strip()[len("Entered for the Court"):].strip(" ,.")
                cand = tail or (
                    blocks[i + 1].text.strip() if i + 1 < len(blocks) else ""
                )
                return self._format_signer(cand)
        return None

    def _format_signer(self, s: str):
        s = s.strip()
        for title in self.author_titles:  # ordered longest-first
            if s.endswith(title):
                name = s[: -len(title)].strip().rstrip(",").strip()
                if name:
                    return f"{name}, {title}"
        return None
