from django.db.models import Model
from django.forms import model_to_dict
from django.http import HttpRequest

from apps.task.utils.taskUtil import byUserIDGetAttendanceState, createAttendance
from util.Response import ResponseJson


def getList(req: HttpRequest):
    """
    获取任务列表
    """
    return ResponseJson({"status": 1, "msg": "获取任务列表成功"})


def attendanceCheckIn(req: HttpRequest):
    """
    签到
    """
    if req.method != 'POST':
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user_id = req.session.get("userID")
    status = byUserIDGetAttendanceState(user_id)
    if status:
        return ResponseJson({"status": 0, "msg": "今天已经签到过了"})
    else:
        createAttendance(user_id)
        return ResponseJson({"status": 1, "msg": "签到成功"})


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
