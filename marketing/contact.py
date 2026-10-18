"""
Kontaktformulare auf /kontakt/: Terminanfrage (#termin) und Nachricht (#nachricht).

Ablauf beim Absenden:
  1. Honigtopf-Feld prüfen, Altcha-Lösung prüfen (Proof of Work, selbst gehostet, mit Ablaufzeit)
     und jede Lösung nur einmal annehmen.
  2. Felder prüfen, dann Begrenzung je Anschluss (fünf je Stunde) und insgesamt (60 je Stunde).
  3. Anfrage als E-Mail an CONTACT_TO zustellen (Antwort-an: die Absenderin).

Einmal-Prüfung und Zähler liegen im Zwischenspeicher „formulare“ (DatabaseCache, siehe
settings.CACHES), damit alle gunicorn-Worker dieselben Einträge sehen. Die Tabelle legt
`python manage.py createcachetable` an (läuft im Container-Start mit).

Die Website speichert Anfragen nicht. Protokolliert werden Art und Ergebnis, nie Inhalte oder Absender.

Zustellung (Umgebungsvariablen, keine Django-Einstellungen nötig):
  CONTACT_SMTP_HOST      SMTP-Server; ohne Wert gilt EMAIL_BACKEND bzw. im DEBUG-Modus die Konsole
  CONTACT_SMTP_PORT      Standard 465 (TLS); 587 schaltet auf STARTTLS
  CONTACT_SMTP_USER      Anmeldename (z. B. App-Passwort-Konto)
  CONTACT_SMTP_PASSWORD  Passwort
  CONTACT_FROM           Absender der Benachrichtigung, Standard hello@mandari.de
  CONTACT_TO             Empfänger, Standard hello@mandari.de
  CONTACT_TRUSTED_PROXIES  Zahl der eigenen Reverse Proxys vor der Website, Standard 1
                         (0 = direkt erreichbar, dann zählt nur REMOTE_ADDR)
"""

from __future__ import annotations

import base64
import datetime
import ipaddress
import json
import logging
import os
import re
import time
from urllib.parse import parse_qs, urlsplit

from django import forms
from django.conf import settings
from django.core.cache import caches
from django.core.mail import EmailMessage, get_connection
from django.core.mail.message import make_msgid
from django.utils import timezone

logger = logging.getLogger(__name__)

FALLBACK_ADDRESS = "hello@mandari.de"

TOPICS = [
    ("verwaltung", "Demo für unsere Verwaltung"),
    ("umstieg", "Umstieg vom bisherigen Ratsinformationssystem"),
    ("fraktion", "mandari Work für unsere Fraktion"),
    ("angebot", "Preise und Angebot"),
    ("partnerschaft", "Partnerschaft"),
    ("presse", "Presse und Medien"),
    ("anderes", "Etwas anderes"),
]
TOPIC_LABELS = dict(TOPICS)

TIME_SLOTS = [("9-11", "9–11 Uhr"), ("11-13", "11–13 Uhr"), ("13-15", "13–15 Uhr"), ("15-17", "15–17 Uhr")]
FORMATS = [("video", "Per Video"), ("telefon", "Am Telefon"), ("vor-ort", "Persönlich in Münster")]

# Alte Verweise wie /kontakt/?subject=Session-Angebot wählen das passende Thema vor.
_SUBJECT_TOPICS = [
    (re.compile(r"migration|umstieg|alt-ris", re.I), "umstieg"),
    (re.compile(r"kommune|session|pilot|oparl|adapter|dms|verwaltung|trust|demo", re.I), "verwaltung"),
    (re.compile(r"work|fraktion|beta", re.I), "fraktion"),
    (re.compile(r"preis|angebot|managed|sepa", re.I), "angebot"),
    (re.compile(r"partner|reseller|förder|foerder|ngo|beirat", re.I), "partnerschaft"),
    (re.compile(r"presse|interview", re.I), "presse"),
]

HERO = {
    "title": "Sprechen wir über Ihre Verwaltung.",
    "subline": (
        "Buchen Sie ein 30-minütiges Erstgespräch oder schreiben Sie uns. Sie sprechen mit Menschen, "
        "die Sitzungsdienst, Ratsarbeit und Vergabe kennen – und wir melden uns innerhalb eines Werktags."
    ),
    "ctas": [],
    "background_color": "gray",
}

