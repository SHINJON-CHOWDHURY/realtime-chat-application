from django.apps import AppConfig


class ChatclearConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatclear'

    def ready(self):
        import chatclear.signals