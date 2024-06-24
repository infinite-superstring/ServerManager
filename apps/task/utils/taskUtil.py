from datetime import datetime

from apps.task.models import Task


def get_today_start_time():
    """
    获取当天的开始时间（00:00:00）

    Returns:
        datetime: 当天日期的开始时间的datetime对象
    """
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def get_today_end_time():
    """
    获取当天的结束时间（23:59:59）

    Returns:
        datetime: 当天日期的结束时间的datetime对象
    """
    return datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)


def get_current_time():
    """
    获取当前时间
    """
    return datetime.now()


def byUserIDGetAttendanceState(user_id: int):
    """
    根据用户ID获取用户当天的签到状态
    """
    task: Task = Task.objects.filter(
        type=0,
        target_user_id=user_id,
        start_time__gte=get_today_start_time(),
        end_time__lte=get_today_end_time()).first()
    return task


def createAttendance(user_id: int):
    """
    创建用户当天的签到任务
    """
    task = Task(init_User_id=1,
                target_user_id=user_id,
                type=0,
                status=1,
                start_time=get_today_start_time(),
                end_time=get_current_time(),
                need_end_time=get_today_end_time(),
                description="签到",
                result="")
    task.save()
