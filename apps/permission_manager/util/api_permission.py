from django.http import HttpRequest

from apps.permission_manager.util.permission import groupPermission
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id
from util.Response import ResponseJson
from util.logger import Log


class api_permission(object):
    __permission: str

    def __init__(self, permission: str | list = ''):
        self.__permission = permission

    def __call__(self, func):  # 接受函数
        def wrapper(*args, **kwargs):
            Log.debug(f"{args} {kwargs}")
            if not isinstance(args[0], HttpRequest):
                raise RuntimeError("request does not exist")
            req: HttpRequest = args[0]
            user: User = get_user_by_id(req.session.get("userID"))
            gp: groupPermission = groupPermission(user.permission)
            if gp.check_group_permission(self.__permission):
                return func(*args, **kwargs)  # 仅在DEBUG等级时运行原始函数
            else:
                Log.debug(f"User {user.userName}(uid: {user.id}) permission denied")
                return ResponseJson({
                    "status": 0,
                    "msg": "Permission denied",
                }, 403)
        return wrapper