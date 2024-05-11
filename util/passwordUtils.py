import hashlib
import random
import re
import secrets
import string

# import app.util.Config
from django.apps import apps

from apps.user_manager.models import User


def PasswordToMd5(password: str):
    md5 = hashlib.md5(apps.get_app_config("setting").get_base_config().get("main").get("Cryptographic_salt").encode())
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


def GeneratePassword(length=12):
    """随机生成密码"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def verifyPasswordRules(password):
    """
    验证密码是否符合规则
    :param password: str 密码
    :return: bool
    """
    return re.match('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[^\w\s]).{6,16}', password)


def encrypt_password(password):
    # 生成随机盐值
    salt = secrets.token_hex(32)
    # 使用盐值与密码进行加密
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    # 返回加密后的密码和盐值
    return hashed_password, salt


def verify_password(hashed_password, password, salt):
    """
    验证密码
    """
    return hashed_password == str(hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ))
