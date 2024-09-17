from django.apps import AppConfig


class GrantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'grants_management'

    def ready(self):
        import grants_management.signals