from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class AuthMiddleware(MiddlewareMixin):
    """
    登录验证中间件
    """
    def process_request(self, request):
        if request.path_info in ["/login", "/auth/login"]:
            return
        if request.session.get("user") and request.session.get("userID"):
            return
        else:
            return redirect("/login")
