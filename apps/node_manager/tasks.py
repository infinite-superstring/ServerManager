import time
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from django.apps import apps
from apps.node_manager.models import Node_UsageData
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from apps.node_manager.utils.nodeUtil import get_node_warning_count
from util.logger import Log

class tasks:
    __scheduler: BackgroundScheduler = BackgroundScheduler()
    def start(self):
        # 注册定时任务
        self.__scheduler.add_job(  # 清理旧数据
            self.__clean_usage_data_old_data,
            trigger=CronTrigger(hour=4, minute=0),
            id='clean_usage_data_old_data',  # 唯一标识任务的 ID
            replace_existing=True,
        )
        self.__scheduler.add_job(  # 处理告警趋势
            self.__handle_alarm_trends,
            id='handle_alarm_trends',  # 唯一标识任务的 ID
            replace_existing=True,
            trigger='interval',
            seconds=60,
        )

        self.__scheduler.start()
        Log.success("Node Manager: Scheduler ready")

    def __clean_usage_data_old_data(self):
        """清理运行数据旧数据"""
        threshold_date = timezone.now() - timedelta(days=apps.get_app_config('setting').get_config().node_usage.data_storage_time)  # 设置数据过期的时限
        del_objects = Node_UsageData.objects.filter(timestamp__lt=threshold_date)
        count = del_objects.count()
        del_objects.delete()
        Log.success(f'Node Manager: 清理任务已完成，删除了 {threshold_date} 之前的数据(影响了{count}条数据)')

    def __handle_alarm_trends(self):
        """处理告警趋势"""
        # 获取当前时间戳的分钟部分
        current_minute = int(time.time() // 60)
        # 使用请求的路径作为键
        key = f"alarm_trend:{current_minute}"
        # 增加计数
        cache.set(key, get_node_warning_count(), timeout=3600)