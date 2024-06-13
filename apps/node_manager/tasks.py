from datetime import datetime, timedelta
from django.utils import timezone
from django.apps import apps
from apps.node_manager.models import Node_UsageData
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from util.logger import Log

class tasks:
    __scheduler: BackgroundScheduler = BackgroundScheduler()
    def start(self):
        # 添加定时任务
        self.__scheduler.add_job(
            self.__clean_usage_data_old_data,
            trigger=CronTrigger(hour=4, minute=0),
            id='clean_usage_data_old_data',  # 唯一标识任务的 ID
            replace_existing=True,
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