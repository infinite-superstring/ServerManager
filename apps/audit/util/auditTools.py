from apps.user_manager.util.userUtils import get_user_by_id
from apps.user_manager.models import User
from util.Request import getClientIp
from util.logger import Log
from apps.audit.models import Audit, Access_Log, FileChange_Log, System_Log, User_Session_Log, Node_Session_Log
from django.http import HttpRequest

# 写访问日志
@Log.catch
def write_access_log(user: int | User, ip: str | HttpRequest, module: str, content: str = '') -> None:
    """
    :param user: 用户id
    :param ip: 用户IP地址
    :param module: 模块
    :return:
    """
    if isinstance(user, int):
        user = get_user_by_id(user)
    elif not isinstance(user, User):
        raise TypeError(f'不支持的数据格式：{type(user)}')
    if isinstance(ip, str):
        pass
    elif isinstance(ip, HttpRequest):
        ip = getClientIp(ip)
    else:
        raise TypeError(f'不支持的数据格式：{type(ip)}')
    Access_Log.objects.create(user=user, ip=ip, module=module, content=content)


# 写系统日志
@Log.catch
def write_system_log(level: int, module: str, content: str):
    """
    :param level: 日志等级
    :param module: 模块
    :param content: 内容
    :return:
    """
    System_Log.objects.create(level=level, module=module, content=content)


# 写审计内容
@Log.catch
def write_audit(user: int | User, action: str, module: str, content: str):
    """
    :param user: 用户
    :param action: 动作
    :param module: 模块
    :param content: 内容
    """
    if isinstance(user, int):
        user = get_user_by_id(user)
    elif not isinstance(user, User):
        raise TypeError(f'不支持的数据格式：{type(user)}')
    Audit.objects.create(user=user, action=action, module=module, content=content)


# 写文件记录
@Log.catch
def write_file_change_log(user: int | User, action: str, filepath: str):
    """
    :param user: 用户
    :param action: 动作
    :param filepath: 目标
    """
    if isinstance(user, int):
        user = get_user_by_id(user)
    elif not isinstance(user, User):
        raise TypeError(f'不支持的数据格式：{type(user)}')
    FileChange_Log.objects.create(user=user, action=action, filepath=filepath)


@Log.catch
def write_user_session_log(user_id: int, action: int, ip: str):
    """
    用户会话记录
    :param user_id: 用户ID
    :param action: 动作
    :param ip: IP地址
    """
    User_Session_Log.objects.create(user=get_user_by_id(user_id), action=action, ip=ip)


@Log.catch
def write_node_session_log(node_uuid, action: int, ip: str):
    """
    节点会话记录
    :param node_uuid: 节点
    :param action: 动作
    :param ip: IP地址
    """
    Node_Session_Log.objects.create(node_id=node_uuid, action=action, ip=ip)
