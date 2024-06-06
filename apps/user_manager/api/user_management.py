from django.apps import apps
from django.http import HttpRequest

from apps.permission_manager.util.permissionGroupUtils import group_id_exists, get_group_by_id
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id, write_user_new_password_to_database, username_exists, \
    real_name_exists, email_exists, user_id_exist
from apps.permission_manager.models import Permission_groups
from apps.audit.util.auditTools import write_access_log, write_audit
from util.pageUtils import get_max_page, get_page_content
from util.Response import ResponseJson
from util.Request import RequestLoadJson, getClientIp
from util.logger import Log
from util.passwordUtils import verifyPasswordRules, encrypt_password
from apps.permission_manager.util.permission import groupPermission


# 获取用户列表
@Log.catch
def getUserList(req: HttpRequest):
    if not req.method == 'POST':
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
    result = User.objects.filter(userName__icontains=search if search else "")
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    maxPage = get_max_page(result.count(), pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "id": item.get("id"),
                "userName": item.get("userName"),
                "realName": item.get("realName"),
                "email": item.get("email"),
                "createdAt": item.get("createdAt"),
                "lastLoginTime": item.get("lastLoginTime"),
                "lastLoginIP": item.get("lastLoginIP"),
                "permissionGroupID": item.get("permission_id"),
                "permissionGroupName": groupPermission(item.get("permission_id")).get_group_name() if item.get(
                    "permission_id") else None,
                "disable": item.get("disable")
            })
    write_access_log(
        req.session.get("userID"),
        getClientIp(req),
        f"获取用户列表(搜索条件: {search} 页码: {page} 页大小: {pageSize})"
    )
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": maxPage,
            "currentPage": page if page < maxPage else maxPage,
            "PageContent": PageContent
        }
    })


