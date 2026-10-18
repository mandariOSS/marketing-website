from django.urls import path
from django.views.generic import RedirectView

from .views import press_logo_package

urlpatterns = [
    # Das eine Logo-Paket für /presse/ – gebaut aus static/brand/
    path("presse/mandari-logopaket.zip", press_logo_package, name="press_logo_package"),
    # /ueber-uns/ ist in /unternehmen/ aufgegangen. Eine bestehende Wagtail-Seite zieht
    # `python manage.py retire_page ueber-uns --redirect /unternehmen/` zurück.
    path("ueber-uns/", RedirectView.as_view(url="/unternehmen/", permanent=True)),
]
