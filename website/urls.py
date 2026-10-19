"""
URL configuration for Mandari Marketing Website.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from marketing import indexnow, llms
from marketing.docs_redirects import docs_redirect
from marketing.sitemaps import FesteSeitenSitemap, MandariSitemap
from marketing.views import (
    altcha_challenge,
    ingestor_info_view,
    robots_txt,
    security_disclosure_view,
    security_txt,
    sla_print_view,
)


def health_check(request):
    """Health check endpoint for Docker."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("django-admin/", admin.site.urls),
    path("cms-admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"wagtail": MandariSitemap, "feste": FesteSeitenSitemap}},
        name="sitemap",
    ),
    # RFC 9309 robots.txt — Crawl-Direktiven für Suchmaschinen und Bots.
    # Plain text, MUSS unter /robots.txt erreichbar sein, referenziert sitemap.xml.
    path("robots.txt", robots_txt, name="robots_txt"),
    # llms.txt (llmstxt.org): Übersicht für Sprachmodelle und KI-Suchen aus Titeln und Beschreibungen des CMS
    path("llms.txt", llms.llms_txt, name="llms_txt"),
    # IndexNow (marketing/indexnow.py): Schlüsseldatei /<schlüssel>.txt, nur mit INDEXNOW_KEY, sonst 404
    re_path(r"^(?P<name>[A-Za-z0-9-]{8,128})\.txt$", indexnow.schluesseldatei, name="indexnow_schluessel"),
    # Statusseite: eigene Instanz unter status.mandari.de, /status/ leitet dauerhaft dorthin.
    path("status/", RedirectView.as_view(url=settings.STATUS_PAGE_URL, permanent=True), name="status"),
    # Blog ruht (keine Beiträge): Index und Feed leiten auf die Releases. Reaktivieren: siehe README.
    path("blog/", RedirectView.as_view(url="/releases/", permanent=True), name="blog_index"),
    path("blog/feed/", RedirectView.as_view(url="/releases/", permanent=True), name="blog_feed"),
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
    # Infoseite zum mandari-ingestor — sein User-Agent verweist hierauf.
    path("ingestor/", ingestor_info_view, name="ingestor_info"),
    # Bis 18.10.2026 hieß sie /crawler/ (Adresse in älteren User-Agents, Mails und Logs). Der Ingestor ist kein
    # Crawler, und Server können User-Agents mit dem Wort „crawler“ ablehnen. Query-String bleibt erhalten.
    path("crawler/", RedirectView.as_view(url="/ingestor/", permanent=True, query_string=True)),
    # Druckansicht des SLA (Unterpfad der Wagtail-Seite /sla/, daher Django-View).
    path("sla/druck/", sla_print_view, name="sla_print"),
    # Unternehmensseiten (Relaunch 2026): Logo-Paket der Presse, /ueber-uns/ → /unternehmen/
    path("", include("company.urls")),
    # Dokumentation lebt auf docs.mandari.de (Repo mandariOSS/docs); alte Pfade leiten dauerhaft weiter
    path("docs/", docs_redirect, name="docs_index"),
    path("docs/<path:rest>", docs_redirect, name="docs_page"),
    # ── 301-Redirects für konsolidierte Pages ───────────────────────────────
    # Phase 1 — Konsolidierungen
    path("loesungen/", RedirectView.as_view(url="/produkte/", permanent=True)),
    path("team/", RedirectView.as_view(url="/unternehmen/", permanent=True)),
    path("danksagungen/", RedirectView.as_view(url="/open-source/#danke", permanent=True)),
    # Phase 2 — weitere Konsolidierungen (Sicherheit komplett in Trust integriert,
    # FAQ aufgelöst — Page-spezifische FAQs direkt auf den jeweiligen Pages)
    path("sicherheit/", RedirectView.as_view(url="/trust/", permanent=True)),
    path("faq/", RedirectView.as_view(url="/kontakt/", permanent=True)),
    # Relaunch 2026 — Produkte: /produkt/ ist aufgeteilt in /produkte/ (Plattform, Modulübersicht,
    # Bürgerportal) und /fraktionen/ (mandari Work); Wagtail-Seite per
    # `retire_page produkt --redirect /fraktionen/` zurückziehen
    path("produkt/", RedirectView.as_view(url="/fraktionen/", permanent=True)),
    # Wagtail catch-all (serves all CMS pages)
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Fehlerseiten: 404 rendert Django aus templates/404.html (Kopf- und Fußzeile, Wegweiser), 500 kommt ohne Datenbank
# und ohne Kontextprozessoren aus (marketing/fehlerseiten.py).
handler500 = "marketing.fehlerseiten.server_error"
