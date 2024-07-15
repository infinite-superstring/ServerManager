from apps.user_manager.util.userUtils import get_user_by_id
from apps.audit.util.auditTools import write_access_log, write_audit, write_system_log
from apps.auth.utils.otpUtils import verify_otp_for_request
from apps.permission_manager.util.permissionGroupUtils import get_group_by_id, group_id_exists
from apps.permission_manager.util.permission import *
from util.pageUtils import get_max_page, get_page_content
from util.Request import RequestLoadJson, getClientIp
from util.Response import ResponseJson
from util.logger import Log


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
    write_access_log(
        req.session.get("userID"),
        req,
        "用户权限管理",
        f"获取权限列表(搜索条件: {search if search else '无'} 页码: {page} 页大小: {pageSize})"
    )
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
    if permission.get('all') and not groupPermission(creator).is_superuser():
        write_system_log(2, "用户权限管理", f"用户{creator.userName}(uid:{creator.id})尝试创建带all的权限组被拒绝")
        return ResponseJson({'status': 0, 'msg': '非法操作：非超管账户无法新增包含all的权限组'})
    group = Permission_groups.objects.create(
        name=name,
        creator=creator,
        disable=disable
    )
    groupPermission(group.id).update_permissions_list(permission)
    write_audit(
        creator,
        "创建权限组",
        "用户权限管理",
        f"权限组名:{name} 权限列表: {permission} 是否禁用: {disable}"
    )
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
    if not PermissionGroupId or code is None:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if not verify_otp_for_request(req, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    query = Permission_groups.objects.filter(id=PermissionGroupId).first()
    if not query:
        return ResponseJson({"status": 0, "msg": "组不存在"})
    if query.id == 1:
        return ResponseJson({"status": 0, "msg": "不允许删除GID为1的组"})
    user = get_user_by_id(req.session.get("userID"))
    if not groupPermission(user).is_superuser() and groupPermission(query).is_superuser():
        write_system_log(2, "用户权限管理", f"用户{user.userName}(uid:{user.id})尝试删除带all的权限组被拒绝")
        return ResponseJson({'status': 0, 'msg': '非法操作：非超管账户无法删除包含all的权限组'})
    if User.objects.filter(permission=query):
        return ResponseJson({"status": 2, "msg": "当前组正在使用中，无法删除"})
    write_audit(
        user,
        "删除权限组",
        "用户权限管理", query.name
    )
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
    write_access_log(
        req.session.get("userID"),
        getClientIp(req),
        "用户权限管理",
        f"获取权限组信息: {query.name}(gid: {query.id})"
    )
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
    if GroupId == 1:
        return ResponseJson({'status': 0, 'msg': 'GID为1的权限组无法被修改'})
    if not group_id_exists(GroupId):
        return ResponseJson({'status': 0, 'msg': '要修改的权限组不存在'})
    Group = get_group_by_id(GroupId)
    newName: str = data.get("newName")
    disable: bool = data.get("disable")
    permissions: list = data.get("permissions")
    userID: int = req.session.get("userID")
    user = get_user_by_id(userID)
    if newName and newName != Group.name:
        write_audit(
            user,
            "重命名权限组",
            "用户权限管理",
            f"{Group.name}-->{newName}"
        )
        Group.name = newName
    if disable is not None and disable != Group.disable:
        if Group.id == 1:
            return ResponseJson({
                "status": 0,
                "msg": "无法禁用GID为1的组"
            })
        write_audit(
            user,
            "禁用权限组",
            "用户权限管理",
            f"{Group.name}: {Group.disable}-->{disable}")
        Group.disable = disable
    gp = groupPermission(Group)
    if set(gp.get_permissions_list()) != set(permissions):
        if 'all' in permissions and not groupPermission(user).is_superuser():
            write_system_log(2, "用户权限管理", f"用户{user.userName}(uid:{user.id})尝试给权限组添加all权限被拒绝")
            return ResponseJson({'status': 0, 'msg': '非法操作：非超管账户无法添加all权限到组中'})
        if groupPermission(Group).is_superuser() and not groupPermission(user).is_superuser():
            write_system_log(2, "用户权限管理",
                             f"用户{user.userName}(uid:{user.id})尝试修改带有all权限组的权限分配被拒绝")
            return ResponseJson({'status': 0, 'msg': '非法操作：非超管账户无法修改包含all的权限组的权限分配'})
        groupPermission(Group).update_permissions_list(permissions)
    Group.save()
    return ResponseJson({"status": 1, "msg": "成功", "data": {
        "id": Group.id,
        "name": Group.name,
        "Permission": groupPermission(Group.id).get_permissions_dict()
    }})



def getPermissionList(req):
    write_access_log(
        req.session.get("userID"),
        getClientIp(req),
        "用户权限管理"
        f"获取权限项列表"
    )
    data: dict = {}
    for permission in get_all_permission_item_info():
        data.update({permission['permission']: permission['translate']})

    return ResponseJson({
        "status": 1,
        "msg": "成功",
        "data": data
    })
