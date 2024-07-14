import json
from django.shortcuts import HttpResponse
from django.apps import apps

from apps.audit.util.auditTools import write_system_log
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from apps.setting.util.Config import saveConfig,dictToConfig

app_setting = apps.get_app_config("setting")

def getSetting(req):
    return HttpResponse(json.dumps(app_setting.get_config(), default=lambda o: o.__dict__, indent=2))

def editSetting(req):
    if req.method == 'POST':
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
        else:
            uid = req.session['userID']
            user = get_user_by_id(uid)
            app_setting.update_config(saveConfig(dictToConfig(req_json)))
            write_system_log(1, "系统设置", f"用户{user.userName}(uid: {user.id})更新了设置")
            return getSetting(req)
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)

def getPageConfig(req):
    config = apps.get_app_config("setting").get_config()
    return ResponseJson({
        "status": 1,
        "data": {
            "webSite_name": config.base.website_name,
            "forceOTP_Bind": config.security.force_otp_bind,
        }
    })