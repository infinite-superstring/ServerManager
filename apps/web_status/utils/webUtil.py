import re
from apps.web_status.models import Web_Status


def is_valid_host(host):
    # 创建正则表达式
    if host == 'localhost' or host == 'http://localhost' or host == 'https://localhost':
        return True
    pattern = r'^(((ht)tps?):\/\/)?[\w-]+(\.[\w-]+)+([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$'
    if re.match(pattern, host):
        return True
    else:
        return False


def is_valid_port(port):
    """
    检查给定的端口是否为有效的端口号。
    :param port: 用户输入的端口号字符串
    :return: 如果端口号是合法的则返回True，否则返回False
    """
    try:
        port = int(port)
        return 0 < port < 65536
    except ValueError:
        return False


def hostIsExist(host):
    """
    检查给定的主机是否已经存在。
    """
    web = Web_Status.objects.filter(host=host)
    if web:
        return True
    else:
        return False
