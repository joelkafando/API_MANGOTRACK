from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path("", RedirectView.as_view(url="/console/")),
    path("api/", include("api.urls")),
    path("console/", TemplateView.as_view(template_name="console.html")),
]