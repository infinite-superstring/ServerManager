from django.http import HttpRequest

from apps.group_task.models import GroupTask
from apps.group_task.utils.group_task_util import createCycle
from util import result
from util.Request import RequestLoadJson


def create_group_task(req: HttpRequest):
    """
    创建集群任务
    """
    if req.method != 'POST':
        return result.api_error('请求方式错误', http_code=405)
    try:
        data = RequestLoadJson(req)
    except:
        return result.api_error('请求数据错误', http_code=400)
    taskName: str = data.get('taskName', '')
    group: int = data.get('group', 0)
    execCount: str = data.get('execCount', '')
    execType: str = data.get('execType', '')
    execTime: str = data.get('execTime', '')
    execInterval: str = data.get('execInterval', '')
    if not taskName or not group or not execCount or not execType:
        return result.error('请将参数填写完整')
    g_task: GroupTask = GroupTask()
    g_task.name = taskName
    g_task.node_group_id = group
    g_task.exec_count = execCount
    g_task.exec_type = execType
    if execType == 'date-time':
        if not execTime:
            return result.error('请选择执行时间')
        g_task.that_time = execTime
    if execType == 'interval':
        if not execInterval:
            return result.error('请选择执行间隔')
        g_task.interval = execInterval
    if execType == 'cycle':
        execCycle: dict = data.get('execCycle', {})
        if not execCycle:
            return result.error('请选择执行周期')
        g_task.cycle = createCycle(execCycle)
    return result.success()
