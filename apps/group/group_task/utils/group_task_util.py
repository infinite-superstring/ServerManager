import hashlib
import re
import uuid
from datetime import datetime
from uuid import UUID

from asgiref.sync import async_to_sync
from django.db.models import QuerySet

from apps.group.group_task.models import GroupTask_Cycle, GroupTask
from apps.group.manager.models import Node_Group
from apps.group.manager.utils.groupUtil import GroupUtil

day_mapping = {
    1: 'monday',
    2: 'tuesday',
    3: 'wednesday',
    4: 'thursday',
    5: 'friday',
    6: 'saturday',
    7: 'sunday',
}


def createCycle(cycle: dict, g_task):
    """
    创建周期对象
    """
    if not cycle:
        return GroupTask_Cycle()

    cycle_obj = GroupTask_Cycle()
    cycle_obj.time = cycle.get('time', '00:00') if cycle.get('time') != '' else '00:00'
    cycle_obj.group_task = g_task
    weeks = cycle.get('week', [])
    for day in weeks:
        if day in day_mapping:
            setattr(cycle_obj, day_mapping[day], True)
    return cycle_obj


def str_time_to_second(str_time: str) -> int:
    # 将字符串转换为datetime对象
    time_obj = datetime.strptime(str_time, "%H:%M")

    # 从datetime对象中获取time对象
    time_only = time_obj.time()

    # 计算从零点到该时间的总秒数
    total_seconds = time_only.hour * 3600 + time_only.minute * 60
    return total_seconds


async def getCycle(uuids) -> dict:
    """
    根据 集群任务ID获取 任务周期对象
    """
    cycle_obj: GroupTask_Cycle = await GroupTask_Cycle.objects.filter(group_task__uuid=uuids).afirst()
    if not cycle_obj:
        return {}
    week = []
    for i in range(1, 8):
        if getattr(cycle_obj, day_mapping[i]):
            week.append(i)
    return {
        'time': cycle_obj.time.strftime('%H:%M'),
        'week': week
    }


async def by_type_get_exec_time(task: GroupTask):
    """
    根据 任务类型 获取执行时间
    """

    if task.exec_type == 'cycle':
        cycle = await getCycle(task.uuid)
        str_exec_time = cycle.get('time')
        return str_time_to_second(str_exec_time)
    if task.exec_type == 'interval':
        return task.interval
    if task.exec_type == 'date-time':
        return task.that_time.timestamp()
    return None


async def get_the_task_of_node(task: GroupTask = None):
    """
    封装 节点 需要的 集群任务数据
    """
    exec_time = await by_type_get_exec_time(task)
    weeks = []
    if task.exec_type == 'cycle':
        weeks = (await getCycle(task.uuid)).get('week', [])
    return {
        'name': task.name,
        'uuid': str(task.uuid),
        'type': task.exec_type,
        'exec_path': task.exec_path,
        'time': exec_time,
        'exec_count': task.exec_count,
        'shell': task.command,
        'week': weeks,
        # 'relative_utc': ''
    }


def handle_change_task(t, task_uuid: UUID = None, group=None, task: GroupTask = None):
    """
    任务变更时向所有节点发送变更事件
    add -> 需要 任务实例 任务所在组
    remove -> 需要 任务uuid 所在组
    reload -> 需要 任务uuid 所在组
    """
    data: dict[str, str | dict]
    # 检查任务是否不需要推送
    if task and t != 'remove' and task_should_not_push(task):
        return
    if t == 'add':
        group: Node_Group = task.node_group
        data = {
            'action': t,
            'data': async_to_sync(get_the_task_of_node)(task=task)
        }
        group_task_change(group, data)
        return
    elif t == 'remove':
        data = {
            'action': t,
            'data': str(task_uuid)
        }
        group_task_change(group, data)
    elif t == 'reload':
        data = {
            'action': t,
            'data': async_to_sync(get_the_task_of_node)(task=task)
        }
        group_task_change(group, data)


def group_task_change(group: Node_Group, data):
    GroupUtil(group=group).send_event_to_all_nodes(event='group_task_change', data=data)


def task_should_not_push(task: GroupTask) -> bool:
    """
    判断任务是否不需要推送
    """
    if not task.enable:
        return True  # 如果任务被禁用，直接返回True，表示不应该推送
    if task.exec_type == 'date-time':
        return task.that_time.timestamp() < datetime.now().timestamp()  # 如果是定时任务，检查是否已经过去
    if task.exec_count is not None:
        return int(task.exec_count) <= 0

    # 如果不是定时任务，或者定时任务还没到时间，这里可以添加其他条件，或者直接返回False
    return False


def by_key_get_uuid(key: str) -> UUID:
    """
    根据 特定 key 获取 uuid 非随机
    """
    # 将键转换为字节
    key_bytes = key.encode('utf-8')
    # 计算 MD5 哈希
    hash_object = hashlib.md5()
    hash_object.update(key_bytes)
    hash_bytes = hash_object.digest()
    # 从哈希字节生成 UUID
    generated_uuid = uuid.UUID(bytes=hash_bytes)
    return generated_uuid


def write_file(file_path, content):
    with open(file_path, 'a+', encoding='utf-8') as file:
        file.write(content)


def command_legal(command: str, command_list: list[str]):
    """
    检查命令是否合法
    """
    for c in command_list:
        if not c:
            continue
        if re.match(c, command):
            return False
    for c in command_list:
        if not c:
            continue
        if c in command:
            return False
    return True


def is_uuid(uuid_str: str):
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def filer_page_result(
        r_l: QuerySet[GroupTask],
        enable: bool | None = None,
        exec_type: str | None = None,
        node_group: int = None
):
    """
    过滤结果
    """
    if enable is not None:
        r_l = r_l.filter(enable=enable)
    if exec_type:
        r_l = r_l.filter(exec_type=exec_type)
    if node_group:
        r_l = r_l.filter(node_group__id=node_group)
    return r_l
