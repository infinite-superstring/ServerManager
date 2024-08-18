from django.apps import apps
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from util.Response import ResponseJson
from util.pathUtil import URL_PathUtil


class AuthMiddleware(MiddlewareMixin):
    """
    登录验证中间件
    """
    def process_request(self, request):
        if request.path_info in ["/login", "/api/auth/login", "/api/auth/nodeAuth", "/api/settings/getServerConfig"]:
            return

        # 清理非法会话
        if (request.session.get("user") or request.session.get("userID")) and (request.session.get("node_name") or request.session.get("node_uuid")):
            request.session.clear()
            return ResponseJson({'status': -1, "msg": "非法的会话"}, 403)

        if request.session.get("node_name") and request.session.get("node_uuid"):
            url_pu = URL_PathUtil(request.path_info)
            if not url_pu.is_node_path():
                request.session.clear()
                return ResponseJson({'status': -1, "msg": "非法访问"}, 403)
            return

        if not request.session.get("user") or not request.session.get("userID"):
            return ResponseJson({'status': -1, 'msg': '账户未登录'}, 403)

        if request.session.get("userID") in apps.get_app_config("user_manager").disable_user_list:
            request.session.clear()
            return ResponseJson({'status': -1, 'msg': '账户已被禁用，请联系管理员'}, 403)