from django.apps import AppConfig
from util.logger import Log


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("Audit: Initializing start")

    def ready(self):
        Log.success("Audit: Initialization complete")
