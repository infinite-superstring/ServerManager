import re
from datetime import datetime

from django.core.cache import cache

from apps.web_status.models import Web_Site, Web_Site_Log, Web_Site_Abnormal_Log
from util import httpCode


def get_or_create_web_site_log(web_id):
    """
    从缓存中获取Web_Site_Log对象，如果不存在，则创建一个新的实例。
    """
    cache_key = f'web_status_log_{web_id}'
    cached_log = cache.get(cache_key)
    if cached_log is not None:
        return cached_log

    return Web_Site_Log()


def get_latest_or_default_abnormal_log(web_id):
    """
    获取与web_id相关的最后一个Web_Site_Abnormal_Log记录，如果没有记录，则创建一个新的实例。
    """
    try:
        # 尝试获取最新的异常记录
        latest_abnormal_log = Web_Site_Abnormal_Log.objects.filter(web_id=web_id).latest('end_time')
    except Web_Site_Abnormal_Log.DoesNotExist:
        # 如果没有找到记录，则创建一个新的实例
        latest_abnormal_log = Web_Site_Abnormal_Log()

    return latest_abnormal_log


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


def createErrLog(web_id, status, error_info=None, start_time=None, end_time=None):
    """
    创建或更新异常日志
    如果传入结束时间，则查询最近开始时间距离现在最近的一条记录并更新其结束时间
    """
    if error_info is None:
        error_info = httpCode.httpCodeMap.get(int(status), '未知错误')

    if end_time:
        recent_log = Web_Site_Abnormal_Log.objects.filter(
            web_id=web_id,
            end_time__isnull=True
        ).order_by('-start_time').first()

        # 如果找到了符合条件的记录
        if recent_log:
            recent_log.end_time = end_time
            recent_log.save()
            return

    if status == 200 or status == '200':
        return
    web = Web_Site_Abnormal_Log()
    web.web_id = web_id
    web.status = status
    web.error_type = byStatusCodeGetErrType(status)
    web.error_info = error_info
    if start_time:
        log: Web_Site_Abnormal_Log = (Web_Site_Abnormal_Log.objects.filter(web_id=web_id)
                                      .order_by('-start_time').first())
        if log and not log.end_time:
            return
        web.start_time = start_time
    if end_time:
        web.end_time = end_time
    web.save()


def byStatusCodeGetErrType(status):
    """
    根据状态码获取错误类型
    """
    if str(status).startswith('1'):
        return '协议变更'
    if str(status).startswith('2'):
        return '完成'
    if str(status).startswith('3'):
        return '重定向'
    if str(status).startswith('4'):
        return '客户端错误'
    if str(status).startswith('5'):
        return '服务器错误'


def handleError(web_id: int, status: str, error_host: list[int]):
    """
    处理监控网站错误
    """
    host_state = status.startswith('2')
    if web_id in error_host:
        if host_state:
            createErrLog(
                web_id=web_id,
                status=status,
                end_time=datetime.now()
            )
            error_host.remove(web_id)
    else:
        if not host_state:
            error_host.append(web_id)
            createErrLog(
                web_id=web_id,
                status=status,
                start_time=datetime.now()
            )
    return error_host
