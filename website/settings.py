"""
Django settings for Mandari Marketing Website (Wagtail).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env first (highest priority), then shared .env
local_env_path = BASE_DIR / ".env"
if local_env_path.exists():
    load_dotenv(local_env_path)

# Load shared .env from parent (won't override already-set vars)
shared_env_path = BASE_DIR.parent / ".env"
if shared_env_path.exists():
    load_dotenv(shared_env_path)

SECRET_KEY = os.environ.get("WEBSITE_SECRET_KEY", os.environ.get("SECRET_KEY", "django-insecure-change-me"))
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

SITE_URL = os.environ.get("SITE_URL", "http://localhost:8001")
MANDARI_API_URL = os.environ.get("MANDARI_API_URL", "http://mandari:8000/api")

# Public URL of the Kener status page — used as the "open status page directly"
# fallback link. Default is the public production status page; the local
# docker-compose stack overrides this with its bundled Kener instance.
STATUS_PAGE_URL = os.environ.get("STATUS_PAGE_URL", "https://status.mandari.de")

# Server-side URL the marketing-site backend uses to call Kener's REST API.
# In Docker this is the internal service name; in local dev outside Docker
# this is typically the same host as STATUS_PAGE_URL.
KENER_INTERNAL_URL = os.environ.get("KENER_INTERNAL_URL", "http://kener:3000")

# API token for the Kener REST API. Generate one in the Kener admin under
# Settings → API Keys after logging in at /account/signin.
# Without a token the /status/ page degrades to a "open status page directly"
# fallback — it never breaks.
KENER_API_TOKEN = os.environ.get("KENER_API_TOKEN", "")

# Booking URL for "Call buchen" CTAs across the site.
# Defaults to the internal /kontakt/#termin-buchen anchor (native form on the
# contact page). Override with an external tool URL (Cal.com, Calendly, …)
# only if you decide to use one.
BOOKING_URL = os.environ.get("BOOKING_URL", "/kontakt/#termin-buchen")

# Altcha (DSGVO-konformer, self-hosted Captcha-Ersatz).
# Der HMAC-Key signiert Challenges + verifiziert Client-Antworten.
# In Production: ein langes, zufälliges Geheimnis aus der .env setzen.
ALTCHA_HMAC_KEY = os.environ.get(
    "ALTCHA_HMAC_KEY",
    "dev-only-altcha-secret-please-replace-in-production",
)
ALTCHA_CHALLENGE_URL = os.environ.get("ALTCHA_CHALLENGE_URL", "/altcha/challenge/")
ALTCHA_MAX_NUMBER = int(os.environ.get("ALTCHA_MAX_NUMBER", "100000"))

from urllib.parse import urlparse

_site_domain = urlparse(SITE_URL).netloc

_allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]
if "localhost" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("localhost")
if _site_domain and _site_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_site_domain)

_csrf_env = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(",") if o.strip()]
if SITE_URL and SITE_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(SITE_URL)

INSTALLED_APPS = [
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # Wagtail dependencies
    "modelcluster",
    "taggit",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    # Project apps
    "marketing",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    # RFC 8288 Link headers for agent / crawler discovery
    # (sitemap, license, privacy-policy, security.txt, vcs-git)
    "marketing.middleware.LinkHeaderMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "marketing.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

# Database
DATABASE_URL = os.environ.get(
    "WEBSITE_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mandari_website"),
)
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/wstatic/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

if not DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Wagtail settings
WAGTAIL_SITE_NAME = "Mandari"
WAGTAILADMIN_BASE_URL = SITE_URL
WAGTAIL_ADMIN_URL = "cms-admin/"

# Search
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
