from apps.node_manager.models import Node, Node_BaseInfo, Node_DiskPartition, Node_UsageData
from util.passwordUtils import verify_password


def verify_node_token(node: Node, token):
    """
    验证节点Token
    """
    if not isinstance(node, Node):
        return False

    return verify_password(node.token_hash, token, node.token_salt)


def refresh_node_info(node: Node, data):
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    node_info = Node_BaseInfo.objects.get(node=node)
    if not node_info:
        raise RuntimeError("Node does not exist.")
    flag = False
    if node_info.memory_total != memory_data['total']:
        flag = True
        node_info.memory_total = memory_data['total']
    if node_info.swap_total != swap_data['total']:
        flag = True
        node_info.swap_total = swap_data['total']
    if flag:
        node_info.save()


def save_node_usage_to_database(node: Node, data):
    cpu_data = data.get('cpu')
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    disk_data = data.get('disk')
    loadavg_data = data.get('loadavg')
    
    core_usage = [Node_UsageData.CpuCoreUsage.objects.create(core_index=index, usage=data) for
                  index, data in enumerate(cpu_data["core_usage"])]
    loadavg = Node_UsageData.Loadavg.objects.create(one_minute=loadavg_data[0], five_minute=loadavg_data[1],
                                                    fifteen_minute=loadavg_data[2])
    usage_data = Node_UsageData.objects.create(
        node=node,
        cpu_usage=cpu_data['usage'],
        memory_used=memory_data['used'],
        swap_used=swap_data['used'],
        disk_io_read_bytes=disk_data['io']['read_bytes'],
        disk_io_write_bytes=disk_data['io']['write_bytes'],
        system_loadavg=loadavg
    )
    for core_usage_item in core_usage:
        usage_data.cpu_core_usage.add(core_usage_item)
    usage_data.save()

def update_disk_partition(node: Node, disk_partition: list):
    """
    更新磁盘分区表
    :param node: 节点对象
    :param disk_partition: 分区列表
    """
    node_info = Node_BaseInfo.objects.get(node=node)
    node_disk_list = Node_DiskPartition.objects.filter(node=node).all()
    Node_DiskPartition.objects.filter(node=node).exclude(device__in=[i['device'] for i in disk_partition]).delete()
    for index, disk_data in enumerate(disk_partition):
        if not node_disk_list.filter(device=disk_data['device']).exists():
            disk = Node_DiskPartition.objects.create(node=node, device=disk_data['device'])
            node_info.disk_list.add(disk)
        else:
            disk = node_disk_list.filter(device=disk_data['device']).first()
        disk.mount_point = disk_data['mount_point']
        disk.fs_type = disk_data['fs_type']
        disk.total = disk_data['total']
        disk.used = disk_data['used'] if disk_data.get("used") else 0
        disk.save()
    node_info.save()
