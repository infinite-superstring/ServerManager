import datetime

from django.apps import apps

from util.Response import ResponseJson
from util.Request import RequestLoadJson, getClientIp
from util.passwordUtils import PasswordToMd5
from util.logger import Log
from audit.util.auditTools import write_audit
from setting.entity.Config import config
from user_manager.util.userUtils import get_user_by_username, verify_username_and_password

config: config = apps.get_app_config('setting').get_config()


def AuthLogin(req):
    """用户登录"""
    if req.session.get("user"):
        return ResponseJson({"status": 1, "msg": "当前账户已登录"})
    if req.method == 'POST':
        req_json = RequestLoadJson(req)
        user = req_json.get("username")
        password = PasswordToMd5(req_json.get("password"))
        if verify_username_and_password(user, password):
            user = get_user_by_username(user)
            if not user.disable:
                req.session["user"] = user.userName
                req.session["userID"] = user.id
                req.session.set_expiry(int(config.base.sessionExpiry) * 60)
                Log.success(f"用户[{user.userName}]已登陆")
                user.lastLoginIP = getClientIp(req)
                user.lastLoginTime = datetime.datetime.now()
                user.save()
                write_audit(user.id, "Login", "Auth", user.lastLoginIP)
                return ResponseJson({"status": 1, "msg": "登录成功"})
            else:
                return ResponseJson({"status": 0, "msg": "账户被禁用，请联系管理员"})
        else:
            return ResponseJson({"status": 0, "msg": "用户名或密码错误"})
    else:
        return ResponseJson({"status": -1, "msg": "请求方法不正确"})


def AuthOutLog(req):
    """用户登出"""
    if req.session.get("user"):
        write_audit(req.session.get("userID"), "Outlog", "Auth", getClientIp(req))
        req.session.clear()
        return ResponseJson({"status": 1, "msg": "登出成功"})
    else:
        return ResponseJson({"status": 0, "msg": "您未登录"})


def node_auth(req):
    """节点认证"""
