import hashlib
import random
import re
import string

# import app.util.Config
from django.apps import apps


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

