from datetime import datetime
from uuid import UUID

from asgiref.sync import async_to_sync
from django.db.models import QuerySet
from django.forms import model_to_dict

from apps.group_task.models import GroupTask_Cycle, GroupTask
from apps.node_manager.models import Node, Node_Group
from apps.node_manager.utils.groupUtil import GroupUtil

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


async def get_the_task_of_node(node_uuid: str = None, group: Node_Group = None, task_uuid: str = None):
    """
    根据 uuid 获取任务
    """
    group_tasks = []
    group_task: QuerySet[GroupTask] = QuerySet[GroupTask]()
    if node_uuid:
        group = await Node_Group.objects.aget(node__uuid=node_uuid)
        group_task = GroupTask.objects.filter(node_group=group)
    if group:
        group_task = GroupTask.objects.filter(node_group=group)
    if task_uuid:
        group_task = GroupTask.objects.filter(uuid=task_uuid)
    if not await group_task.aexists():
        return group_tasks
    async for task in group_task:
        if not task.enable:
            continue
        exec_time = await by_type_get_exec_time(task)
        weeks = []
        if task.exec_type == 'cycle':
            weeks = (await getCycle(task.uuid)).get('week')
        group_tasks.append({
            'name': task.name,
            'uuid': str(task.uuid),
            'type': task.exec_type,
            'exec_path': task.exec_path,
            'time': exec_time,
            'exec_count': task.exec_count,
            'shell': task.command,
            'week': weeks
        })
    return group_tasks


def handle_change_task(t, task_uuid: UUID = None, group=None, task: GroupTask = None):
    """
    任务变更时向所有节点发送变更事件
    """
    data: dict[str, str | dict]
    if t == 'add':
        group: Node_Group = task.node_group
        data = {
            'action': t,
            'data': async_to_sync(get_the_task_of_node)(task_uuid=task.uuid)
        }
        group_task_change(group, data)
        print(data)
        return
    elif t == 'remove':
        data = {
            'action': t,
            'data': str(task_uuid)
        }
        group_task_change(group, data)
        print(data)
    elif t == 'reload':
        data = {
            'action': t,
            'data': async_to_sync(get_the_task_of_node)(task_uuid=task.uuid)
        }
        print(data)
        group_task_change(group, data)


def group_task_change(group: Node_Group, data):
    GroupUtil(group=group).send_event_to_all_nodes(event='group_task_change', data=data)
