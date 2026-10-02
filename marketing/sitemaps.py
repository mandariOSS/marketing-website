"""
Sitemap für mandari.de.

Gegenüber der Wagtail-Standard-Sitemap:

* Adressen entstehen aus ``SITE_URL`` (immer ``https://`` in Produktion,
  identisch mit Canonical und og:url).
* ``lastmod`` ist plausibel: Übersichtsseiten (z. B. /releases/, /vergleich/)
  tragen das Datum ihrer jüngsten veröffentlichten Unterseite, die Startseite
  das jüngste Datum der gesamten Website. Ohne diese Regel bliebe die
  Startseite auf dem Tag ihrer ersten Veröffentlichung stehen, obwohl sich
  ihr Inhalt mit jeder neuen Seite ändert.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from wagtail.contrib.sitemaps import Sitemap

from marketing import seo


class MandariSitemap(Sitemap):
    def _urls(self, page, protocol, domain):
        items = list(self.paginator.page(page).object_list)
        own = [(item.path, item.depth, self.lastmod(item)) for item in items]
        root_id = self.get_wagtail_site().root_page_id

        urls = []
        last_mods = set()
        for item in items:
            if item.pk == root_id:
                candidates = [lastmod for _, _, lastmod in own]
            else:
                candidates = [self.lastmod(item)] + [
                    lastmod
                    for path, depth, lastmod in own
                    if depth == item.depth + 1 and path.startswith(item.path)
                ]
            candidates = [value for value in candidates if value]
            lastmod = max(candidates) if candidates else None

            for url_info in item.get_sitemap_urls(self.request):
                info = dict(url_info)
                info["location"] = seo.absolute_url(urlsplit(info["location"]).path)
                if lastmod:
                    info["lastmod"] = lastmod
                urls.append(info)
                last_mods.add(info.get("lastmod"))

        if last_mods and None not in last_mods:
            self.latest_lastmod = max(last_mods)
        return urls
