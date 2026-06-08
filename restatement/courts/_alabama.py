"""Shared base for the Alabama appellate courts.

The Alabama Supreme Court and the Court of Civil/Criminal Appeals all publish
on the same "STATE OF ALABAMA -- JUDICIAL DEPARTMENT" template: a ``Rel:``
release line, a notice advisory, a centered court banner, ``OCTOBER TERM,
YYYY-YYYY``, ``____`` separators around the docket, the case caption, and an
``Appeal from <Court> (docket)`` history line. The body opens with an author
byline (``LASTNAME, Justice.`` or ``LASTNAME, Judge.``).

That shared structure lives here. Each court subclass declares only what
differs — the two-letter docket prefix, the author title(s), and the
``<court>`` label. No regex; the caption predicates and docket matcher are
plain string scans.
"""

from __future__ import annotations

from ..base import BaseExtractor
from ..models import DocType


_HYPHENS = "-‑"  # ASCII hyphen + non-breaking hyphen (U+2011)
_TITLE_PUNCT = set(" \t\n\r\f\v,.-:;")


class AlabamaAppellate(BaseExtractor):
    # --- Per-court identity (subclasses override) -----------------------
    court_id = ""
    court_label = ""
    docket_prefix = ""  # two-letter docket prefix, e.g. "SC" / "CL"
    author_titles = ("Justice",)

    # --- Shared Alabama appellate layout --------------------------------
    footnote_sep_rect = (72.0, 216.0)
    underline_offset_min = -4.0
    underline_offset_max = 5.0
    running_header_docket = True
    strip_author_trailing_mark = True
    banner_center_min_size = 20.0
    skip_notice_headmatter = True

    SKIP_BODY_TYPES = (DocType.CERTIFICATE,)

    # ====================================================================
    # DOCKET MATCHING (no regex) — '<PREFIX>-YYYY-NNNN'
    # ====================================================================
    def _match_docket(self, text: str) -> str | None:
        """Return the first '<docket_prefix>-YYYY-NNNN' token in ``text``, else
        None. The hyphens may be ASCII or non-breaking."""
        pre = self.docket_prefix
        if not pre:
            return None
        plen = len(pre)
        width = plen + 10  # PREFIX + hy + 4 + hy + 4
        n = len(text)
        i = 0
        while i <= n - width:
            if (
                text[i : i + plen] == pre
                and text[i + plen] in _HYPHENS
                and text[i + plen + 1 : i + plen + 5].isdigit()
                and text[i + plen + 5] in _HYPHENS
                and text[i + plen + 6 : i + plen + 10].isdigit()
            ):
                return text[i : i + width]
            i += 1
        return None

    def is_docket_line(self, text) -> bool:
        return self._match_docket(text or "") is not None

    # ====================================================================
    # DOCUMENT-TYPE CLASSIFIER
    # ====================================================================
    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """Alabama document styles:
        - CERTIFICATE OF JUDGMENT (page-1 centered heading) -> classified
          but not parsed (see SKIP_BODY_TYPES).
        - OPINIONS (authored byline) -> opinion.
        - NO-OPINION decision lists -> returned as opinion per spec.
        """
        for page_no, seg, _ in all_segments:
            if page_no > 1:
                break
            for l in seg:
                if (l.get("text") or "").strip() == "CERTIFICATE OF JUDGMENT":
                    return DocType.CERTIFICATE

        if author_indices:
            return DocType.OPINION

        text = " ".join(
            (l.get("text") or "") for _, seg, _ in all_segments for l in seg
        ).lower()
        if not text.strip():
            return DocType.UNKNOWN
        if "no opinion" in text:
            return DocType.OPINION
        if "per curiam" in text or "it is ordered" in text or "ordered that" in text:
            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # ====================================================================
    # CAPTION / HEADMATTER PARSER (no regex)
    # ====================================================================
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = {
            "decisiondate": None,
            "court": self.court_label,
            "docketnumber": None,
            "parties": [],
            "history": None,
            "parentcase": None,
        }
        party_lines = []
        saw_docket = False
        for seg in headmatter_segs:
            text = " ".join(l["text"].strip() for l in seg).strip()

            # 'Rel: <date>'
            if out["decisiondate"] is None and text.startswith("Rel:"):
                rest = text[len("Rel:") :].strip()
                if rest:
                    out["decisiondate"] = rest
                    continue

            if self.classify_segment(seg) == "notice":
                continue

            size, _, bold = self.line_meta(seg[0])

            if size >= 20:  # court-banner singleton (court_label is static)
                continue
            if self.is_separator_line(seg[0]):
                continue
            if not bold:
                continue

            if text.startswith("OCTOBER TERM,"):
                continue

            docket = self._match_docket(text)
            if docket:
                out["docketnumber"] = docket
                saw_docket = True
                continue

            if not saw_docket:
                continue

            # Petition title (all-caps) -> history.
            if " " in text and _is_all_caps_title(text):
                out["history"] = self._merge(out.get("history"), text)
                continue

            # Parent case: '(In re: ...)'
            if _starts_with_in_re(text):
                out["parentcase"] = text.strip("()")
                continue

            # Lower-court docket parentheticals -> history.
            if (
                _is_courtname_docket_paren(text)
                or _is_no_paren(text)
                or _is_alpha_docket_paren(text)
            ):
                out["history"] = self._merge(out.get("history"), text.strip("()"))
                continue

            # 'Appeal from <Court>' -> history.
            if _starts_appeal_from(text):
                out["history"] = self._merge(out.get("history"), text)
                continue

            party_lines.append(text)

        out["parties"] = party_lines

        # Loss-resistant raw dump of everything before the first opinion.
        raw = BaseExtractor.extract_headmatter(
            self, headmatter_segs, page1_rules=page1_rules
        )
        out["summary"] = raw.get("summary")
        out["dropped"] = raw.get("dropped")
        return out

    @staticmethod
    def _merge(prev, addition):
        return (prev + " " + addition) if prev else addition


