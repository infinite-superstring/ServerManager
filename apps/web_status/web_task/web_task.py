from django.apps import AppConfig
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from util.logger import Log
import requests
from threading import Thread


class WebTask(AppConfig):
    name = 'apps.web_status.web_task'

    def ready(self):
        # 启动一个新的异步事件循环
        from apps.web_status.models import Web_Status
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(event_loop=loop)
        # 添加一个定时任务
        scheduler.add_job(self.monitor, IntervalTrigger(seconds=10))
        # 启动调度器
        Log.info("启动网站监控")
        scheduler.start()

    async def monitor(self):
        # 你的异步逻辑代码
        await self.__start_monitor()
        await asyncio.sleep(1)

    async def __start_monitor(self):
        from apps.web_status.models import Web_Status
        web_list = Web_Status.objects.all()
        async for web in web_list:
            t = Thread(target=self.__getWebStatus, args=(web,))
            t.start()

    def __getWebStatus(self, web):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            }
            host = web.host if web.host.startswith('http') else 'http://' + web.host
            result = requests.get(url=host, headers=headers, timeout=1)
            delay = result.elapsed.microseconds / 1000
            Log.debug(f'网站‘{host}’状态为‘{result.status_code}’延迟为‘{delay}ms’')
            web.status = result.status_code
            web.delay = delay
            if str(web.status).startswith('4'):
                web.online = False
            else:
                web.online = True
        except TimeoutError as e:
            web.status = 404
            web.online = False
        except Exception as e:
            Log.debug(e)
            web.status = 500
            # 在此记录错误日志
        finally:
            web.save()
