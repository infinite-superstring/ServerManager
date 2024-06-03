from django.apps import AppConfig
from util.logger import Log
from apps.setting.entity.Config import config

class SettingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.setting'
    __config = None

    def __init__(self, *args, **kwargs):
        super(SettingConfig, self).__init__(*args, **kwargs)
    def ready(self):
        from apps.setting.util.Config import loadConfig
        try:
            self.__config = config()
            self.__config = loadConfig(self.__config)
        except Exception as err:
            Log.error(f"从数据库加载配置失败！\n{err}")
        Log.success("Setting: Initialization complete")

    def get_config(self):
        return self.__config

    def update_config(self, config):
        self.__config = config
