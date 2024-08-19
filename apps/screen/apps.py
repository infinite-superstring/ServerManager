import os.path
from datetime import datetime

from django.apps import AppConfig, apps
from apps.screen.entity.ScreenCacheKey import ScreenCacheKey
from apps.screen.utils.CacheUtil import CacheUtil
from util.logger import Log


class ScreenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.screen'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

    def ready(self):
        """
        初始化缓存数据
        """
        self.cache_init()
        Log.success("Screen:Cache InitializationInProgress")
        # self.record_init()
        # Log.success("Screen:Record InitializationInProgress")
        Log.success("Screen:Initialization complete")

    @Log.catch
    def cache_init(self):
        #  告警 数量和类型 初始化
        from apps.screen.utils import screenUtil
        screenUtil.reset_cache()

    def record_init(self):
        # 初始化各节点运行记录
        from apps.screen.utils import screenUtil
        # screenUtil.pack_node_data()
