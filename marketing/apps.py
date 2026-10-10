from django.apps import AppConfig


class MarketingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "marketing"
    verbose_name = "Marketing Website"

    def ready(self):
        from marketing import signals

        signals.verbinden()
