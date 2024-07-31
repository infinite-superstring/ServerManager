from asgiref.sync import sync_to_async
from django.apps import apps
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.node_manager.entity.alarm_setting import AlarmSetting, cpu, memory, network, disk
from apps.node_manager.models import Node, Node_BaseInfo, Node_DiskPartition, Node_UsageData, Node_AlarmSetting, \
    Node_Event
from apps.group.manager.models import Node_Group
from apps.node_manager.utils.groupUtil import node_group_id_exists, get_node_group_by_id
from apps.user_manager.models import User
from apps.permission_manager.util.permission import groupPermission
from util.passwordUtils import verify_password
from util.logger import Log

config = apps.get_app_config('setting').get_config


def node_name_exists(node_name) -> bool:
    """检查节点名是否存在"""
    return Node.objects.filter(name=node_name).exists()


def node_uuid_exists(node_uuid) -> bool:
    """检查节点UUID是否存在"""
    return Node.objects.filter(uuid=node_uuid).exists()


def get_node_by_uuid(node_uuid) -> Node:
    """根据节点UUID获取节点实例"""
    return Node.objects.get(uuid=node_uuid)


def get_node_by_name(node_name) -> Node:
    """根据节点名获取节点实例"""
    return Node.objects.get(name=node_name)


def get_node_count() -> int:
    """获取节点数量"""
    return Node.objects.count()


def get_node_online_count() -> int:
    """获取在线节点数量"""
    return Node_BaseInfo.objects.filter(online=True).count()


def get_node_offline_count() -> int:
    """获取离线节点数量"""
    return get_node_count() - Node_BaseInfo.objects.filter(online=True).count()


def get_node_warning_count() -> int:
    """获取正在告警的节点数量"""
    return Node_Event.objects.filter(level__in=["Warning", "Error"]).filter(end_time=None).count()


def get_user_node_count(user: User) -> int:
    """获取用户可用的节点数量"""
    return filter_user_available_nodes(user).count()


def get_user_node_online_count(user: User) -> int:
    """获取用户可用的在线节点数量"""
    return filter_user_available_nodes(user, Node.objects.filter(node_baseinfo__online=True)).count()


def get_user_node_offline_count(user: User) -> int:
    """获取用户可用的离线节点数量"""
    return get_user_node_count(user) - filter_user_available_nodes(user, Node.objects.filter(node_baseinfo__online=True)).count()


def get_user_node_warning_count(user: User) -> int:
    """获取用户可用的正在告警的节点数量"""
    node_uuids = filter_user_available_nodes(user).values_list('uuid')
    Node_Event.objects.filter(level__in=["Warning", "Error"]).filter(end_time=None).filter()
    return Node_Event.objects.filter(level__in=["Warning", "Error"]).filter(end_time=None).filter(
        node_id__in=[u for u in node_uuids[0]]).count()


def node_set_group(node_uuid, group_id) -> bool:
    if not node_group_id_exists(group_id):
        Log.error('Node Group does not exist')
        return False
    if not node_uuid_exists(node_uuid):
        Log.error("Node UUID does not exist")
        return False
    node = Node.objects.get(uuid=node_uuid)
    node.group = get_node_group_by_id(group_id)
    node.save()
    return True


def verify_node_token(node: Node, token) -> bool:
    """
    验证节点Token
    """
    if not isinstance(node, Node):
        return False

    return verify_password(node.token_hash, token, node.token_salt)


async def refresh_node_info(node: Node, data):
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    try:
        node_info = await Node_BaseInfo.objects.aget(node=node)
    except apps.node_manager.models.Node_BaseInfo.DoesNotExist:
        return False
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
    cpu_data = data.get('cpu')
    memory_data = data.get('memory')
    swap_data = data.get('swap')
    disk_data = data.get('disk')
    network_data = data.get('network')
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
        await sync_to_async(usage_data.cpu_core_usage.add)(
            await Node_UsageData.CpuCoreUsage.objects.acreate(
                core_index=index,
                usage=data
            ))
    for port_name in network_data["io"]:
        await sync_to_async(usage_data.network_usage.add)(
            await Node_UsageData.NetworkUsage.objects.acreate(
                port_name=port_name,
                bytes_sent=network_data["io"][port_name]["bytes_sent"],
                bytes_recv=network_data["io"][port_name]["bytes_recv"],
            )
        )
    await usage_data.asave()


async def update_disk_partition(node: Node, disk_partition: list):
    """
    更新磁盘分区表
    :param node: 节点对象
    :param disk_partition: 分区列表
    """
    node_info = await Node_BaseInfo.objects.aget(node=node)
    node_disk_list = Node_DiskPartition.objects.filter(node=node).all()
    await Node_DiskPartition.objects.filter(node=node).exclude(
        device__in=[i['device'] for i in disk_partition]).adelete()
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


async def read_performance_record(node: Node, start_time: str, end_time: str):
    """读取节点性能记录"""
    start_time = parse_datetime(start_time)
    end_time = parse_datetime(end_time)
    return Node_UsageData.objects.filter(node=node, timestamp__range=(start_time, end_time))


