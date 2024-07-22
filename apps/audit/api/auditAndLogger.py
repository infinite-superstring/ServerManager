from apps.audit.models import Audit, Access_Log, FileChange_Log, System_Log, User_Session_Log, Node_Session_Log
from apps.node_manager.models import Node
from apps.permission_manager.util.api_permission import api_permission
from apps.user_manager.util.userUtils import get_user_by_id
from util.pageUtils import *
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


@api_permission("viewAudit")
def getAudit(req):
    if not req.method == "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    result = Audit.objects.filter().order_by("-time")
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


@api_permission("viewAudit")
def getAccessLog(req):
    if not req.method == "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    # 按时间排序查询
    result = Access_Log.objects.filter().order_by("-time")
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


@api_permission("viewAudit")
def getFileChangeLog(req):
    if not req.method == "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    result = FileChange_Log.objects.filter().order_by("-time")
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


@api_permission("viewAudit")
def getSystemLog(req):
    if not req.method == "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    PageContent = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    result = System_Log.objects.filter().order_by("-time")
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


@api_permission("viewAudit")
def get_user_session_log(req):
    if req.method != "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    page = req_json.get("page", 1)
    page_size = req_json.get("pageSize", 20)
    log_list = User_Session_Log.objects.filter().order_by("-time")
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


@api_permission("viewAudit")
def get_node_session_log(req):
    if req.method != "POST":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    page = req_json.get("page", 1)
    page_size = req_json.get("pageSize", 20)
    log_list = Node_Session_Log.objects.filter().order_by("-time")
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
