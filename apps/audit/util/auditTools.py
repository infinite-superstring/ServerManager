from apps.user_manager.util.userUtils import get_user_by_id
from util.logger import Log
from apps.audit.models import Audit, Access_Log, FileChange_Log, System_Log

# 写访问日志
@Log.catch
def write_access_log(user_id, ip: str, module: str):
    """
    :param user_id: 用户id
    :param ip: 用户IP地址
    :param module: 模块
    :return:
    """
    Access_Log.objects.create(user=get_user_by_id(user_id), ip=ip, module=module)


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
def write_audit(user_id: int, action: str, module: str, content: str):
    """
    :param user_id: 用户ID
    :param action: 动作
    :param module: 模块
    :param content: 内容
    """
    Audit.objects.create(user=get_user_by_id(user_id), action=action, module=module, content=content)


# 写文件记录
@Log.catch
def write_file_change_log(user_id: int, action: str, filepath: str):
    """
    :param user_id: 用户ID
    :param action: 动作
    :param filepath: 目标
    """
    FileChange_Log.objects.create(user=get_user_by_id(user_id), action=action, filepath=filepath)
