from django.apps import AppConfig


class LisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lis'

    def ready(self) -> None:
        from .signals import set_barcode
        return super().ready()
