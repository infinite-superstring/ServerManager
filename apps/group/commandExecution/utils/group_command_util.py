from apps.group.commandExecution.models import Cluster_Execute
from apps.group.group_task.models import GroupTask
from apps.group.group_task.utils import group_task_util
from apps.group.manager.models import Node_Group


def getCluster_Execute_by_uuid(uuid) -> Cluster_Execute:
    return Cluster_Execute.objects.filter(uuid=uuid).first()


def create_temp_task(base_path: str, group: Node_Group, shell: str, uuid: str) -> GroupTask:
    task = GroupTask()
    task.name = "集群指令:" + str(uuid)
    task.uuid = uuid
    task.command = shell
    task.exec_type = 'interval'
    task.exec_count = 1
    task.interval = 1
    task.node_group = group
    task.exec_path = base_path
    task.enable = True
    return task


def executeGroupCommand(task_info: Cluster_Execute):
    task = create_temp_task(task_info.base_path, task_info.group, task_info.shell, task_info.uuid)
    group_task_util.handle_change_task(t='add', task=task, group=task.node_group)
    pass
