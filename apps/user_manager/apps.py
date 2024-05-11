from django.apps import AppConfig
from util.logger import Log


class UserManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_manager'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("User Manager: Initializing start")

    def ready(self):
        Log.success("User Manager: Initialization complete")
