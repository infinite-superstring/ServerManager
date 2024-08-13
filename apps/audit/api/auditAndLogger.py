from typing import Union

from django.db.models import QuerySet, Q
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from apps.audit.models import Audit, Access_Log, FileChange_Log, System_Log, User_Session_Log, Node_Session_Log
from apps.node_manager.models import Node
from apps.permission_manager.util.api_permission import api_permission
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.pageUtils import *


def _filterResult(
        result: QuerySet[Union[Audit, Access_Log, FileChange_Log, System_Log, User_Session_Log, Node_Session_Log]],
        date_range: dict = None, search: str = None, level: int | list = None, action: int = None):
    """
    过滤不同类型日志的结果
    """
    # 根据日期范围过滤
    if date_range:
        start_date = parse_datetime(date_range.get('start')) if date_range.get('start') else None
        end_date = parse_datetime(date_range.get('end')) if date_range.get('end') else None
        result = result.filter(time__range=(start_date, end_date))

    # 根据搜索关键词过滤
    if search:
        if isinstance(result.first(), Audit):
            result = result.filter(
                Q(content__icontains=search) |
                Q(module__icontains=search) |
                Q(action__icontains=search))
        elif isinstance(result.first(), Access_Log):
            result = result.filter(
                Q(ip__icontains=search) |
                Q(user__userName__icontains=search) |
                Q(content__icontains=search) |
                Q(module__icontains=search))
        elif isinstance(result.first(), FileChange_Log):
            result = result.filter(
                Q(user__userName__icontains=search) |
                Q(filepath__icontains=search) |
                Q(action__icontains=search))
        elif isinstance(result.first(), System_Log):
            result = result.filter(
                Q(module__icontains=search) |
                Q(content__icontains=search) |
                Q(level__in=level))
        elif isinstance(result.first(), User_Session_Log):
            result = result.filter(
                Q(ip__icontains=search) |
                Q(user__userName__icontains=search))
        elif isinstance(result.first(), Node_Session_Log):
            result = result.filter(
                Q(ip__icontains=search) |
                Q(node__name__icontains=search))

            # 根据日志等级过滤（适用于 System_Log）
    if level is not None and isinstance(result.first(), System_Log):
        result = result.filter(level=level)

    # 根据动作过滤（适用于 Audit、FileChange_Log、User_Session_Log 和 Node_Session_Log）
    if action is not None:
        if isinstance(result.first(), Audit):
            result = result.filter(action__icontains=action)
        elif isinstance(result.first(), FileChange_Log):
            result = result.filter(action__icontains=action)
        elif isinstance(result.first(), User_Session_Log):
            result = result.filter(action=action)
        elif isinstance(result.first(), Node_Session_Log):
            result = result.filter(action=action)

    return result


@require_POST
@api_permission("viewAudit")
def getAudit(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    date_range: dict = req_json.get("date_range")
    search = req_json.get("search")
    result = Audit.objects.filter().order_by("-time")
    result = _filterResult(result, date_range=date_range, search=search)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                "time": item.get("time"),
                "action": item.get("action"),
                "module": item.get("module"),
                "content": item.get("content"),
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(Audit.objects.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
@api_permission("viewAudit")
def getAccessLog(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    date_range: dict = req_json.get("date")
    search = req_json.get("search")
    # 按时间排序查询
    result = Access_Log.objects.filter().order_by("-time")
    result = _filterResult(result, date_range=date_range, search=search)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                "time": item.get("time"),
                "ip": item.get("ip"),
                "module": item.get("module"),
                "content": item.get("content"),
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(Access_Log.objects.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
@api_permission("viewAudit")
def getFileChangeLog(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    date_range: dict = req_json.get("date")
    search = req_json.get("search")
    result = FileChange_Log.objects.filter().order_by("-time")
    result = _filterResult(result, date_range=date_range, search=search)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                "time": item.get("time"),
                "action": item.get("action"),
                "filepath": item.get("filepath"),
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(FileChange_Log.objects.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
@api_permission("viewAudit")
def getSystemLog(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    date_range: dict = req_json.get("date")
    search = req_json.get("search")
    level: list = req_json.get("level")
    result = System_Log.objects.filter().order_by("-time")
    result = _filterResult(result, date_range=date_range, search=search, level=level)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "time": item.get("time"),
                "level": item.get("level"),
                "module": item.get("module"),
                "content": item.get("content"),
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(System_Log.objects.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
@api_permission("viewAudit")
def get_user_session_log(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    page = req_json.get("page", 1)
    page_size = req_json.get("pageSize", 20)
    action: int = req_json.get("action")
    search = req_json.get("search")
    date_range: dict = req_json.get("date")
    log_list = User_Session_Log.objects.filter().order_by("-time")
    log_list = _filterResult(log_list, action=action, search=search, date_range=date_range)
    page_content = get_page_content(log_list, page if page > 0 else 1, page_size)
    page_max = get_max_page(log_list.count(), page_size)
    result = []
    for item in page_content:
        result.append({
            "id": item.get("id"),
            "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
            "ip": item.get("ip"),
            "action": item.get("action"),
            "time": item.get("time"),
        })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": page_max,
            "currentPage": page,
            "PageContent": result
        }
    })


@require_POST
@api_permission("viewAudit")
def get_node_session_log(req):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    page = req_json.get("page", 1)
    page_size = req_json.get("pageSize", 20)
    action: int = req_json.get("action")
    search = req_json.get("search")
    date_range: dict = req_json.get("date")
    log_list = Node_Session_Log.objects.filter().order_by("-time")
    log_list = _filterResult(log_list, action=action, search=search, date_range=date_range)
    page_content = get_page_content(log_list, page if page > 0 else 1, page_size)
    page_max = get_max_page(log_list.count(), page_size)
    result = []
    for item in page_content:
        node_name = Node.objects.get(uuid=item.get("node_id")).name
        result.append({
            "id": item.get("id"),
            "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
            "name": node_name,
            "ip": item.get("ip"),
            "action": item.get("action"),
            "time": item.get("time"),
        })
    result.sort(key=lambda x: x["time"])
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": page_max,
            "currentPage": page,
            "PageContent": result
        }
    })
