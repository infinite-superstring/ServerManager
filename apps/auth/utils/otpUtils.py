import pyotp
from django.apps import apps
from django.http import HttpRequest

from apps.auth.models import OTP
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id

config = apps.get_app_config('setting').get_config


def hasOTPBound(user: User) -> bool:
    """用户是否已绑定OTP"""
    return OTP.objects.filter(user=user, scanned=True).exists()


def getUserOTP_Token(user: User) -> str:
    """获取用户已绑定的OTP Token"""
    return OTP.objects.filter(user=user, scanned=True).first().token


def verify_otp(user: User, code: str) -> bool:
    """验证用户输入的OTP"""
    user_bind_status = hasOTPBound(user)
    if not config().security.force_otp_bind and not user_bind_status:
        return True
    if not user_bind_status:
        return False
    return pyotp.TOTP(getUserOTP_Token(user)).verify(code)


def verify_otp_for_request(request: HttpRequest, code) -> bool:
    """通过请求体拿到用户信息验证OTP"""
    uid = request.session['userID']
    user = get_user_by_id(uid)
    return verify_otp(user, code)
