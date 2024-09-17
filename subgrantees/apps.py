from django.apps import AppConfig


class SubgranteesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subgrantees'

    def ready(self):
        import subgrantees.signals



