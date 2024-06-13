import random
import time

from django.apps import apps
from django.core.cache import cache
from django.db.models import QuerySet

from apps.message.models import MessageBody
from apps.message.utils.messageUtil import send
from apps.user_manager.models import User
from apps.auth.models import OTP

config = apps.get_app_config('setting').get_config

def user_otp_is_binding(user: User):
    return OTP.objects.filter(user=user).exists()

def user_otp_bind(user: User):
    """用户绑定OTP"""

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
        'end_time': currentTime+config().security.auth_code_resend_interval,
    }, config().security.auth_code_timeout * 60)
    title = f"【{config().base.website_name}】验证您的操作"
    content = f"【操作验证】验证码：{code}（{config().security.auth_code_timeout}分钟内有效）。您正在执行高危操作，请勿将验证码告诉他人。\n（系统消息请勿回复）"
    return send(MessageBody(
        title=title,
        content=content,
        recipient=user,
        email_sms_only=True
    ))
