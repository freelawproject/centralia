"""District of Columbia Court of Appeals.

Byline is name-first with a spelled-out judicial title and a colon, running
inline with the opinion text, not bold:
  'SHANKER, Associate Judge: Appellant Khari Alston ...'      (majority)
  'THOMPSON, Senior Judge: The petitioner ...'
  'BECKWITH, Associate Judge, dissenting: ...'                (separate writing)
A 'Before MCLEESE and SHANKER, Associate Judges, and GLICKMAN, Senior ...'
panel roster (plural 'Judges', 'Before' lead) and the announcement lines
('Opinion for the court by Senior Judge THOMPSON.' / 'Dissenting opinion by
Associate Judge BECKWITH at page 31.', which have no comma after a surname) are
not opinion starts.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name

_TITLES = ("Associate Judge", "Senior Judge", "Chief Judge")


class DCCourtOfAppeals(StateSupreme):
    court_id = "dc"
    court_label = "District of Columbia Court of Appeals."

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Route the revision notice ('Notice: This opinion is subject to formal
        revision before publication ...') out of the headmatter into the dropped
        bucket — administrative furniture, not opinion content. It opens with
        'Notice:' and runs until the court banner."""
        hm = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        summary = hm.get("summary") or []
        notice, kept, in_notice = [], [], False
        for row in summary:
            s = str(row).strip()
            if s.lower().startswith("notice:"):
                in_notice = True
            if in_notice and "court of appeals" in s.lower():
                in_notice = False  # banner — notice has ended
            if in_notice:
                notice.append(s)
            else:
                kept.append(row)
        if notice:
            hm["summary"] = kept
            hm["dropped"] = list(hm.get("dropped") or []) + [" ".join(notice)]
        return hm

    def _dc_parse(self, text: str):
        """Return (name, title, kind) or None."""
        text = text.strip()
        if text.upper().startswith("BEFORE ") or "," not in text:
            return None
        name = text.split(",", 1)[0].strip()
        if not _is_byline_name(name):
            return None
        rest = text.split(",", 1)[1].strip()
        title = next((t for t in _TITLES if rest.startswith(t)), None)
        if title is None:
            return None
        # After the title comes ': <body>' (majority) or ', <kind>: <body>'.
        low = rest[len(title) :].lower()
        if "concur" in low[:30] and "dissent" in low[:30]:
            kind = "concurring in part and dissenting in part"
        elif "concur" in low[:30]:
            kind = "concurring"
        elif "dissent" in low[:30]:
            kind = "dissenting"
        else:
            kind = None
        return name, title, kind

    def parse_author_line(self, text):
        r = self._dc_parse(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._dc_parse(text) is None:
            return super()._byline_split(line)
        ci = text.find(":")
        if ci == -1:
            return text, ""
        return text[: ci + 1], text[ci + 1 :].strip()
