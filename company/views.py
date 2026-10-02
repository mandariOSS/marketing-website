from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from .press import logo_package


@require_http_methods(["GET", "HEAD"])
def press_logo_package(request):
    """/presse/mandari-logopaket.zip – alle Logo-Fassungen in einer Datei."""
    response = HttpResponse(logo_package(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="mandari-logopaket.zip"'
    response["Cache-Control"] = "public, max-age=86400"
    return response
