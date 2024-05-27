from asgiref.sync import sync_to_async

from apps.node_manager.models import Node, Node_BaseInfo, Node_DiskPartition, Node_UsageData
from util.passwordUtils import verify_password
from util.logger import Log

def verify_node_token(node: Node, token):
    """
    验证节点Token
    """
    if not isinstance(node, Node):
        return False

    return verify_password(node.token_hash, token, node.token_salt)


async def refresh_node_info(node: Node, data):
    Log.debug('refresh_node_info')
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    node_info = await Node_BaseInfo.objects.aget(node=node)
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
        await node_info.asave()


async def save_node_usage_to_database(node: Node, data):
    Log.debug('save_node_usage_to_database')
    cpu_data = data.get('cpu')
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    disk_data = data.get('disk')
    loadavg_data = data.get('loadavg')

    loadavg = await Node_UsageData.Loadavg.objects.acreate(
        one_minute=loadavg_data[0],
        five_minute=loadavg_data[1],
        fifteen_minute=loadavg_data[2]
    )
    usage_data = await Node_UsageData.objects.acreate(
        node=node,
        cpu_usage=cpu_data['usage'],
        memory_used=memory_data['used'],
        swap_used=swap_data['used'],
        disk_io_read_bytes=disk_data['io']['read_bytes'],
        disk_io_write_bytes=disk_data['io']['write_bytes'],
        system_loadavg=loadavg
    )
    for index, data in enumerate(cpu_data["core_usage"]):
        # print(await sync_to_async(usage_data.cpu_core_usage)())
        await sync_to_async(usage_data.cpu_core_usage.add)(await Node_UsageData.CpuCoreUsage.objects.acreate(core_index=index, usage=data))

    # for core_usage_item in core_usage:
    #     await usage_data.cpu_core_usage.add(core_usage_item)
    await usage_data.asave()


async def update_disk_partition(node: Node, disk_partition: list):
    """
    更新磁盘分区表
    :param node: 节点对象
    :param disk_partition: 分区列表
    """
    Log.debug('update_disk_partition')
    node_info = await Node_BaseInfo.objects.aget(node=node)
    node_disk_list = Node_DiskPartition.objects.filter(node=node).all()
    await Node_DiskPartition.objects.filter(node=node).exclude(device__in=[i['device'] for i in disk_partition]).adelete()
    for index, disk_data in enumerate(disk_partition):
        if not await node_disk_list.filter(device=disk_data['device']).aexists():
            disk = await Node_DiskPartition.objects.acreate(node=node, device=disk_data['device'])
            await sync_to_async(node_info.disk_list.add)(disk)
        else:
            disk = await node_disk_list.filter(device=disk_data['device']).afirst()
        disk.mount_point = disk_data['mount_point']
        disk.fs_type = disk_data['fs_type']
        disk.total = disk_data['total']
        disk.used = disk_data['used'] if disk_data.get("used") else 0
        await disk.asave()
    await node_info.asave()
