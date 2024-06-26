from django.db.models import Model
from django.forms import model_to_dict
from django.http import HttpRequest

from apps.task.models import Task
from apps.task.utils.taskUtil import byUserIDGetAttendanceState, createAttendance, year_month_to_start_and_end_time, \
    randomColor
from util.Response import ResponseJson


def getList(req: HttpRequest):
    """
    获取任务列表
    """
    return ResponseJson({"status": 1, "msg": "获取任务列表成功", 'data': []})


def getDuty(req: HttpRequest):
    """
    获取所有用户的值班记录（每日签到记录）
    """
    if req.method != 'GET':
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
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
    )

    result = []
    for task in tasks:
        result.append({
            'userId': task.target_user.id,
            'pic': task.target_user.avatar,
            'title': task.target_user.realName,
            'start': task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end': task.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            # 'color': randomColor()
        })

    return ResponseJson({"status": 1, "msg": "获取值班记录成功", 'data': result})


def attendanceCheckIn(req: HttpRequest):
    """
    签到
    """
    if req.method != 'POST':
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user_id = req.session.get("userID")
    status = byUserIDGetAttendanceState(user_id)
    if status:
        return ResponseJson({"status": 1, "msg": "今天已经签到过了", 'data': False})
    else:
        task = createAttendance(user_id)
        return ResponseJson({"status": 1, "msg": "签到成功", 'date': model_to_dict(task)})


def getCheckInStatus(req: HttpRequest):
    """
    获取签到状态
    """
    if req.method != 'GET':
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user_id = req.session.get("userID")
    status = byUserIDGetAttendanceState(user_id)
    if status:
        return ResponseJson({"status": 1, "msg": "今天已经签到过了", "data": model_to_dict(status)})
    else:
        return ResponseJson({"status": 1, "msg": "今天还没有签到"})
