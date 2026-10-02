"""
Kontaktformulare auf /kontakt/: Terminanfrage (#termin) und Nachricht (#nachricht).

Ablauf beim Absenden:
  1. Altcha-Lösung prüfen (Proof of Work, selbst gehostet) und jede Lösung nur einmal annehmen.
  2. Honigtopf-Feld und Begrenzung je IP-Adresse (Arbeitsspeicher, höchstens eine Stunde).
  3. Felder prüfen, Anfrage als E-Mail an CONTACT_TO zustellen (Antwort-an: die Absenderin).

Die Website speichert Anfragen nicht. Protokolliert werden Art und Ergebnis, nie Inhalte oder Absender.

Zustellung (Umgebungsvariablen, keine Django-Einstellungen nötig):
  CONTACT_SMTP_HOST      SMTP-Server; ohne Wert gilt EMAIL_BACKEND bzw. im DEBUG-Modus die Konsole
  CONTACT_SMTP_PORT      Standard 465 (TLS); 587 schaltet auf STARTTLS
  CONTACT_SMTP_USER      Anmeldename (z. B. App-Passwort-Konto)
  CONTACT_SMTP_PASSWORD  Passwort
  CONTACT_FROM           Absender der Benachrichtigung, Standard hello@mandari.de
  CONTACT_TO             Empfänger, Standard hello@mandari.de
"""

from __future__ import annotations

import base64
import datetime
import json
import logging
import os
import re

from django import forms
from django.conf import settings
from django.core.cache import cache
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
    {"anliegen": "Bewerbungen", "hinweis": "Auch initiativ", "adresse": "bewerbung@mandari.de",
     "link": "/karriere/", "link_text": "Karriere"},
    {"anliegen": "Sicherheit", "hinweis": "Schwachstellen vertraulich melden", "adresse": "security@mandari.de",
     "link": "/sicherheit/disclosure/", "link_text": "Meldeverfahren"},
    {"anliegen": "Datenschutz", "hinweis": "Auskunft, Berichtigung, Löschung", "adresse": "datenschutz@mandari.de"},
    {"anliegen": "Missbrauch", "hinweis": "Rechtswidrige Inhalte und Spam melden", "adresse": "abuse@mandari.de",
     "link": "/abuse/", "link_text": "Meldestelle"},
    {"anliegen": "Buchhaltung", "hinweis": "Rechnungen und Abrechnung", "adresse": "invoice@mandari.de"},
]

PER_ADDRESS_PER_HOUR = 5
TOTAL_PER_HOUR = 60
_ALTCHA_REUSE_SECONDS = 2 * 3600


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


def _client_address(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else "") or request.META.get("REMOTE_ADDR", "")


def _within_rate_limit(request) -> bool:
    address = _client_address(request) or "unbekannt"
    per_address = f"kontakt:rate:{address}"
    total = "kontakt:rate:gesamt"
    cache.add(per_address, 0, 3600)
    cache.add(total, 0, 3600)
    if cache.get(per_address, 0) >= PER_ADDRESS_PER_HOUR or cache.get(total, 0) >= TOTAL_PER_HOUR:
        return False
    for key in (per_address, total):
        try:
            cache.incr(key)
        except ValueError:  # abgelaufen zwischen add und incr
            cache.set(key, 1, 3600)
    return True


def _altcha_ok(payload_b64: str) -> bool:
    from marketing.views import verify_altcha_payload

    if not verify_altcha_payload(payload_b64):
        return False
    # Jede gelöste Aufgabe gilt genau einmal.
    try:
        challenge = json.loads(base64.b64decode(payload_b64))["challenge"]
    except (KeyError, ValueError, TypeError):
        return False
    return cache.add(f"kontakt:altcha:{challenge}", True, _ALTCHA_REUSE_SECONDS)


# ── Zustellung ─────────────────────────────────────────────────────────────


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
    ``"gesendet"``, ``"ungueltig"``, ``"spamschutz"``, ``"zu-viele"``, ``"nicht-zustellbar"``.
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
    if not _within_rate_limit(request):
        logger.warning("Kontaktformular (%s): Grenze je Stunde erreicht", kind)
        return kind, form, "zu-viele"

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