def init_node_alarm_setting(node: Node):
    node_default_alarm_setting = config().node_default_alarm_setting
    """初始化节点告警设置"""
    a_setting = Node_AlarmSetting.objects.create(
        node=node,
        enable=node_default_alarm_setting.enable,
        delay_seconds=node_default_alarm_setting.delay_seconds,
        network_rule=Node_AlarmSetting.NetworkAlarmRule.objects.create(
            module="Network",
            enable=node_default_alarm_setting.network__enable,
            send_threshold=node_default_alarm_setting.network__send_threshold,
            receive_threshold=node_default_alarm_setting.network__receive_threshold,
        )
    )
    a_setting.general_rules.add(
        Node_AlarmSetting.GeneralAlarmRule.objects.create(
            module="CPU",
            enable=node_default_alarm_setting.cpu__enable,
            threshold=node_default_alarm_setting.cpu__threshold
        )
    )
    a_setting.general_rules.add(
        Node_AlarmSetting.GeneralAlarmRule.objects.create(
            module="Memory",
            enable=node_default_alarm_setting.memory__enable,
            threshold=node_default_alarm_setting.memory__threshold
        )
    )
    return a_setting


def load_node_alarm_setting(node: Node):
    alarm_setting = Node_AlarmSetting.objects.filter(node=node).first()
    cpu_rule = alarm_setting.general_rules.filter(module="CPU").first() if alarm_setting else None
    memory_rule = alarm_setting.general_rules.filter(module="Memory").first() if alarm_setting else None
    network_rule = alarm_setting.network_rule if alarm_setting else None
    disk_rules = alarm_setting.disk_used_rules.all() if alarm_setting and alarm_setting.disk_used_rules.exists() else []
    setting: AlarmSetting = AlarmSetting(
        enable=alarm_setting.enable if alarm_setting else False,
        delay_seconds=alarm_setting.delay_seconds if alarm_setting else 360,
        interval=alarm_setting.interval if alarm_setting else 60,
        cpu=cpu(
            enable=cpu_rule.enable if cpu_rule else False,
            threshold=cpu_rule.threshold if cpu_rule else None
        ),
        memory=memory(
            enable=memory_rule.enable if memory_rule else False,
            threshold=memory_rule.threshold if memory_rule else None
        ),
        network=network(
            enable=network_rule.enable if network_rule else False,
            send_threshold=network_rule.send_threshold if network_rule else None,
            receive_threshold=network_rule.receive_threshold if network_rule else None
        ),
        disk=[disk(
            device=i.device.device,
            threshold=i.threshold
        ) for i in disk_rules]
    )
    return setting


def filter_user_available_nodes(user: User, base: Node = None):
    """
    过滤用户可用的节点
    :param user: 用户
    :param base: 基础查询
    """
    if base is None:
        result = Node.objects
    else:
        result = base
    # 查询创建者为自己的节点
    nodes_created_by_me = result.filter(creator=user)
    # 查询我作为节点负责人的节点
    nodes_i_lead = result.filter(group__leader=user)
    # 获取当前时间
    current_time = timezone.now().time()
    # 获取今天是星期几，0 表示星期一，6 表示星期日
    current_day_of_week = timezone.now().weekday()
    # 星期对应的字段名称
    weekday_field = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][current_day_of_week]
    query = Q(**{f"time_slot_recipient__{weekday_field}": True})
    node_group = Node_Group.objects.filter(
        time_slot_recipient__start_time__lte=current_time,
        time_slot_recipient__end_time__gte=current_time,
        time_slot_recipient__recipients=user
    ).filter(query)
    # 合并所有查询结果，去重
    return nodes_created_by_me.union(nodes_i_lead, result.filter(group__in=node_group))


def is_node_available_for_user(user, node):
    """
    检查用户当前是否可用该节点
    :param user: 用户实例
    :param node: 节点实例
    """
    if groupPermission(user.permission).check_group_permission("viewAllNode"):
        return True
    nodes = filter_user_available_nodes(user)
    if node not in nodes:
        return False
    return True


async def a_load_node_alarm_setting(node: Node) -> AlarmSetting:
    Log.debug("load node alarm setting")
    alarm_setting = await Node_AlarmSetting.objects.filter(node=node).afirst()
    cpu_rule = await alarm_setting.general_rules.filter(module="CPU").afirst() if alarm_setting else None
    memory_rule = await alarm_setting.general_rules.filter(module="Memory").afirst() if alarm_setting else None
    network_rule = await sync_to_async(lambda: alarm_setting.network_rule)() if alarm_setting else None
    setting: AlarmSetting = AlarmSetting(
        enable=alarm_setting.enable if alarm_setting else False,
        delay_seconds=alarm_setting.delay_seconds if alarm_setting else 360,
        interval=alarm_setting.interval if alarm_setting else 60,
        cpu=cpu(
            enable=cpu_rule.enable if cpu_rule else False,
            threshold=cpu_rule.threshold if cpu_rule else None
        ),
        memory=memory(
            enable=memory_rule.enable if memory_rule else False,
            threshold=memory_rule.threshold if memory_rule else None
        ),
        network=network(
            enable=network_rule.enable if network_rule else False,
            send_threshold=network_rule.send_threshold if network_rule else None,
            receive_threshold=network_rule.receive_threshold if network_rule else None
        ),
        disk=[disk(
            device=await sync_to_async(lambda: i.device.device)(),
            threshold=i.threshold
        ) async for i in alarm_setting.disk_used_rules.all()]
    )
    return setting