# 新增用户
@Log.catch
def addUser(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
        Log.debug(req_json)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    userName = req_json.get("userName")
    realName = req_json.get("realName")
    email = req_json.get("email")
    password = req_json.get("password")
    disable = req_json.get("disable")
    permission = req_json.get("permission")
    if not (userName and password):
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if username_exists(userName):
        return ResponseJson({"status": 0, "msg": "用户已存在"})
    if realName and real_name_exists(realName):
        return ResponseJson({"status": 0, "msg": "该用户已有账户"})
    if email and email_exists(email):
        return ResponseJson({"status": 0, "msg": "邮箱已使用过"})
    if not verifyPasswordRules(password):
        return ResponseJson(
            {"status": 0, "msg": "密码不符合安全要求（至少6字符，必须含有数字，小写字母，大写字母，特殊字符）"}
        )
    hashed_password, salt = encrypt_password(password)
    createUser = User.objects.create(
        userName=userName,
        realName=realName,
        email=email,
        password=hashed_password,
        passwordSalt=salt,
        disable=disable,
        permission=Permission_groups.objects.get(id=permission) if permission else None
    )
    if not createUser:
        return ResponseJson({"status": 0, "msg": "用户创建失败"})
    write_audit(
        req.session.get("userID"),
        "创建用户",
        "用户管理",
        f"用户名:{userName} 真实姓名: {realName} 邮箱: {email} 禁用: {disable}"
    )
    if disable: apps.get_app_config("user_manager").disable_user_list.append(createUser.id)
    return ResponseJson({"status": 1, "msg": "用户创建成功"})



# 删除用户
@Log.catch
def delUser(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    userId = req_json.get("id")
    if not userId:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if userId == req.session.get("userID"):
        return ResponseJson({"status": 0, "msg": "不能删除当前登录用户"})
    if userId == 1:
        return ResponseJson({"status": -1, "msg": "不能删除id为1的用户"})
    query = get_user_by_id(userId)
    if query.permission_id is not None and groupPermission(query.permission_id).check_group_permission("all"):
        return ResponseJson({"status": 0, "msg": "不能删除拥有All权限的用户"})
    if not query:
        return ResponseJson({"status": 0, "msg": "用户不存在"})
    write_audit(
        req.session.get("userID"),
        "Del user(删除用户)",
        "User Manager(用户管理)",
        f"User Id: {query.id} User Name: {query.userName}")
    query.delete()
    if userId in apps.get_app_config("user_manager").disable_user_list:
        apps.get_app_config("user_manager").disable_user_list.remove(userId)
    return ResponseJson({"status": 1, "msg": "用户已删除"})


# 获取用户权限
@Log.catch
def getUserPermission(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    userId = req_json.get("id")
    if not userId:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    query = get_user_by_id(userId)
    if not user_id_exist(userId):
        return ResponseJson({"status": 0, "msg": "用户不存在"}, 404)
    write_access_log(req.session.get("userID"), getClientIp(req), f"获取用户权限(uid: {userId})")
    return ResponseJson({"status": 1, "data": {
        "permissionId": query.permission_id,
        "permissionName": get_group_by_id(query.permission_id).name if query.permission_id else None,
    }})


# 获取用户信息
@Log.catch
def getUserInfo(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    userId = req_json.get("id")
    if not userId:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    query = get_user_by_id(userId)
    if not query:
        return ResponseJson({"status": 0, "msg": "用户不存在"})
    write_access_log(req.session.get("userID"), getClientIp(req), f"获取用户信息(uid: {userId})")
    return ResponseJson({"status": 1, "data": {
        "id": query.id,
        "userName": query.userName,
        "realName": query.realName,
        "email": query.email,
        "permissionId": query.permission_id,
        "permissionName": groupPermission(query.permission_id).get_group_name() if query.permission_id else None,
        "disable": query.disable
    }})


# 修改用户信息
@Log.catch
def setUserInfo(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    userId = req_json.get("id")
    data = req_json.get("data")
    if not (userId and data):
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    User = get_user_by_id(userId)
    userName: str = data.get("userName")
    realName: str = data.get("realName")
    email: str = data.get("email")
    password: str = data.get("password")
    permission: int = data.get("permission")
    disable: bool = data.get("disable")
    if userName and userName != User.userName:
        if username_exists(userName):
            return ResponseJson({"status": 0, "msg": "用户已存在"})
        write_audit(
            req.session.get("userID"),
            "编辑用户: 更新用户名",
            "用户管理",
            f"{User.userName}-->{userName}"
        )
        User.userName = userName
    if realName and realName != User.realName:
        if real_name_exists(realName):
            return ResponseJson({"status": 0, "msg": "用户已存在"})
        write_audit(
            req.session.get("userID"),
            "编辑用户: 更新真实姓名",
            "用户管理",
            f"{User.realName}-->{realName}")
        User.realName = realName
    if email and email != User.email:
        if email_exists(email):
            return ResponseJson({"status": 0, "msg": "邮箱已使用"})
        write_audit(
            req.session.get("userID"),
            "编辑用户: 更新邮箱",
            "用户管理",
            f"{User.email}-->{email}")
        User.email = email
    if password:
        if not verifyPasswordRules(password):
            return ResponseJson(
                {
                    "status": 0,
                    "msg": "密码不符合安全要求（至少6字符，必须含有数字，小写字母，大写字母，特殊字符）"
                }
            )
        write_user_new_password_to_database(User, password)
        write_audit(
            req.session.get("userID"),
            "编辑用户: 更新密码",
            "用户管理",
            ""
        )
    if permission and permission != User.permission_id:
        if not group_id_exists(permission):
            return ResponseJson({"status": 0, "msg": "所选择的权限组不存在"})
        newPermission = get_group_by_id(permission)
        write_audit(
            req.session.get("userID"),
            "编辑用户: 更新权限组",
            "用户管理",
            f"{get_group_by_id(User.permission_id).name if User.permission_id else 'None'}-->{newPermission.name}"
        )
        User.permission_id = newPermission
    if disable is not None and disable != User.disable:
        if User.id == 1:
            return ResponseJson({'status': 0, 'msg': "无法禁用id为1的账户"})
        write_audit(
            req.session.get("userID"),
            "编辑用户: 禁用用户" if disable else "编辑用户: 启用用户",
            "用户管理",
            f"{User.disable}-->{disable}"
        )
        User.disable = disable
        apps.get_app_config("user_manager").disable_user_list.append(userId) if disable else apps.get_app_config("user_manager").disable_user_list.remove(userId)
    User.save()
    return ResponseJson({"status": 1, "msg": "成功", "data": {
        "id": User.id,
        "userName": User.userName,
        "realName": User.realName,
        "email": User.email,
        "permissionId": User.permission_id.id if isinstance(User.permission_id,
                                                            Permission_groups) else User.permission_id,
        "permissionName": Permission_groups.objects.filter(
            id=User.permission_id.id if isinstance(User.permission_id,
                                                   Permission_groups) else User.permission_id).first().name if User.permission_id else None,
        "disable": User.disable
    }})
