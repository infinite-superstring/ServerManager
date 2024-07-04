"""
初始化新用户
"""
import time

import pyotp
from django.apps import apps
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

from apps.user_manager.util.userUtils import get_user_by_id
from apps.auth.utils.authCodeUtils import generate_verification_code
from apps.message.api.message import send_email
from apps.message.models import MessageBody
from apps.auth.models import OTP
from util.Request import RequestLoadJson
from util.passwordUtils import verifyPasswordRules, encrypt_password
from util.result import api_error, error, success
from util.logger import Log

config = apps.get_app_config('setting').get_config


def sendEmailVerifyCode(request: HttpRequest) -> HttpResponse:
    """发送邮箱验证码"""
    if not request.method == 'GET':
        return api_error("请求方法不正确", 405)
    uid = request.session['userID']
    user = get_user_by_id(uid)
    print(user.isNewUser)
    if not user.isNewUser:
        return api_error("您不是新用户，请通过正常渠道修改用户信息")
    email = request.GET.get('email', None)
    if not email:
        return api_error("参数不完整")
    user_cache = cache.get(f"init_user_email_verify_{user.id}", None)
    if user_cache and user_cache.get('end_time') and user_cache.get('end_time') > time.time():
        return error(f'冷却中! 请等待{int(user_cache.get("end_time") - time.time())}秒')
    code = generate_verification_code(config().security.auth_code_length)
    currentTime = time.time()
    cache.set(f"init_user_email_verify_{user.id}", {
        "code": code,
        'email': email,
        'start_time': currentTime,
        'end_time': currentTime + config().security.auth_code_resend_interval,
    }, config().security.auth_code_timeout * 60)
    title = f"需验证您的操作"
    content = f"【操作验证】验证码：{code}（{config().security.auth_code_timeout}分钟内有效）。您正在绑定OTP令牌，请勿将验证码告诉他人。\n（系统消息请勿回复）"
    print(code)
    send_email(MessageBody(
        title=title,
        content=content,
        recipient=user,
        email_sms_only=True
    ))
    return success({
        'interval': config().security.auth_code_resend_interval,
    })


def initUserInfo(request: HttpRequest) -> HttpResponse:
    """初始化用户信息"""
    if not request.method == 'POST':
        return api_error("请求方法不正确", 405)
    try:
        req_json = RequestLoadJson(request)
        Log.debug(str(req_json))
    except:
        return api_error("Json解析失败", 400)
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if not user.isNewUser:
        return api_error("您不是新用户，请通过正常渠道修改用户信息")
    email = req_json.get('email')
    password = req_json.get('password')
    verify_code = req_json.get('verify_code')
    if not email or not password or not verify_code:
        return api_error("参数不完整")
    user_cache = cache.get(f"init_user_email_verify_{user.id}", None)
    if not user_cache or user_cache.get("code") != verify_code:
        return error("验证码错误")
    if user_cache.get('email') != email:
        return error("要绑定的邮箱与接收验证码的邮箱不一致")
    user.email = email
    pv, pv_msg = verifyPasswordRules(password, config().security.password_level)
    if not pv:
        return error({"status": 0, "msg": f"新密码格式不合规（{pv_msg}）"})
    user.password, user.passwordSalt = encrypt_password(password)
    user.save()
    token = pyotp.random_base32()
    if not OTP.objects.filter(user=user).exists():
        OTP.objects.create(user=user, token=token)
    else:
        OTP.objects.filter(user=user).update(token=token)
    return success({
        'qrcode': pyotp.totp.TOTP(token).provisioning_uri(
            name=user.userName + "@" + user.realName,
            issuer_name=config().base.website_name
        )
    })

def checkOTP_Code(request: HttpRequest) -> HttpResponse:
    if not request.method == 'GET':
        return api_error("请求方法不正确", 405)
    code = request.GET.get('code', None)
    uid = request.session['userID']
    user = get_user_by_id(uid)
    otp = OTP.objects.filter(user=user).first()
    if not otp or (otp and not otp.token):
        return error("绑定错误，请尝试重新绑定")
    if pyotp.TOTP(otp.token).verify(code):
        otp.scanned = True
        otp.save()
        return success()
    user.isNewUser = False
    user.save()
    return error('绑定失败，请检查验证码')