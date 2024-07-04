import json
from django.shortcuts import HttpResponse
from django.apps import apps

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
            app_setting.update_config(saveConfig(dictToConfig(req_json)))
            return HttpResponse(json.dumps(apps.get_app_config("setting").get_config(), default=lambda o: o.__dict__, indent=2))

    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)

def getPageConfig(req):
    config = apps.get_app_config("setting").get_config()
    return ResponseJson({
        "status": 1,
        "data": {
            "forceOTP_Bind": config.security.forceOTP_Bind,
        }
    })