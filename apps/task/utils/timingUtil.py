from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from util.logger import Log

class TimingUtil:
    __scheduler: BackgroundScheduler = BackgroundScheduler()

    def start(self):
        self.__scheduler.add_job(
            self.__new_checkIn_task(),
            trigger=CronTrigger(hour=4, minute=0),
            id='new_signIn_task',
            replace_existing=True,
        )
        self.__scheduler.start()
        Log.info("task:定时任务启动")

    def __new_checkIn_task(self):
        pass
