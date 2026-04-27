"""
URL configuration for Mandari Marketing Website.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from blog.feeds import BlogFeed
from marketing.views import (
    altcha_challenge,
    robots_txt,
    security_disclosure_view,
    security_txt,
    status_view,
)


def health_check(request):
    """Health check endpoint for Docker."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("django-admin/", admin.site.urls),
    path("cms-admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap, name="sitemap"),
    # RFC 9309 robots.txt — Crawl-Direktiven für Suchmaschinen und Bots.
    # Plain text, MUSS unter /robots.txt erreichbar sein, referenziert sitemap.xml.
    path("robots.txt", robots_txt, name="robots_txt"),
    path("blog/feed/", BlogFeed(), name="blog_feed"),
    # Live status page — server-side rendered with data from the Kener API.
    # MUST come BEFORE the Wagtail catch-all so it overrides any /status/
    # CMS page that might exist.
    path("status/", status_view, name="status"),
    # Altcha (DSGVO-konformer Captcha-Ersatz) — Challenge-Endpoint für das
    # JS-Widget. Form-Handler verifizieren mit verify_altcha_payload().
    path("altcha/challenge/", altcha_challenge, name="altcha_challenge"),
    # RFC 9116 security.txt — Sicherheitsforscher:innen finden hier den
    # Disclosure-Kontakt. MUSS unter /.well-known/security.txt erreichbar sein.
    path(".well-known/security.txt", security_txt, name="security_txt"),
    # Responsible Disclosure Page — als Sub-Path von /sicherheit/, deshalb via
    # Django-View statt Wagtail (Wagtail unterstützt Page-Nesting hier nicht
    # ohne Umbau der MarketingPage-Struktur).
    path("sicherheit/disclosure/", security_disclosure_view, name="security_disclosure"),
    # ── 301-Redirects für konsolidierte Pages ───────────────────────────────
    # Phase 1 — Konsolidierungen
    path("loesungen/", RedirectView.as_view(url="/produkt/#zielgruppen", permanent=True)),
    path("team/", RedirectView.as_view(url="/ueber-uns/#founder", permanent=True)),
    path("danksagungen/", RedirectView.as_view(url="/open-source/#danke", permanent=True)),
    # Phase 2 — weitere Konsolidierungen (Sicherheit komplett in Trust integriert,
    # FAQ aufgelöst — Page-spezifische FAQs direkt auf den jeweiligen Pages)
    path("sicherheit/", RedirectView.as_view(url="/trust/", permanent=True)),
    path("faq/", RedirectView.as_view(url="/kontakt/#faq", permanent=True)),
    # Wagtail catch-all (serves all CMS pages)
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