# Adressen nach Anliegen (Abschnitt „Direkt zur richtigen Stelle“).
DIRECTORY = [
    {"anliegen": "Verwaltungen und Kommunen", "hinweis": "Demo, Pilotbetrieb, Vergabeunterlagen",
     "adresse": "hello@mandari.de"},
    {"anliegen": "Support", "hinweis": "Fragen zur Nutzung, Störungen, Zugänge", "adresse": "support@mandari.de"},
    {"anliegen": "Presse", "hinweis": "Anfragen, Interviews, Bildmaterial", "adresse": "presse@mandari.de",
     "link": "/presse/", "link_text": "Pressebereich"},
    {"anliegen": "Bewerbungen", "hinweis": "Auch initiativ", "adresse": "bewerbung@mandari.de"},
    {"anliegen": "Sicherheit", "hinweis": "Schwachstellen vertraulich melden", "adresse": "security@mandari.de",
     "link": "/sicherheit/disclosure/", "link_text": "Meldeverfahren"},
    {"anliegen": "Datenschutz", "hinweis": "Auskunft, Berichtigung, Löschung", "adresse": "datenschutz@mandari.de"},
    {"anliegen": "Missbrauch", "hinweis": "Rechtswidrige Inhalte und Spam melden", "adresse": "abuse@mandari.de",
     "link": "/abuse/", "link_text": "Meldestelle"},
    {"anliegen": "Buchhaltung", "hinweis": "Rechnungen und Abrechnung", "adresse": "invoice@mandari.de"},
]

PER_ADDRESS_PER_HOUR = 5
TOTAL_PER_HOUR = 60
RATE_WINDOW_SECONDS = 3600
CACHE_ALIAS = "formulare"


# Anlass zu einem ?subject=-Wert für den zugänglichen Namen eines Aufrufs (Linkzweck, WCAG 2.4.4): Führt derselbe
# Aufruftext auf einer Seite zu verschiedenen Anlässen, nennen vorlesende Programme den Anlass mit. Auf /kommunen/
# heißt der Aufruf im Seitenkopf und im Schlussband „Erstgespräch vereinbaren“ – einmal zur Anbindung, einmal für
# Pilotkommunen. Ausgabe: {% aufruf_name label url %} (marketing/templatetags/zugang.py).
ANLASS_NAMEN = {
    "Kommune-anbinden": "Kommune anbinden",
    "Pilot-Kommune": "Pilotkommune werden",
}


def anlass_for_url(url: str) -> str:
    """Anlass aus ``ANLASS_NAMEN`` für den ``subject``-Parameter einer Adresse (leer, wenn keiner eingetragen ist)."""
    werte = parse_qs(urlsplit(str(url or "")).query).get("subject") or [""]
    return ANLASS_NAMEN.get(werte[0], "")


def topic_for_subject(subject: str) -> str:
    """Thema, das ein ?subject=-Parameter vorwählt (leer, wenn nichts passt)."""
    for pattern, topic in _SUBJECT_TOPICS:
        if pattern.search(subject or ""):
            return topic
    return ""


def clean_line(value: str, length: int) -> str:
    """Eine Zeile ohne Steuerzeichen – verhindert eingeschleuste Kopfzeilen."""
    return re.sub(r"[\x00-\x1f\x7f]+", " ", str(value or "")).strip()[:length]


class _ContactBase(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=200)
    organisation = forms.CharField(max_length=160, required=False)
    thema = forms.ChoiceField(choices=TOPICS)
    datenschutz = forms.BooleanField(error_messages={"required": "Bitte bestätigen Sie die Datenschutzerklärung."})
    anlass = forms.CharField(max_length=80, required=False)
    # Honigtopf: Menschen sehen das Feld nicht, einfache Bots füllen es aus.
    website = forms.CharField(required=False)

    def clean_name(self):
        return clean_line(self.cleaned_data["name"], 120)

    def clean_organisation(self):
        return clean_line(self.cleaned_data.get("organisation", ""), 160)

    def clean_anlass(self):
        return clean_line(self.cleaned_data.get("anlass", ""), 80)


