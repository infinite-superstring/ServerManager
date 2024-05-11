from django.apps import AppConfig, apps
from util.logger import Log


class NodeManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.node_manager'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        Log.info("Node Manager: Initializing start")

    def ready(self):
        for i in apps.get_model("node_manager", "Node_BaseInfo").objects.all():
            i.online = False
            i.save()
        Log.success("Node Manager: Initialization complete")

