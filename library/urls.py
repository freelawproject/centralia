from django.urls import path
from . import views

app_name = "library"
urlpatterns = [
    path("", views.court_list, name="court_list"),
    path("styles/", views.styles, name="styles"),
    path("audit/", views.audit, name="audit"),
    path("<slug:court_id>/reprocess", views.reprocess, name="reprocess"),
    path("<slug:court_id>/", views.court_detail, name="court_detail"),
    path("<slug:court_id>/<str:stem>/", views.document_detail, name="document_detail"),
]
