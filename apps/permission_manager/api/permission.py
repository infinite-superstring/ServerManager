from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id
from apps.audit.util.auditTools import write_access_log, write_audit
from apps.auth.utils.otpUtils import verify_otp_for_request
from util.pageUtils import get_max_page, get_page_content
from util.Request import RequestLoadJson, getClientIp
from util.Response import ResponseJson
from util.logger import Log
from apps.permission_manager.util.permission import *


# 获取权限组列表
def getPermissionGroupsList(req):
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
    search = req_json.get("search", "")
    result = Permission_groups.objects.filter(name__icontains=search if search else "")
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "creator": get_user_by_id(item.get("creator_id")).userName if item.get("creator_id") else None,
                "createdAt": item.get("createdAt"),
                "disable": item.get("disable")
            })
    write_access_log(req.session.get("userID"), getClientIp(req), f"Get permission group list(Search: {search} Page: {page} Page Size: {pageSize})")
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


# 新建权限组
def addPermissionGroup(req):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    name = req_json.get("name")
    if Permission_groups.objects.filter(name=name):
        return ResponseJson({"status": 0, "msg": "组已存在"})
    creator = get_user_by_id(req.session.get("userID"))
    disable = req_json.get("disable")
    permission = req_json.get("permissions")
    if not name or not creator or not permission or not disable:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    group = Permission_groups.objects.create(
        name=name,
        creator=creator,
        disable=disable
    )
    groupPermission(group.id).update_permissions_list(permission)
    write_audit(req.session.get("userID"), "Add permission group(添加权限组)", "Permission Manager(权限管理)", f"Name:{name} Permission: {permission} Disable: {disable}")
    return ResponseJson({"status": 1, "msg": "添加成功"})


# 删除权限组
def delPermissionGroup(req):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    PermissionGroupId = req_json.get("id")
    code = req_json.get("code")
    if not PermissionGroupId or not code:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if not verify_otp_for_request(req, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    query = Permission_groups.objects.filter(id=PermissionGroupId).first()
    if not query:
        return ResponseJson({"status": 0, "msg": "组不存在"})
    if User.objects.filter(permission=query):
        return ResponseJson({"status": 2, "msg": "当前组正在使用中，无法删除"})
    write_audit(req.session.get("userID"), "Del permission group(删除权限组)", "Permission Manager(权限管理)", query.name)
    query.delete()
    return ResponseJson({"status": 1, "msg": "组已删除"})



# 获取权限组信息
@Log.catch
def getPermissionGroupInfo(req):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    PermissionGroupId = req_json.get("id")
    if not PermissionGroupId:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    query = Permission_groups.objects.filter(id=PermissionGroupId).first()
    if not query:
        return ResponseJson({"status": 0, "msg": "组不存在"})
    write_access_log(req.session.get("userID"), getClientIp(req), f"Get permission group info: {query.name}")
    return ResponseJson({"status": 1, "data": {
        "id": query.id,
        "name": query.name,
        "creator": query.creator.userName if query.creator else None,
        "createdAt": query.createdAt,
        "disable": query.disable,
        "Permission": groupPermission(query.id).get_permissions_dict()
    }})



# 修改权限组
def setPermissionGroup(req):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    GroupId = req_json.get("id")
    data = req_json.get("data")
    if not GroupId or not data:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    Group = Permission_groups.objects.filter(id=GroupId).first()
    newName: str = data.get("newName")
    disable: bool = data.get("disable")
    permissions: list = data.get("permissions")
    clientIp: str = getClientIp(req)
    userID: int = req.session.get("userID")
    if newName and newName != Group.name:
        write_audit(
            userID,
            "Rename permission group(重命名权限组)",
            "Permission Manager(权限管理)",
            f"{Group.name}-->{newName}"
        )
        Group.name = newName
    if disable != Group.disable:
        write_audit(
            userID,
            "Update status permission group(更新权限组状态)",
            "Permission Manager(权限管理)",
            f"{Group.name}: {Group.disable}-->{disable}")
        Group.disable = disable
    if permissions:
        groupPermission(Group.id).update_permissions_list(permissions)
    Group.save()
    return ResponseJson({"status": 1, "msg": "成功", "data": {
        "id": Group.id,
        "name": Group.name,
        "Permission": groupPermission(Group.id).get_permissions_dict()
    }})



def getPermissionList(req):
    write_access_log(req.session.get("userID"), getClientIp(req), f"Get permission item list")
    data: dict = {}
    for permission in get_all_permission_item_info():
        data.update({permission['permission']: permission['translate']})

    return ResponseJson({
        "status": 1,
        "msg": "成功",
        "data": data
    })
