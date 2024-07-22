from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest
from django.views.decorators.http import require_GET, require_POST, require_http_methods

import util.result as R
from apps.audit.util.auditTools import write_audit
from apps.permission_manager.util.api_permission import api_permission
from apps.web_status.models import Web_Site, Web_Site_Abnormal_Log
from apps.web_status.utils.webUtil import is_valid_host, hostIsExist, get_or_create_web_site_log, \
    get_latest_or_default_abnormal_log
from util import result, pageUtils
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


@require_GET
@api_permission("viewWebStatus")
def getList(req: HttpRequest):
    """
    获取监控网站列表
    """
    page = int(req.GET.get("page", 1))
    pageSize = int(req.GET.get("pageSize", 10))
    name = req.GET.get("name", "")
    web_list = Web_Site.objects.filter(title__contains=name, ).order_by('id')
    count = web_list.count()
    web_list: QuerySet = pageUtils.get_page_content(web_list, int(page), int(pageSize))
    result = []
    max_page = pageUtils.get_max_page(count, int(pageSize))
    for web in web_list:
        runtime = get_or_create_web_site_log(web.get("id"))
        error_time = get_latest_or_default_abnormal_log(web.get("id"))
        result.append({
            "id": web.get("id"),
            "title": web.get("title"),
            "host": web.get("host"),
            "status": runtime.status,
            "delay": int(runtime.delay),
            "online": str(runtime.status).startswith("2"),
            "description": web.get("description"),
            'last_error_info': error_time.end_time if error_time.end_time else error_time.start_time,
        })

    return R.success(data={
        'list': result,
        'maxPage': max_page
    })


@require_POST
@api_permission("editWebStatus")
def addWeb(req: HttpRequest):
    """
    添加监控站点
    """
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    title = data['title']
    host = data['host']
    description = data.get('description', '')

    if not title or not host:
        return ResponseJson({"status": 0, "msg": "标题和主机不能为空"})

    if not is_valid_host(host):
        return ResponseJson({"status": 0, "msg": "主机地址不合法"})
    if hostIsExist(host):
        return ResponseJson({"status": 0, "msg": "主机地址已存在"})
    web = Web_Site.objects.create(title=title, host=host, description=description)
    cache.delete(f'web_status_web_list')
    write_audit(req.session['userID'], "新增网站监控", "网站监控", f"ID：{web.id} 标题：{title} 主机：{host}")
    return ResponseJson({"status": 1, "msg": "添加成功"})


@require_http_methods("DELETE")
@api_permission("editWebStatus")
def delWeb(req: HttpRequest, id):
    """
    删除监控站点
    """
    if id:
        if not Web_Site.objects.get(id=int(id)):
            return ResponseJson({"status": 0, "msg": "主机不存在"})
    Web_Site.objects.filter(id=int(id)).delete()
    cache.delete(f'web_status_web_list')
    write_audit(req.session['userID'], "删除网站监控", "网站监控", f"ID: {id}")
    return ResponseJson({"status": 1, "msg": "删除成功"})


@require_http_methods("PUT")
@api_permission("editWebStatus")
def update(req: HttpRequest):
    """
    更新监控站点
    """
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return result.api_error("JSON解析失败")
    id = data.get('id', None)
    if not id:
        return result.error('id不能为空')
    site = Web_Site.objects.get(id=int(id))
    if not site:
        return result.error('主机不存在')
    site.title = data.get('title', site.title)
    site.description = data.get('description', site.description)
    site.save()
    write_audit(req.session['userID'], "编辑网站监控", "网站监控", f"ID: {id}")
    return result.success(msg='更新成功')


@require_GET
@api_permission("viewWebStatus")
def getSiteNames(req: HttpRequest):
    """
    获取监控站点名称
    """
    names = Web_Site.objects.filter().values_list('title', 'host')
    return result.success(names)


@require_GET
@api_permission("viewWebStatus")
def getLog(req: HttpRequest):
    """
    获取 监控日志
    """
    host = req.GET.get('host', '')
    page = req.GET.get('page', 1)
    pageSize = req.GET.get('pageSize', 20)
    logs = Web_Site_Abnormal_Log.objects.filter(web__host=host).order_by('-start_time')
    page_list: list[dict] = pageUtils.get_page_content(logs, int(page), int(pageSize))
    max_page = pageUtils.get_max_page(logs.count(), int(pageSize))
    result_list = []
    for log in page_list:
        result_list.append({
            'status_code': log.get('status'),
            'error_type': log.get('error_type'),
            'error_info': log.get('error_info'),
            'start_time': log.get('start_time'),
            'end_time': log.get('end_time').strftime("%Y-%m-%d %H:%M:%S") if log.get('end_time') else None,
        })
    return result.success(data={
        'list': result_list,
        'maxPage': max_page
    })
