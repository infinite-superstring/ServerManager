import hashlib
import random
import re
import secrets
import string
from re import Match


def GeneratePassword(length=12):
    """随机生成密码"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def verifyPasswordRules(password, level=0) -> tuple[Match[str] | None, str] | tuple[bool, str]:
    """
    验证密码是否符合规则
    :param password: str 密码
    :param level: int
    :return: tuple[Match[str] | None, str] | tuple[bool, str]
    1.无限制(仅限制长度 6-16位)
    2.弱密码(限制数字+英文 6-16位)
    3.中密码(限制数字+英文大小写 8-20位)
    4.强密码(限制数字+英文大小写+特殊符号 8-20位)
    """
    match level:
        case 1:
            return re.match(r'^.{6,16}$', password), "仅限制长度 6-16位"
        case 2:
            return re.match(r'^(?=.*\d)(?=.*[a-zA-Z]).{6,16}$', password), "数字+英文 6-16位"
        case 3:
            return re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$', password), "数字+英文大小写 8-20位"
        case 4:
            return re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[^\w\s]).{8,20}', password), "数字+英文大小写+特殊符号 8-20位"
    return False, "未知的密码等级"


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
