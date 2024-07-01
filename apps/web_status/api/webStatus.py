from datetime import datetime

from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.web_status.models import Web_Site, Web_Site_Log
from apps.web_status.utils.webUtil import is_valid_host, hostIsExist
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
    web_list = Web_Site.objects.filter(title__contains=name, host__contains=name, description__contains=name)
    result = []
    for web in web_list:
        runtime: Web_Site_Log = cache.get(f'web_status_log_{web.id}') if cache.get(
            f'web_status_log_{web.id}') else Web_Site_Log()
        result.append({
            "id": web.id,
            "title": web.title,
            "host": web.host,
            "status": runtime.status,
            "delay": int(runtime.delay),
            "online": str(runtime.status).startswith("2"),
            "description": web.description,
        })

    return ResponseJson({"status": 1, "msg": "获取成功", "data": {"list": result, }})


def getRuntime(req: HttpRequest):
    if req.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    logs = Web_Site_Log.objects.all()
    web_group = logs.only('web').distinct()
    web_host = [web.web.host for web in web_group]
    result = {}
    for host_key in web_host:
        times: QuerySet[(datetime,)] = logs.filter(web__host=host_key).values_list('time')
        datas: QuerySet[(int,)] = logs.filter(web__host=host_key).values_list('delay')
        result[host_key] = {
            'time': [str(time[0].strftime("%H:%M:%S")) for time in times],
            'data': [str(data[0]) for data in datas]
        }
    return ResponseJson({"status": 1, "msg": "获取成功", "data": result})


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
    web = Web_Site.objects.create(title=title, host=host, description=description)
    cache.delete(f'WebStatusClient_web_list')
    return ResponseJson({"status": 1, "msg": "添加成功"})


def delWeb(req: HttpRequest, id):
    """
    删除监控站点
    """
    if req.method != "DELETE":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    if id:
        if not Web_Site.objects.get(id=int(id)):
            return ResponseJson({"status": 0, "msg": "主机不存在"})
    Web_Site.objects.filter(id=int(id)).delete()
    cache.delete(f'WebStatusClient_web_list')
    return ResponseJson({"status": 1, "msg": "删除成功"})
