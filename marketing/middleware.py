"""
Marketing Middleware: HTTP Link Header (RFC 8288) for agent discovery.

Adds a Link: response header on HTML pages pointing crawlers, AI agents and
research tools to canonical resources (sitemap, license docs, security policy,
trust center). Uses IANA-registered link relation types where possible.

Reference:
- RFC 8288 — Web Linking: https://www.rfc-editor.org/rfc/rfc8288
- IANA Link Relations: https://www.iana.org/assignments/link-relations/
"""

from __future__ import annotations

from django.conf import settings


class LinkHeaderMiddleware:
    """Adds a single ``Link`` HTTP header on HTML responses.

    Header format follows RFC 8288: comma-separated list of
    ``<URL>; rel="relation-type"`` entries.

    Only emits the header on HTML responses (skip JSON/XML APIs, sitemap,
    static files, redirects). Does not override an existing Link header.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._cached_link_value: str | None = None

    def _build_link_value(self) -> str:
        """Build the Link header value once and cache it.

        We can cache because all entries are static URLs derived from
        SITE_URL — they don't change per request.
        """
        site_url = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
        if not site_url:
            return ""

        # IANA-registered link relations: https://www.iana.org/assignments/link-relations/
        # rel="sitemap"          — RFC 5005 (Atom feed paging) + sitemaps.org
        # rel="author"           — HTML 5 (points to /impressum/ as authoring info)
        # rel="privacy-policy"   — IANA registered
        # rel="terms-of-service" — IANA registered
        # rel="license"          — RFC 4946 (AGPL-3.0)
        # rel="service-doc"      — RFC 8631 (links to Trust Center as service documentation)
        # rel="describedby"      — RFC 5988 (security.txt describes security policy)
        # rel="vcs-git"          — non-standard but understood by many tools
        entries = [
            f'<{site_url}/sitemap.xml>; rel="sitemap"; type="application/xml"',
            f'<{site_url}/impressum/>; rel="author"',
            f'<{site_url}/datenschutz/>; rel="privacy-policy"',
            f'<{site_url}/agb/>; rel="terms-of-service"',
            f'<https://www.gnu.org/licenses/agpl-3.0.html>; rel="license"; title="AGPL-3.0"',
            f'<{site_url}/trust/>; rel="service-doc"',
            f'<{site_url}/.well-known/security.txt>; rel="describedby"; type="text/plain"',
            f'<https://github.com/mandariOSS/mandari>; rel="vcs-git"',
        ]
        return ", ".join(entries)

    def __call__(self, request):
        response = self.get_response(request)

        # Skip non-HTML responses, redirects, and responses already carrying Link
        content_type = response.get("Content-Type", "")
        if not content_type.startswith("text/html"):
            return response
        if response.status_code >= 300 and response.status_code < 400:
            return response
        if "Link" in response:
            return response

        if self._cached_link_value is None:
            self._cached_link_value = self._build_link_value()

        if self._cached_link_value:
            response["Link"] = self._cached_link_value

        return response
