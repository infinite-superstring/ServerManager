from django.apps import AppConfig
from util.logger import Log

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("Auth: Initializing start")

    def ready(self):
        Log.success("Auth: Initialization complete")