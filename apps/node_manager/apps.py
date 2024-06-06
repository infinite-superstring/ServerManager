from django.apps import AppConfig, apps
from django.core.cache import cache
from django.core.signals import request_finished

from util.logger import Log


class NodeManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.node_manager'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("Node Manager: Initializing start")

    def ready(self):
        try:
            for i in apps.get_model("node_manager", "Node_BaseInfo").objects.all():
                if i.online:
                    i.online = False
                    i.save()
                    cache.delete(f"node_{i.node.uuid}_usage_last_update_time")
                    cache.delete(f"node_client_online_{i.node.uuid}")
        except Exception as e:
            Log.warning(f"重置节点在线状态失败!\n{e}")
        Log.success("Node Manager: Initialization complete")

