import time

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

from apps.auth.utils.authCodeUtils import user_otp_is_binding, send_auth_code
from apps.user_manager.util.userUtils import get_user_by_id
from util.Response import ResponseJson


def send_bind_otp_auth_code(request: HttpRequest) -> HttpResponse:
    """发送绑定用验证码"""
    uid = request.session['userID']
    user = get_user_by_id(uid)
    # if user_otp_is_binding(user):
    #     return ResponseJson({
    #         'status': 0,
    #         'msg': '已绑定过OTP'
    #     })
    # if cache.get(f"getAuthCode_{user.id}") and cache.get(f"getAuthCode_{user.id}")['end_time'] > time.time():
    #     return ResponseJson({
    #         'status': 0,
    #         'msg': f'冷却中! 请等待{cache.get(f"getAuthCode_{user.id}")["end_time"] - time.time()}秒'
    #     })
    try:
        send_auth_code(user)
    except Exception as e:
        return ResponseJson({
            'status': -1,
            'msg': '发件失败'
        })
    return ResponseJson({
        'status': 1,
        'msg': '发件成功，请检查收件箱'
    })


def bind_otp_token(req: HttpRequest) -> HttpResponse:
    pass
