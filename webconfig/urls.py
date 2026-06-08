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

from library.views import captions, review_marks, viewer

_OUTPUT = str(settings.BASE_DIR / "output")
_ASSETS = str(settings.BASE_DIR / "assets")

urlpatterns = [
    path("", viewer, name="viewer"),
    path("captions", captions, name="captions"),
    path("marks", review_marks, name="review_marks"),
    path("courts/", include("library.urls")),
    path("admin/", admin.site.urls),
    # Source PDFs: each rendered doc page frames its original at
    # ../../assets/<court>/<stem>.pdf, which resolves to /assets/... here.
    re_path(r"^assets/(?P<path>.+)$", serve, {"document_root": _ASSETS}),
    # Viewer assets, served from output/ at the site root so the viewer's
    # relative links resolve (manifest.js, notes.js, and <court>/<stem>.html).
    re_path(r"^(?P<path>(?:manifest|notes)\.js)$", serve, {"document_root": _OUTPUT}),
    re_path(r"^(?P<path>[^/]+/[^/]+\.html)$", serve, {"document_root": _OUTPUT}),
]
