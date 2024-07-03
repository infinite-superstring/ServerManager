import pyotp

from apps.auth.models import OTP
from apps.user_manager.models import User


def hasOTPBound(user: User) -> bool:
    """用户是否已绑定OTP"""
    return OTP.objects.filter(user=user, scanned=True).exists()

def getUserOTP_Token(user: User) -> str:
    """获取用户已绑定的OTP Token"""
    return OTP.objects.filter(user=user, scanned=True).first().token

def check_otp(user: User, otp: str) -> bool:
    """验证用户输入的OTP"""
    if not hasOTPBound(user):
        return False
    return pyotp.TOTP(getUserOTP_Token(user)).verify(otp)