from django.apps import AppConfig
from util.logger import Log


class FileManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file_manager'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("File manager: Initializing start")

    def ready(self):
        Log.success("File manager: Initialization complete")