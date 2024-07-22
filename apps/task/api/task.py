from datetime import datetime

from django.forms import model_to_dict
from django.http import HttpRequest
from django.db.models import Count
from django.views.decorators.http import require_GET, require_POST

from apps.permission_manager.util.api_permission import api_permission
from apps.task.models import Task
from apps.task.utils.taskUtil import byUserIDGetAttendanceState, createAttendance, year_month_to_start_and_end_time, \
    get_current_time
from apps.user_manager.models import User
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


def getList(req: HttpRequest):
    """
    获取任务列表
    """
    return ResponseJson({"status": 1, "msg": "获取任务列表成功", 'data': []})


@require_GET
@api_permission("viewDuty")
def getDuty(req: HttpRequest):
    """
    获取所有用户的值班记录（每日签到记录）
    """
    str_year_and_month = req.GET.get('year_and_month')
    if str_year_and_month is None:
        return ResponseJson({"status": 0, "msg": "参数错误"}, 400)
    # 将字符串格式化为 日期
    start_time, end_time = year_month_to_start_and_end_time(str_year_and_month)
    tasks = Task.objects.filter(
        start_time__gte=start_time,
        end_time__lte=end_time,
        type=0,
        status=1
    ).values('start_time', 'end_time', 'target_user').annotate(count=Count('target_user')).filter(count__lte=15)

    result = []
    for task in tasks:
        target_user = User.objects.get(id=task['target_user'])
        result.append({
            'userId': target_user.id,
            'pic': target_user.avatar,
            'title': target_user.realName,
            'start': task['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
            'end': task['end_time'].strftime("%Y-%m-%d %H:%M:%S"),
            # 'color': randomColor()
        })

    return ResponseJson({"status": 1, "msg": "获取值班记录成功", 'data': result})


@require_POST
def attendanceCheckIn(req: HttpRequest):
    """
    签到
    """
    try:
        # 如果请求体为空，则不解析
        if req.body == b'':
            data = {}
        else:
            data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    user_id = data.get('userId', None)
    timestamp = data.get('timestamp', None)
    if user_id is None:  # 不是补签状态
        user_id = req.session.get("userID")
        timestamp = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    #  当前时间戳
    currTimestamp = get_current_time()
    if timestamp.timestamp() > currTimestamp.timestamp():
        return ResponseJson({"status": 1, "msg": "签到时间不能大于当前时间", 'data': False})

    status = byUserIDGetAttendanceState(user_id, timestamp)
    if status:
        return ResponseJson({"status": 1, "msg": "已经签到过了", 'data': False})
    else:
        task = createAttendance(user_id, timestamp)
        return ResponseJson({"status": 1, "msg": "签到成功", 'date': model_to_dict(task)})


@require_GET
def getCheckInStatus(req: HttpRequest):
    """
    获取签到状态
    """
    user_id = req.session.get("userID")
    time = get_current_time()
    status = byUserIDGetAttendanceState(user_id, time)
    if status:
        return ResponseJson({"status": 1, "msg": "今天已经签到过了", "data": model_to_dict(status)})
    else:
        return ResponseJson({"status": 1, "msg": "今天还没有签到"})