# ---------------------------------------------------------------------------
# Caption line predicates (no regex)
# ---------------------------------------------------------------------------


def _is_all_caps_title(text: str) -> bool:
    """True for an all-caps title line: first char A-Z, every char an ASCII
    uppercase letter or one of space/,.-:; (no lowercase, digits, or other
    punctuation). Mirrors ^[A-Z][A-Z\\s,.\\-:;]+$."""
    if len(text) < 2:
        return False
    if not ("A" <= text[0] <= "Z"):
        return False
    for c in text:
        if "A" <= c <= "Z" or c in _TITLE_PUNCT:
            continue
        return False
    return True


def _starts_with_in_re(text: str) -> bool:
    """True for '( In re<word-boundary>...' (case-insensitive). Mirrors
    ^\\(\\s*In\\s+re\\b."""
    if not text.startswith("("):
        return False
    s = text[1:].lstrip()
    if not s[:2].lower() == "in":
        return False
    after_in = s[2:]
    if not (after_in and after_in[0].isspace()):  # \s+ requires >=1
        return False
    rest = after_in.lstrip()
    if not rest[:2].lower() == "re":
        return False
    after_re = rest[2:]
    if after_re and (after_re[0].isalnum() or after_re[0] == "_"):
        return False  # \b: next char must be a non-word char or end
    return True


def _is_courtname_docket_paren(text: str) -> bool:
    """True for '(Court Name: docket...'. Mirrors ^\\([\\w\\s.&]+:\\s*[\\w\\d\\-]+."""
    if not text.startswith("("):
        return False
    s = text[1:]
    i = 0
    while i < len(s):
        c = s[i]
        if c.isalnum() or c == "_" or c.isspace() or c in ".&":
            i += 1
        else:
            break
    if i < 1 or i >= len(s) or s[i] != ":":
        return False
    i += 1
    while i < len(s) and s[i].isspace():
        i += 1
    n2 = 0
    while i < len(s):
        c = s[i]
        if c.isalnum() or c == "_" or c == "-":
            i += 1
            n2 += 1
        else:
            break
    return n2 >= 1


def _is_no_paren(text: str) -> bool:
    """True for '(No. ...' (case-insensitive). Mirrors ^\\(No\\.\\s*."""
    return text.startswith("(") and text[1:].lower().startswith("no.")


def _is_alpha_docket_paren(text: str) -> bool:
    """True for '(XX-9...' where XX is 2-4 uppercase letters then a hyphen and
    a digit. Mirrors ^\\([A-Z]{2,4}[-‑]\\d."""
    if not text.startswith("("):
        return False
    s = text[1:]
    i = 0
    while i < len(s) and i < 4 and "A" <= s[i] <= "Z":
        i += 1
    if not (2 <= i <= 4):
        return False
    if i >= len(s) or s[i] not in _HYPHENS:
        return False
    return i + 1 < len(s) and s[i + 1].isdigit()


def _starts_appeal_from(text: str) -> bool:
    """True for 'Appeal from<word-boundary>...' (case-insensitive). Mirrors
    ^Appeal from\\b."""
    prefix = "appeal from"
    if not text.lower().startswith(prefix):
        return False
    after = text[len(prefix) :]
    if after and (after[0].isalnum() or after[0] == "_"):
        return False
    return True
