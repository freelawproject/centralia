"""URL configuration for webconfig.

The JavaScript review viewer (output/viewer.html) is the homepage, served by
Django along with the assets it loads relative to the site root — manifest.js,
notes.js, and the per-court <court>/<stem>.html documents shown in its iframe.
The rich database-backed views (court list + per-court breakdown + document
pages) live under /courts/.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from library.manifest import rebuild_manifest_if_stale
from library.views import (
    captions,
    footnote_index,
    footnote_review,
    footnote_truth,
    review_marks,
    viewer,
)

_OUTPUT = str(settings.BASE_DIR / "output")
_ASSETS = str(settings.BASE_DIR / "assets")


def _serve_nocache(request, path, document_root=None):
    """manifest.js / notes.js, told never to be cached.

    Both are rewritten whenever a court is re-ingested or a review mark moves,
    but ``django.views.static.serve`` sends only Last-Modified — so the browser
    reuses its copy and the sidebar keeps showing stale document counts through
    a normal reload, which reads as 'the new PDFs never arrived'.

    manifest.js is also rebuilt here when the DB has been written since the file
    was, so the health chips are right however the data changed — no write path
    has to remember to refresh them."""
    if path == "manifest.js":
        rebuild_manifest_if_stale()
    response = serve(request, path, document_root=document_root)
    response["Cache-Control"] = "no-store, must-revalidate"
    return response

urlpatterns = [
    path("", viewer, name="viewer"),
    path("captions", captions, name="captions"),
    path("marks", review_marks, name="review_marks"),
    path("footnotes/", footnote_index, name="footnote_index"),
    path("footnotes/<slug:court_id>/", footnote_review, name="footnote_review"),
    path("footnote-truth", footnote_truth, name="footnote_truth"),
    path("courts/", include("library.urls")),
    path("admin/", admin.site.urls),
    # Source PDFs: each rendered doc page frames its original at
    # ../../assets/<court>/<stem>.pdf, which resolves to /assets/... here.
    re_path(r"^assets/(?P<path>.+)$", serve, {"document_root": _ASSETS}),
    # Viewer assets, served from output/ at the site root so the viewer's
    # relative links resolve (manifest.js, notes.js, and <court>/<stem>.html).
    re_path(
        r"^(?P<path>(?:manifest|notes)\.js)$", _serve_nocache,
        {"document_root": _OUTPUT},
    ),
    re_path(r"^(?P<path>[^/]+/[^/]+\.html)$", serve, {"document_root": _OUTPUT}),
]
