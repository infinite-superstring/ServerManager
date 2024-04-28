from user_manager.util.userUtils import *
from audit.models import Audit, Access_Log, FileChange_Log, System_Log
from util.pageUtils import *
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log

def getAudit(req):
    if req.method == "POST":
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"})
        else:
            PageContent = []
            page = req_json.get("page", 1)
            pageSize = req_json.get("pageSize", 20)
            result = Audit.objects.filter()
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
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})

def getAccessLog(req):
    if req.method == "POST":
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"})
        else:
            PageContent = []
            page = req_json.get("page", 1)
            pageSize = req_json.get("pageSize", 20)
            result = Access_Log.objects.filter()
            pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
            if pageQuery:
                for item in pageQuery:
                    PageContent.append({
                        "id": item.get("id"),
                        "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                        "time": item.get("time"),
                        "ip": item.get("ip"),
                        "module": item.get("module"),
                    })
            return ResponseJson({
                "status": 1,
                "data": {
                    "maxPage": get_max_page(Access_Log.objects.all().count(), 20),
                    "currentPage": page,
                    "PageContent": PageContent
                }
            })
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})

def getFileChangeLog(req):
    if req.method == "POST":
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"})
        else:
            PageContent = []
            page = req_json.get("page", 1)
            pageSize = req_json.get("pageSize", 20)
            result = FileChange_Log.objects.filter()
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
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})

def getSystemLog(req):
    if req.method == "POST":
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"})
        else:
            PageContent = []
            page = req_json.get("page", 1)
            pageSize = req_json.get("pageSize", 20)
            result = System_Log.objects.filter()
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
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})
