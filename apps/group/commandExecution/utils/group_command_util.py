from apps.group.commandExecution.models import Cluster_Execute
from apps.node_manager.utils.groupUtil import GroupUtil


def getCluster_Execute_by_uuid(uuid) -> Cluster_Execute:
    return Cluster_Execute.objects.filter(uuid=uuid).first()


def executeGroupCommand(task_info: Cluster_Execute):
    group_util = GroupUtil(task_info.group)
    group_util.send_event_to_all_nodes('run_shell', {
        'shell': task_info.shell,
        'task_uuid': str(task_info.uuid),
        'base_path': task_info.base_path
    })
