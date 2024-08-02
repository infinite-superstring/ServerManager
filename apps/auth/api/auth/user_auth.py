import datetime

from django.apps import apps
from django.core.cache import cache
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from util.Response import ResponseJson
from util.Request import RequestLoadJson, getClientIp
from util.logger import Log
from apps.auth.utils.otpUtils import hasOTPBound
from apps.audit.util.auditTools import write_audit, write_user_session_log
from apps.setting.entity.Config import config
from apps.user_manager.util.userUtils import get_user_by_username, verify_username_and_password
from apps.permission_manager.util.permission import groupPermission

config: config = apps.get_app_config('setting').get_config()


@require_POST
def AuthLogin(req: HttpRequest):
    """用户登录"""
    if req.session.get("user"):
        return ResponseJson({"status": 1, "msg": "当前账户已登录"})
    req_json = RequestLoadJson(req)
    user = req_json.get("username")
    password = req_json.get("password")
    ip = getClientIp(req)
    limit = cache.get(f"user_temp_limit_{ip}")
    login_error_count = config.security.login_error_count
    if limit is not None and login_error_count is not None and limit >= login_error_count:  # 次数
        return ResponseJson({"status": 0, "msg": "您已被临时限制登录，请稍后再试"})
    if not verify_username_and_password(user, password):
        expiry = config.security.login_expiry if config.security.login_expiry else 1
        cache.set(f"user_temp_limit_{ip}", limit + 1 if limit else 1, expiry * 60) # 时间
        return ResponseJson({"status": 0, "msg": "用户名或密码错误"})
    user = get_user_by_username(user)
    if user.disable:
        return ResponseJson({"status": 0, "msg": "账户被禁用，请联系管理员"})
    req.session["user"] = user.userName
    req.session["userID"] = user.id
    req.session["auth_method"] = "User Auth"
    req.session.set_expiry(int(config.base.session_expiry) * 60)
    Log.success(f"用户[{user.userName}]已登陆")
    user.lastLoginIP = getClientIp(req)
    user.lastLoginTime = datetime.datetime.now()
    user.save()
    write_audit(user.id, "用户登录", "用户认证", user.lastLoginIP)
    write_user_session_log(user_id=user.id, action=0, ip=user.lastLoginIP)
    return ResponseJson({"status": 1, "msg": "登录成功", "data": {
        'id': user.id,
        "userName": user.userName,
        "realName": user.realName,
        "email": user.email,
        "enableOTP": hasOTPBound(user),
        "group": user.permission.name,
        "permissions": groupPermission(user.permission.id).get_permissions_list(),
        "isNewUser": user.isNewUser
    }})


def AuthOutLog(req: HttpRequest):
    """用户登出"""
    if req.session.get("user"):
        user_id = req.session.get("userID")
        ip = getClientIp(req)
        write_audit(user_id, "退出登录", "用户认证", ip)
        write_user_session_log(user_id=user_id, action=1, ip=ip)
        req.session.clear()
        return ResponseJson({"status": 1, "msg": "登出成功"})
    else:
        return ResponseJson({"status": 0, "msg": "您未登录"})


def getLoginStatus(req: HttpRequest):
    """获取用户登录状态"""
    if req.session["user"] and req.session["userID"]:
        return ResponseJson({"status": 1, "msg": "已登录"})
    return ResponseJson({"status": 0, "msg": "未登录"})
