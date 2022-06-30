from django.apps import AppConfig


class OutpatientAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'outpatient_app'

    def ready(self):
        from .signals import QueueSignal

