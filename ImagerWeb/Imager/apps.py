from django.apps import AppConfig


class ImagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Imager'
    
    def ready(self):
        from .signals import create_profile