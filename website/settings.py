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

# Öffentliche Basisadresse. Canonical, og:url, og:image, Sitemap, robots.txt und
# security.txt bauen ihre absoluten Adressen daraus – nie aus dem Host-Header.
# Produktion: SITE_URL=https://mandari.de
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8001")

# Öffentliche Statusseite. /status/ leitet dauerhaft dorthin weiter,
# die Fußzeile verlinkt sie.
STATUS_PAGE_URL = os.environ.get("STATUS_PAGE_URL", "https://status.mandari.de/").rstrip("/") + "/"

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

# Sicherheits-Header (marketing/sicherheit.py): Permissions-Policy immer, Content-Security-Policy je nach Modus.
# CSP_MODUS: "report" (Standard, Content-Security-Policy-Report-Only: der Browser meldet Verstöße, blockiert nichts),
# "scharf" (Content-Security-Policy: der Browser blockiert) oder "aus". Verstöße gehen an CSP_REPORT_URI, in
# Produktion den Endpunkt der mandari-Anwendung auf derselben Domain (Reverse Proxy: /csp-report/ → mandari).
CSP_MODUS = os.environ.get("CSP_MODUS", "report").strip().lower()
CSP_REPORT_URI = os.environ.get("CSP_REPORT_URI", "/csp-report/").strip()

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
    "wagtail.contrib.settings",
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
    "company",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ETag für HTML: Seiten ohne Formular sind bytegleich (CSP über Hashes, ohne Nonce); bei unveränderter Seite
    # antwortet die Website auf If-None-Match mit 304. Vor allen Middlewares, die den Inhalt ändern könnten.
    "django.middleware.http.ConditionalGetMiddleware",
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
    # Permissions-Policy und Content-Security-Policy (CSP_MODUS, siehe oben)
    "marketing.sicherheit.SicherheitsHeaderMiddleware",
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

# Zwischenspeicher. "formulare" liegt in der Datenbank, damit alle gunicorn-Worker dieselben
# Einträge sehen (Einmal-Prüfung des Spamschutzes, Begrenzung der Kontaktanfragen).
# Tabelle anlegen: python manage.py createcachetable (idempotent, läuft im Container-Start).
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "formulare": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "website_formular_cache",
        "OPTIONS": {"MAX_ENTRIES": 20000},
    },
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
WAGTAIL_SITE_NAME = "mandari"
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
