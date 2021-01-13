from django.apps import AppConfig


class CorporationsConfig(AppConfig):
    name = 'corporations'

    def ready(self):
        import corporations.signals
