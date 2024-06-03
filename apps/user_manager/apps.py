from django.apps import AppConfig
from django.apps import apps
from util.logger import Log


class UserManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_manager'
    disable_user_list: list[str] = []

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("User Manager: Initializing start")

    def ready(self):
        try:
            self.__load_disable_user_list()
        except Exception as e:
            Log.error(f"load disable user list error: {e}")
        Log.success("User Manager: Initialization complete")

    def __load_disable_user_list(self):
        disable_user = apps.get_model('user_manager', 'User').objects.filter(disable=True)
        self.disable_user_list = [user.id for user in disable_user]
        Log.debug(self.disable_user_list)