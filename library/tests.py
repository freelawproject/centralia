from types import SimpleNamespace

from django.test import SimpleTestCase

from .views import _document_quality


class _Opinions:
    def __init__(self, exists):
        self._exists = exists

    def exists(self):
        return self._exists


def _doc(**overrides):
    values = {
        "doc_type": "opinion",
        "warnings": [],
        "residual": [],
        "suspect": False,
        "coverage": 100.0,
        "layout_ok": True,
        "opinions": _Opinions(True),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class DocumentQualityTests(SimpleTestCase):
    def test_distinguishes_scan_from_unreadable_text_layer(self):
        scan = _doc(
            warnings=["scanned image-only PDF — no text layer to extract (needs OCR)"],
            opinions=_Opinions(False),
            suspect=True,
        )
        broken_font = _doc(
            warnings=["unreadable text layer: 900 unmapped (cid:N) glyphs"],
            opinions=_Opinions(False),
            suspect=True,
        )
        self.assertEqual(_document_quality(scan)[0], "scan")
        self.assertEqual(_document_quality(broken_font)[0], "text-layer")

    def test_distinguishes_missing_opinion_from_valid_non_opinion(self):
        failed_notice = _doc(
            doc_type="notice", opinions=_Opinions(False), suspect=True
        )
        valid_notice = _doc(
            doc_type="notice", opinions=_Opinions(False), suspect=False
        )
        self.assertEqual(_document_quality(failed_notice)[0], "missing-opinion")
        self.assertEqual(_document_quality(valid_notice)[0], "non-opinion")

    def test_actionable_parser_buckets(self):
        unplaced = _doc(residual=[{"kind": "content", "text": "lost"}])
        unknown = _doc(doc_type="unknown", opinions=_Opinions(False))
        layout = _doc(coverage=98.5)
        error = _doc(doc_type="error", opinions=_Opinions(False))
        self.assertEqual(_document_quality(unplaced)[0], "unplaced")
        self.assertEqual(_document_quality(unknown)[0], "unclassified")
        self.assertEqual(_document_quality(layout)[0], "layout")
        self.assertEqual(_document_quality(error)[0], "error")

    def test_clean_extraction(self):
        self.assertEqual(_document_quality(_doc()), ("clean", "clean extraction"))
