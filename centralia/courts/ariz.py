"""Supreme Court of the State of Arizona.

Shares the Arizona page mechanics (running-header drop, ¶-marker body grouping,
centered headings, page-aware headmatter) with the Court of Appeals via
``ArizonaStyle``. What is specific here:

  * the byline is reversed and title-led: 'JUSTICE KING, Opinion of the Court:'
    / 'JUSTICE BOLICK, concurring:';
  * separate writings are located by the running-header identifier — when it
    switches from 'Opinion of the Court' to a justice byline (or one justice to
    the next), a new opinion starts on that page. The lead opinion is found by
    its byline; the body byline the court prints ('BOLICK, J., dissenting.') is
    kept as the author, with the opinion type taken from the header id.

(An authorship summary 'JUSTICE KING authored the Opinion of the Court ...' also
appears but isn't a byline — the caps-name check rejects it because the text
after the comma isn't a bare surname.)
"""

from __future__ import annotations

from ._arizona import ArizonaStyle
from ._statesupreme import StateSupreme, is_caps_name

_JUSTICE_HEADER = ("JUSTICE", "CHIEF JUSTICE", "VICE CHIEF JUSTICE")


class ArizonaSupreme(ArizonaStyle, StateSupreme):
    court_id = "ariz"
    court_label = "Supreme Court of the State of Arizona."

    # ------------------------------------------------------------- author line
    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip().rstrip(":")
        for title in ("VICE CHIEF JUSTICE", "CHIEF JUSTICE", "JUSTICE"):
            if t.upper().startswith(title + " ") and "," in t:
                rest = t[len(title) + 1 :]
                name, kind = rest.split(",", 1)
                name, kind = name.strip(), kind.strip()
                if not is_caps_name(name):
                    return None
                if "opinion of the court" in kind.lower():
                    kind = None
                return name, title.title(), kind
        return None

    # ------------------------------------------------------- opinion boundaries
    def find_authors(self, all_segments) -> list:
        # Lead opinion: its byline ('JUSTICE BEENE, Opinion of the Court:').
        base = list(super().find_authors(all_segments))

        first_idx_of_page: dict = {}
        for i, (pno, _seg, _k) in enumerate(all_segments):
            first_idx_of_page.setdefault(pno, i)

        # Separate writings: where the running-header identifier changes to a
        # justice byline, the opinion starts on the first segment of that page.
        prev = None
        for pno in sorted(self._page_header):
            hid = self._page_header[pno]
            if hid != prev:
                if prev is not None and hid.upper().startswith(_JUSTICE_HEADER):
                    idx = first_idx_of_page.get(pno)
                    if idx is not None:
                        base.append(idx)
                        self._op_type[idx] = self._header_type(hid)
                prev = hid

        return sorted(set(base))

    @staticmethod
    def _header_type(hid: str) -> str:
        low = hid.lower()
        if "concur" in low and "dissent" in low:
            return "concurring-in-part-and-dissenting-in-part"
        if "dissent" in low:
            return "dissent"
        if "concur" in low:
            return "concurrence"
        return "majority"
