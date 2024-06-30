import re
from apps.web_status.models import Web_Site, Web_Site_Log, Web_Site_Abnormal_Log
from util import httpCode


def is_valid_host(host):
    # 创建正则表达式
    if host == 'localhost' or host == 'http://localhost' or host == 'https://localhost':
        return True
    pattern = r'^(((ht)tps?):\/\/)?[\w-]+(\.[\w-]+)+([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$'
    if re.match(pattern, host):
        return True
    else:
        return False


def hostIsExist(host):
    """
    检查给定的主机是否已经存在。
    """
    web = Web_Site.objects.filter(host=host)
    if web:
        return True
    else:
        return False


def createLog(web_id, status, delay):
    """
    创建日志
    """
    if Web_Site_Log.objects.filter(web_id=web_id).count() >= 30:
        Web_Site_Log.objects.filter(web_id=web_id).first().delete()
    return Web_Site_Log.objects.create(
        web_id=web_id,
        status=status,
        delay=delay,
    )


def createErrLog(web_id, status, error_info=''):
    """
    创建异常日志
    """
    if not error_info:
        error_info = byStatusCodeGetErrInfo(status)
    Web_Site_Abnormal_Log.objects.create(
        web_id=web_id,
        status=status,
        error_type=byStatusCodeGetErrType(status),
        error_info=error_info,
    )


def byStatusCodeGetErrInfo(status):
    """
    根据状态码获取错误信息
    """
    return httpCode.httpCodeMap.get(status, '未知错误')


def byStatusCodeGetErrType(status):
    """
    根据状态码获取错误类型
    """
    if str(status).startswith('4'):
        return '客户端错误'
    if str(status).startswith('5'):
        return '服务器错误'
