from django.forms import model_to_dict
from django.http import HttpRequest

from apps.web_status.models import Web_Status
from apps.web_status.utils.webUtil import is_valid_host, is_valid_port, hostIsExist
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


def getList(req: HttpRequest):
    """
    获取监控网站列表
    """
    if req.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    page = int(req.GET.get("page", 1))
    pageSize = int(req.GET.get("pageSize", 10))
    name = req.GET.get("name", "")
    web_list = Web_Status.objects.filter(title__contains=name, host__contains=name, description__contains=name)
    result = []
    for web in web_list:
        result.append(model_to_dict(web))

    return ResponseJson({"status": 1, "msg": "获取成功", "data": {"list": result, }})


def addWeb(req: HttpRequest):
    """
    添加监控站点
    """
    if req.method != "POST":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    title = data['title']
    host = data['host']
    description = data['description']
    if not is_valid_host(host):
        return ResponseJson({"status": 0, "msg": "主机地址不合法"})
    if hostIsExist(host):
        return ResponseJson({"status": 0, "msg": "主机地址已存在"})
    web = Web_Status.objects.create(title=title, host=host, description=description)
    return ResponseJson({"status": 1, "msg": "添加成功", "data": {"id": web.id}})
