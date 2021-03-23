from django.apps import AppConfig


class RemConfig(AppConfig):
    name = 'rem'

    def ready(self):
        import rem.signals
