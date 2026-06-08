"""Puerto Rico Court of Appeals (Tribunal de Apelaciones).

Opinions are in Spanish and do not use an English byline. The page-1 caption
('ESTADO LIBRE ASOCIADO DE PUERTO RICO / TRIBUNAL DE APELACIONES / PANEL ...')
is a two-column box (parties left, court-of-origin and case numbers right),
followed by the three-judge panel roster ('Panel integrado por su presidenta,
la Jueza ..., el Juez ... y la Jueza ...').

Two authorship shapes:

  * a designated author — the *ponente* — named just below the panel roster:
    'Cintrón Cintrón, Jueza Ponente' / 'Lotti Rodríguez, Juez Ponente' (the case
    of 'juez ponente' varies). The surname(s) before the comma is the author;
    the opinion body opens at the centered disposition header that follows
    ('SENTENCIA' / 'RESOLUCIÓN' / 'OPINIÓN', sometimes letter-spaced) and the
    dated opening ('En San Juan, Puerto Rico, a ...').

  * no ponente — a per-curiam panel decision (e.g. a pro-se 'por derecho propio'
    review): there is no author line, so the opinion opens at the centered
    disposition header and is authored PER CURIAM.

The author title is kept verbatim ('Jueza Ponente' / 'Juez Ponente').
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Centered disposition headers that open the body (despaced, upper-cased before
# matching, so the letter-spaced 'S E N T E N C I A' is recognized too).
_PR_DISPOSITIONS = (
    "SENTENCIA",
    "RESOLUCIÓN",
    "RESOLUCION",
    "OPINIÓN",
    "OPINION",
    "ORDEN",
)


class PuertoRicoCourtOfAppeals(StateSupreme):
    court_id = "prapp"
    court_label = "Puerto Rico Court of Appeals."
    # These are legal-size ('oficio') pages, 1008pt tall — not US Letter. The
    # default bottom margin (725, calibrated for 792pt pages) would clip the
    # bottom ~28% of every page; the body runs to ~910 above a footer rule at
    # ~942.
    margin_bottom = 940.0
    # The body is double-spaced, but block quotes (e.g. the lettered certiorari
    # criteria) and the closing certification are single-spaced. Those would be
    # classified 'notice' by gap and dropped — keep all body content.
    drop_notice_in_body = False

    # ------------------------------------------------------------- byline
    @staticmethod
    def _pr_name_ok(name: str) -> bool:
        toks = name.split()
        if not toks or len(toks) > 4:
            return False
        return all(
            t[:1].isupper() and t.replace("'", "").replace("-", "").isalpha()
            for t in toks
        )

    def _pr_ponente(self, text: str):
        """Parse a 'NAME, Juez[a] Ponente' byline -> (name, title, None)."""
        t = text.strip()
        if "," not in t or not t.lower().rstrip(".").endswith("ponente"):
            return None
        name, title_raw = (s.strip() for s in t.split(",", 1))
        title_raw = title_raw.rstrip(".")
        toks = title_raw.lower().split()
        if not toks or toks[0] not in ("juez", "jueza") or toks[-1] != "ponente":
            return None
        if not self._pr_name_ok(name):
            return None
        return name, " ".join(w.capitalize() for w in title_raw.split()), None

    def parse_author_line(self, text):
        r = self._pr_ponente(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _pr_doc_header(self, line) -> bool:
        t = self.line_plain_text(line).strip()
        if not t or line.get("x0", 0) < 200:  # centered, not the left margin
            return False
        if not self.line_meta(line)[2]:  # bold
            return False
        return "".join(t.split()).upper().startswith(_PR_DISPOSITIONS)

    # ------------------------------------------------------------- authors
    def extract(self, pdf_path):
        self._pr_percuriam = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._pr_percuriam = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._pr_ponente(self.line_plain_text(seg[0]).strip()):
                return [i]
        # No ponente -> per-curiam panel decision; the body opens at the centered
        # disposition header.
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._pr_doc_header(seg[0]):
                self._pr_percuriam = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_pr_percuriam", None) is not None:
            return "", [line]  # the disposition header opens the body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_pr_percuriam", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op
