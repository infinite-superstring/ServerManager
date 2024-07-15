import random
import time

from django.apps import apps
from django.core.cache import cache

from apps.message.models import MessageBody
from apps.message.api.message import send_email
from apps.user_manager.models import User
from apps.auth.models import OTP

config = apps.get_app_config('setting').get_config


def user_otp_is_binding(user: User):
    return OTP.objects.filter(user=user, scanned=True).exists()


def generate_verification_code(length=8):
    digits = "0123456789"
    verification_code = "".join(random.choice(digits) for _ in range(length))
    return verification_code


def send_auth_code(user: User):
    code = generate_verification_code(config().security.auth_code_length)
    currentTime = time.time()
    cache.set(f"getAuthCode_{user.id}", {
        "code": code,
        'start_time': currentTime,
        'end_time': currentTime + config().security.auth_code_resend_interval,
    }, config().security.auth_code_timeout * 60)
    title = f"需验证您的操作"
    content = f"【操作验证】验证码：{code}（{config().security.auth_code_timeout}分钟内有效）。您正在绑定OTP令牌，请勿将验证码告诉他人。\n（系统消息请勿回复）"
    return send_email(MessageBody(
        title=title,
        content=content,
        recipient=user,
        email_sms_only=True
    ))


def check_auth_code(user: User, code):
    """
    验证 验证码
    :param user: 用户实例
    :param code: 验证码
    """
    cache_code = cache.get(f"getAuthCode_{user.id}")
    if cache_code is None:
        return False
    if cache_code.get('code') != code:
        return False
    return True
