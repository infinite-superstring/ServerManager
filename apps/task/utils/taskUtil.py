import calendar
import random
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
    return task


def year_month_to_start_and_end_time(years: str):
    """
    根据字符串年月转换为 年月的开始时间和结束时间
    """
    year, month = years.split("-")
    year = int(year)
    month = int(month)

    # 一个月的第一天的最开始
    start_time = datetime(year, month, 1, 0, 0, 0)

    # 获取当前月份的天数
    last_day = calendar.monthrange(year, month)[1]

    # 一个月的最后一天的最后的时间
    end_time = datetime(year, month, last_day, 23, 59, 59, 999999)

    return start_time, end_time


def randomColor():
    """
    随机获取一个颜色
    """
    colors = ['blue', 'indigo', 'deep-purple', 'cyan', 'green', 'orange', 'grey darken-1']
    return colors[int(random.randint(0, len(colors) - 1))]
