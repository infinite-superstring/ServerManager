import time

from django.apps import apps
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from apps.auth.models import OTP
from apps.auth.utils.authCodeUtils import user_otp_is_binding, send_unbind_otp_email, check_unbind_otp_email_code
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.result import api_error
from util.logger import Log

config = apps.get_app_config('setting').get_config


def send_email_code(request: HttpRequest) -> HttpResponse:
    """
    解绑:发送邮箱验证码
    """
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if not user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您未绑定OTP令牌!'
        })
    if cache.get(f"UnbindOtpEmailCode_{user.id}") and cache.get(f"UnbindOtpEmailCode_{user.id}").get('end_time') > time.time():
        return ResponseJson({
            'status': 0,
            'msg': f'冷却中! 请等待{int(cache.get(f"UnbindOtpEmailCode_{user.id}").get("end_time") - time.time())}秒'
        })
    if send_unbind_otp_email(user):
        return ResponseJson({
            'status': 1,
            'msg': '发件成功，请检查收件箱',
            'data': {
                'code_len': config().security.auth_code_length
            }
        })
    return ResponseJson({
        'status': -1,
        'msg': '发件失败',
    })


@require_POST
def unbind_otp(request: HttpRequest) -> HttpResponse:
    """
    解绑OTP令牌
    """
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if not user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您未绑定OTP令牌!'
        })
    try:
        req_json = RequestLoadJson(request)
    except Exception as e:
        Log.error(e)
        return api_error("Json解析失败", 400)
    code: str = req_json.get('code')
    if not code or not check_unbind_otp_email_code(user, code):
        return ResponseJson({'status': 0, 'msg': '验证码不正确'})
    OTP.objects.filter(user=user).delete()
    return ResponseJson({'status': 1, 'msg': '已解绑OTP令牌', 'data': {
        'status': 1
    }})