class AppointmentForm(_ContactBase):
    """Terminanfrage für ein 30-minütiges Erstgespräch."""

    kind = "termin"
    datum = forms.DateField(input_formats=["%Y-%m-%d"])
    zeitfenster = forms.ChoiceField(choices=TIME_SLOTS)
    format = forms.ChoiceField(choices=FORMATS)
    telefon = forms.CharField(max_length=40, required=False)
    nachricht = forms.CharField(max_length=4000, required=False)

    def clean_datum(self):
        day = self.cleaned_data["datum"]
        today = timezone.localdate()
        if day < today:
            raise forms.ValidationError("Bitte wählen Sie einen Tag ab heute.")
        if day > today + datetime.timedelta(days=180):
            raise forms.ValidationError("Bitte wählen Sie einen Tag in den nächsten sechs Monaten.")
        if day.weekday() >= 5:
            raise forms.ValidationError("Bitte wählen Sie einen Tag von Montag bis Freitag.")
        return day

    def clean_telefon(self):
        return clean_line(self.cleaned_data.get("telefon", ""), 40)


class MessageForm(_ContactBase):
    """Schriftliche Nachricht."""

    kind = "nachricht"
    nachricht = forms.CharField(
        max_length=4000,
        min_length=10,
        error_messages={"min_length": "Bitte schreiben Sie uns ein paar Worte mehr."},
    )


FORMS = {AppointmentForm.kind: AppointmentForm, MessageForm.kind: MessageForm}


# ── Spamschutz ─────────────────────────────────────────────────────────────


def _store():
    """Gemeinsamer Zwischenspeicher aller Worker (settings.CACHES["formulare"])."""
    return caches[CACHE_ALIAS]


def _trusted_proxies() -> int:
    try:
        return max(0, int(os.environ.get("CONTACT_TRUSTED_PROXIES", "1")))
    except ValueError:
        return 1


def _client_address(request) -> str:
    """Anschluss der Absenderin, wie ihn der eigene Reverse Proxy gesehen hat.

    X-Forwarded-For kann jeder Client selbst mitschicken. Verlässlich ist nur, was die eigenen
    Proxys anhängen: bei N Proxys der N-te Eintrag von hinten. Ohne Proxy (N = 0) oder ohne
    passenden Eintrag zählt REMOTE_ADDR. IPv6-Adressen zählen je /64-Netz, so viele Adressen
    hat ein einzelner Anschluss.
    """
    remote = request.META.get("REMOTE_ADDR", "")
    hops = _trusted_proxies()
    entries = [entry.strip() for entry in request.META.get("HTTP_X_FORWARDED_FOR", "").split(",") if entry.strip()]
    from_proxy = entries[-hops] if hops and len(entries) >= hops else remote
    for candidate in (from_proxy, remote):
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if address.version == 6:
            if address.ipv4_mapped:
                return str(address.ipv4_mapped)
            return str(ipaddress.ip_network(f"{address}/64", strict=False))
        return str(address)
    return "unbekannt"


def _rate_limit(request) -> str:
    """Leer, wenn die Anfrage durchgeht; sonst "zu-viele" (dieser Anschluss) oder "ueberlastet" (alle).

    Gleitendes Fenster von einer Stunde: Je Schlüssel stehen die Zeitpunkte der angenommenen
    Anfragen im Zwischenspeicher. Abgelehnte Anfragen zählen nicht mit.
    """
    store = _store()
    now = time.time()
    buckets = [
        (f"kontakt:rate:{_client_address(request)}", PER_ADDRESS_PER_HOUR, "zu-viele"),
        ("kontakt:rate:gesamt", TOTAL_PER_HOUR, "ueberlastet"),
    ]
    recent = []
    for key, limit, result in buckets:
        stamps = [stamp for stamp in store.get(key, []) if stamp > now - RATE_WINDOW_SECONDS]
        if len(stamps) >= limit:
            return result
        recent.append((key, stamps))
    for key, stamps in recent:
        store.set(key, [*stamps, now], RATE_WINDOW_SECONDS)
    return ""


def _altcha_ok(payload_b64: str) -> bool:
    from marketing.views import altcha_expires, verify_altcha_payload

    if not verify_altcha_payload(payload_b64):
        return False
    # Jede gelöste Aufgabe gilt genau einmal – gemerkt bis zu ihrem Ablauf.
    try:
        payload = json.loads(base64.b64decode(payload_b64))
        challenge, expires = payload["challenge"], altcha_expires(payload["salt"])
    except (KeyError, ValueError, TypeError):
        return False
    remaining = (expires or 0) - time.time()
    if remaining <= 0:
        return False
    return _store().add(f"kontakt:altcha:{challenge}", True, int(remaining) + 60)


# ── Zustellung ─────────────────────────────────────────────────────────────


