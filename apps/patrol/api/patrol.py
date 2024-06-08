from django.http import HttpRequest

from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


def addARecord(req: HttpRequest):
    if req.method != "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        data = RequestLoadJson(req)
        Log.debug(data)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    else:
        data.get("")
    return
