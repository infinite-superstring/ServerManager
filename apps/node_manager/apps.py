import os.path
from datetime import datetime

from django.apps import AppConfig, apps
from django.core.cache import cache
from util.logger import Log


class NodeManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.node_manager'
    terminal_record_save_dir: str
    group_task_result_save_dir: str
    group_command_result_save_dir: str

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        data_save_base_path = os.path.join(os.getcwd(), "data")

        def __create_dir(dir_name) -> str:
            if not os.path.exists(os.path.join(data_save_base_path, dir_name)):
                os.mkdir(os.path.join(data_save_base_path, dir_name))
            return str(os.path.join(data_save_base_path, dir_name))

        self.terminal_record_save_dir = __create_dir('terminal_session_record')
        self.group_task_result_save_dir = __create_dir('group_task_run_result')
        self.group_command_result_save_dir = __create_dir('group_command_run_result')
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
            Log.warning(f"重置节点在线状态失败! Error Message: {e}")
        try:
            for i in apps.get_model("node_manager", "Node_Event").objects.filter(end_time=None).all():
                i.end_time = datetime.now()
                i.save()
            Log.info("Closed all node events")
        except Exception as e:
            Log.warning(f"关闭节点事件失败! Error Message: {e}")
        from apps.node_manager.tasks import tasks
        task = tasks()
        task.start()
        Log.success("Node Manager: Initialization complete")
