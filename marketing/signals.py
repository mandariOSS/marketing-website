"""Signale der Website: veröffentlichte und zurückgezogene Seiten an IndexNow melden (marketing/indexnow.py)."""

from __future__ import annotations

from django.db import transaction
from wagtail.signals import page_published, page_unpublished

from marketing import indexnow


def _melden(sender, instance, **kwargs):
    if not indexnow.schluessel():
        return
    adressen = indexnow.seitenadressen(instance)
    # Erst nach dem Speichern: Die Suchmaschine soll den neuen Stand abholen, nicht den alten
    transaction.on_commit(lambda: indexnow.melden(adressen))


def verbinden():
    page_published.connect(_melden, dispatch_uid="marketing_indexnow_veroeffentlicht")
    page_unpublished.connect(_melden, dispatch_uid="marketing_indexnow_zurueckgezogen")
