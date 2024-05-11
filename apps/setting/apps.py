from django.apps import AppConfig
from util.logger import Log
from apps.setting.entity.Config import config

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

class SettingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.setting'
    __config = None
    __base_config = None

    def __init__(self, *args, **kwargs):
        super(SettingConfig, self).__init__(*args, **kwargs)
        Log.info("Setting: Initializing start")
        try:
            with open("configs/config.toml", "rb") as f:
                self.__base_config = tomllib.load(f)
                Log.success("基本配置文件加载完成")
        except Exception as err:
            Log.error(err)
            raise RuntimeError("基本配置文件加载失败，应用启动失败")

    def ready(self):
        from apps.setting.util.Config import loadConfig
        try:
            self.__config = config()
            self.__config = loadConfig(self.__config)
        except Exception as err:
            Log.error(f"从数据库加载配置失败！\n{err}")
        Log.success("Setting: Initialization complete")

    def get_base_config(self):
        return self.__base_config

    def get_config(self):
        return self.__config

    def update_config(self, config):
        self.__config = config
