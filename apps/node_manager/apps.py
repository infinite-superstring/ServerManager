from django.apps import AppConfig, apps
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
                i.online = False
                i.save()
        except Exception as e:
            Log.warning("重置节点在线状态失败!")
        Log.success("Node Manager: Initialization complete")

