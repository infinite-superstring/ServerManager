from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from util.logger import Log
import requests
from threading import Thread
from django.apps import apps
from django.core.cache import cache


class WebStatusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web_status'

    def __init__(self, *args, **kwargs):
        Log.info("Web Status: Initializing start")
        super().__init__(*args, **kwargs)

    def ready(self):
        # 启动一个新的异步事件循环
        # loop = asyncio.get_event_loop()
        scheduler = BackgroundScheduler()
        # 添加一个定时任务
        config = apps.get_app_config('setting').get_config
        if not config():
            return
        heartbeat = config().web_status.heartbeat
        if heartbeat is None:
            return
        scheduler.add_job(self.__start_monitor, IntervalTrigger(seconds=heartbeat))
        # 启动调度器
        scheduler.start()
        Log.success("Web Status: Initialization complete")

    def __start_monitor(self):
        from apps.web_status.models import Web_Site
        web_list = Web_Site.objects.all()
        for web in web_list:
            t = Thread(target=self.__getWebStatus, args=(web,))
            t.start()

    def __getWebStatus(self, web):
        from apps.web_status.utils import webUtil
        host = web.host
        result = None
        delay = 0
        try:
            config = apps.get_app_config('setting').get_config
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            }
            host = web.host if web.host.startswith('http') else 'http://' + web.host
            result = requests.get(url=host, headers=headers, timeout=config().web_status.timeout)
            delay = result.elapsed.microseconds / 1000
            if str(result.status_code).startswith('4'):
                webUtil.createErrLog(host, result.status_code)
            else:
                pass
        except TimeoutError as e:
            webUtil.createErrLog(host, 408)
            pass
        except Exception as e:
            Log.debug(e)
            webUtil.createErrLog(web_id=web.id, status=result.status_code if result is not None else 500)
            # 在此记录错误日志
        finally:
            status_code = result.status_code if result is not None else 500
            Log.debug(f'网站‘{host}’状态为‘{status_code}’延迟为‘{delay}ms’')
            log = webUtil.createLog(web.id, status_code, delay)
            cache.set(f'web_status_log_{web.id}', log, 60)
