"""
Context processors for the Mandari Marketing Website.
"""

from django.conf import settings


def site_context(request):
    """Provides site-wide context variables."""
    return {
        "MANDARI_API_URL": getattr(settings, "MANDARI_API_URL", ""),
        "SITE_URL": getattr(settings, "SITE_URL", ""),
        "STATUS_PAGE_URL": getattr(settings, "STATUS_PAGE_URL", ""),
        "BOOKING_URL": getattr(settings, "BOOKING_URL", ""),
        "ALTCHA_CHALLENGE_URL": getattr(settings, "ALTCHA_CHALLENGE_URL", ""),
    }
