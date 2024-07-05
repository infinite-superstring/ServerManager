from asgiref.sync import async_to_sync
from django.db.models import QuerySet

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


async def getCycle(id):
    """
    根据 集群任务ID获取 任务周期对象
    """
    cycle_obj: GroupTask_Cycle = await GroupTask_Cycle.objects.filter(group_task_id=id).afirst()
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


async def by_uuid_get_task(uuids: str = None, group: Node_Group = None):
    """
    根据 uuid 获取任务
    """

    group_tasks = []
    if not group:
        group = await Node_Group.objects.aget(node__uuid=uuids)
    if not group:
        return group_tasks
    group_task = GroupTask.objects.filter(node_group=group)
    if not await group_task.aexists():
        return group_tasks
    async for task in group_task:
        if not task.enable:
            continue
        group_tasks.append({
            'name': task.name,
            'exec_type': task.exec_type,
            'interval': task.interval,
            'that_time': task.that_time.strftime('%Y-%m-%d %H:%M:%S') if task.that_time else '',
            'exec_count': task.exec_count,
            'command': task.command,
            'cycle': await getCycle(task.uuid)
        })
    return group_tasks


def handle_change_task():
    """
    任务变更时向所有节点发送变更事件
    """
    group_tasks = GroupTask.objects.all()
    group_list = [g.node_group for g in group_tasks]
    for group in group_list:
        group_util = GroupUtil(group)
        tasks = async_to_sync(by_uuid_get_task)(group=group)
        print(tasks)
        group_util.send_event_to_all_nodes('group_task_change', {'tasks': tasks})
