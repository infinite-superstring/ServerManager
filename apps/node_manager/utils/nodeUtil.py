from apps.node_manager.models import Node, Node_BaseInfo, Node_DiskPartition
from util.passwordUtils import verify_password


def verify_node_token(node: Node, token):
    """
    验证节点Token
    """
    if not isinstance(node, Node):
        return False

    return verify_password(node.token_hash, token, node.token_salt)


def refresh_node_info(node: Node, data):
    node_info = Node_BaseInfo(node=node)


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
