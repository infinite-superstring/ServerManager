from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect
from util.Response import ResponseJson
from util.pathUtil import URL_PathUtil
import re


class AuthMiddleware(MiddlewareMixin):
    """
    登录验证中间件
    """
    def process_request(self, request):
        if request.path_info in ["/login", "/api/auth/login", "/api/auth/nodeAuth"]:
            return

        # 清理非法会话
        if (request.session.get("user") or request.session.get("userID")) and (request.session.get("node_name") or request.session.get("node_uuid")):
            request.session.clear()
            return redirect("/error/403")

        url_pu = URL_PathUtil(request.path_info)

        if request.session.get("node_name") and request.session.get("node_uuid"):
            if url_pu.is_node_path():
                return
            else:
                return ResponseJson({'status': -1, "msg": "非法访问"})

        if request.session.get("user") and request.session.get("userID"):
            if not url_pu.is_node_path():
                return
            else:
                match(url_pu.is_api_path()):
                    case True:
                        return ResponseJson({'status': -1, 'msg': '非法访问'})
                    case False:
                        return redirect("/error/403")
        else:
            return redirect("/login")
