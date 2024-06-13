from datetime import datetime, timedelta
from django.utils import timezone
from django.apps import apps
from apps.node_manager.models import Node_UsageData
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from util.logger import Log

class tasks:
    __scheduler: BackgroundScheduler = BackgroundScheduler()
    def start(self):
        # self.__scheduler.add_jobstore(BackgroundScheduler(), 'default')

        # 添加定时任务
        self.__scheduler.add_job(
            self.__clean_usage_data_old_data,
            # 'interval',
            # seconds=3,
            trigger=CronTrigger(hour=4, minute=0),
            id='clean_usage_data_old_data',  # 唯一标识任务的 ID
            replace_existing=True,
        )

        self.__scheduler.start()
        # self.__clean_usage_data_old_data()
        Log.success("Node Manager: Scheduler started")

    def __clean_usage_data_old_data(self):
        """清理运行数据旧数据"""
        threshold_date = timezone.now() - timedelta(days=apps.get_app_config('setting').get_config().node_usage.data_storage_time)  # 设置数据过期的时限
        Node_UsageData.objects.filter(timestamp__lt=threshold_date).delete()
        Log.success(f'清理任务已完成，删除了 {threshold_date} 之前的数据')