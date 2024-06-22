from django.http import HttpRequest
from apps.task.models import Task
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


def getList(req: HttpRequest):
    """
    获取任务列表
    """


def attendanceCheckIn(req: HttpRequest):
    """
    签到
    """
    if req.method != 'POST':
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    userId = req.session.get("userID")



def getCheckInStatus(req: HttpRequest):
    """
    获取签到状态
    """
