import time
import pyotp
from django.apps import apps

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from apps.auth.utils.authCodeUtils import user_otp_is_binding, check_bind_otp_email_code, send_bind_otp_email
from apps.user_manager.util.userUtils import get_user_by_id
from apps.auth.models import OTP
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.result import api_error

config = apps.get_app_config('setting').get_config


def send_email_code(request: HttpRequest) -> HttpResponse:
    """绑定:发送邮箱验证码"""
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您已绑定过OTP令牌!'
        })
    if (
        cache.get(f"BindOtpEmailCode_{user.id}") and
        cache.get(f"BindOtpEmailCode_{user.id}").get('end_time') > time.time()):
        return ResponseJson({
            'status': 0,
            'msg': f'冷却中! 请等待{int(cache.get(f"BindOtpEmailCode_{user.id}")["end_time"] - time.time())}秒'
        })
    if send_bind_otp_email(user):
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
def check_emali_code(request: HttpRequest) -> HttpResponse:
    """绑定:检查邮箱验证码并获取OPT二维码"""
    uid = request.session['userID']
    user = get_user_by_id(uid)
    try:
        req_json = RequestLoadJson(request)
        Log.debug(str(req_json))
    except:
        return api_error("Json解析失败", 400)
    if user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您已绑定过OTP!'
        })
    auth_code = req_json.get('code')
    if not auth_code or not check_bind_otp_email_code(user, auth_code):
        return ResponseJson({'status': 0, 'msg': '验证码不正确'})
    token = pyotp.random_base32()
    if not OTP.objects.filter(user=user).exists():
        OTP.objects.create(user=user, token=token)
    else:
        OTP.objects.filter(user=user).update(token=token)
    return ResponseJson({
        'status': 1,
        'data': {
            'qrcode': pyotp.totp.TOTP(token).provisioning_uri(
                name=user.userName + "@" + user.realName,
                issuer_name=config().base.website_name
            )
        }
    })


@require_POST
def bind_otp_check(request: HttpRequest) -> HttpResponse:
    """绑定:检查OTP验证码"""
    try:
        req_json = RequestLoadJson(request)
    except:
        return api_error("Json解析失败", 400)
    uid = request.session['userID']
    user = get_user_by_id(uid)
    otp_code = req_json.get('code')
    if user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您已绑定过OTP!'
        })
    if not otp_code:
        return api_error("参数不完整")
    otp = OTP.objects.filter(user=user).first()
    if not otp or (otp and not otp.token):
        return ResponseJson({'status': 0, 'msg': '绑定错误，请尝试重新绑定'})
    if pyotp.TOTP(otp.token).verify(otp_code):
        otp.scanned = True
        otp.save()
        return ResponseJson({'status': 1, 'msg': '绑定成功'})
    return ResponseJson({'status': 0, 'msg': '绑定失败，请检查令牌'})
