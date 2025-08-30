from django.apps import AppConfig


class AllianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alliance'

    def ready(self):
        # register signal handlers
        import alliance.signals  