def delivery_ready() -> bool:
    """Ob Anfragen zugestellt werden können. Ohne Zustellweg zeigt /kontakt/ die Mailadresse statt der Formulare."""
    return _connection() is not None


def _connection():
    host = os.environ.get("CONTACT_SMTP_HOST", "").strip()
    if host:
        port = int(os.environ.get("CONTACT_SMTP_PORT", "465"))
        return get_connection(
            "django.core.mail.backends.smtp.EmailBackend",
            host=host,
            port=port,
            username=os.environ.get("CONTACT_SMTP_USER", ""),
            password=os.environ.get("CONTACT_SMTP_PASSWORD", ""),
            use_ssl=port == 465,
            use_tls=port != 465,
            timeout=15,
        )
    backend = getattr(settings, "EMAIL_BACKEND", "")
    if backend and backend != "django.core.mail.backends.smtp.EmailBackend":
        return get_connection(backend)
    if settings.DEBUG:
        return get_connection("django.core.mail.backends.console.EmailBackend")
    return None


def _mail_body(form) -> tuple[str, str]:
    data = form.cleaned_data
    topic = TOPIC_LABELS.get(data["thema"], data["thema"])
    lines = [
        f"Thema: {topic}",
        f"Name: {data['name']}",
        f"E-Mail: {data['email']}",
        f"Organisation: {data.get('organisation') or '–'}",
    ]
    if form.kind == "termin":
        subject = f"Terminanfrage: {topic} – {data['name']}"
        lines += [
            f"Telefon: {data.get('telefon') or '–'}",
            f"Wunschtermin: {data['datum']:%d.%m.%Y}, {dict(TIME_SLOTS)[data['zeitfenster']]}",
            f"Gesprächsform: {dict(FORMATS)[data['format']]}",
        ]
    else:
        subject = f"Nachricht: {topic} – {data['name']}"
    if data.get("anlass"):
        lines.append(f"Aufgerufen über: {data['anlass']}")
    message = (data.get("nachricht") or "").strip()
    lines += ["", message or "(keine Nachricht)", "", "–", "Gesendet über das Kontaktformular auf mandari.de"]
    return clean_line(subject, 200), "\n".join(lines)


def handle_submission(request):
    """Verarbeitet einen POST auf /kontakt/.

    Rückgabe: (art, formular, ergebnis) mit ergebnis in
    ``"gesendet"``, ``"ungueltig"``, ``"spamschutz"``, ``"zu-viele"``, ``"ueberlastet"``,
    ``"nicht-zustellbar"``.
    """
    kind = request.POST.get("art", "")
    form_class = FORMS.get(kind)
    if form_class is None:
        return "", None, "ungueltig"
    form = form_class(request.POST)

    if request.POST.get("website"):
        logger.info("Kontaktformular (%s): Honigtopf ausgelöst", kind)
        return kind, form, "spamschutz"
    if not _altcha_ok(request.POST.get("altcha", "")):
        logger.info("Kontaktformular (%s): Spamschutz nicht gelöst", kind)
        return kind, form, "spamschutz"
    if not form.is_valid():
        return kind, form, "ungueltig"
    limited = _rate_limit(request)
    if limited:
        logger.warning("Kontaktformular (%s): Grenze je Stunde erreicht (%s)", kind, limited)
        return kind, form, limited

    connection = _connection()
    if connection is None:
        logger.error("Kontaktformular (%s): keine Zustellung eingerichtet (CONTACT_SMTP_HOST fehlt)", kind)
        return kind, form, "nicht-zustellbar"

    subject, body = _mail_body(form)
    mail = EmailMessage(
        subject=subject,
        body=body,
        from_email=os.environ.get("CONTACT_FROM", FALLBACK_ADDRESS),
        to=[os.environ.get("CONTACT_TO", FALLBACK_ADDRESS)],
        reply_to=[form.cleaned_data["email"]],
        connection=connection,
        # Message-ID ohne den Rechnernamen des Containers
        headers={"Message-ID": make_msgid(domain="mandari.de")},
    )
    try:
        mail.send(fail_silently=False)
    except Exception:  # noqa: BLE001 – jede Zustellstörung führt zur gleichen Rückmeldung
        logger.exception("Kontaktformular (%s): Zustellung fehlgeschlagen", kind)
        return kind, form, "nicht-zustellbar"

    logger.info("Kontaktformular (%s): zugestellt", kind)
    return kind, form, "gesendet"
