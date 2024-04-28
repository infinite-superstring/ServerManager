from django.apps import AppConfig
from util.logger import Log


class PermissionManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permission_manager'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("Permission Manager: Initializing start")

    def ready(self):
        Log.success("Permission Manager: Initialization complete")
