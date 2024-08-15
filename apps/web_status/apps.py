from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.apps import AppConfig
from django.apps import apps
from django.core.cache import cache

from util.logger import Log


class WebStatusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web_status'
    error_host: list[int] = []
    __thread_pool: ThreadPoolExecutor = None

    def __init__(self, *args, **kwargs):
        Log.info("Web Status: Initializing start")
        self.__thread_pool = ThreadPoolExecutor(max_workers=5)  # 线程池
        super().__init__(*args, **kwargs)

    def ready(self):
        scheduler = BackgroundScheduler()
        config = apps.get_app_config('setting').get_config
        if not config():
            return
        heartbeat = config().web_status.heartbeat
        if heartbeat is None:
            return
        scheduler.add_job(self.__start_monitor, IntervalTrigger(seconds=heartbeat))
        scheduler.start()
        Log.success("Web Status: Initialization complete")
        auto_empty_log = BackgroundScheduler()
        auto_empty_log.add_job(self.__auto_empty_log, IntervalTrigger(hours=1))
        auto_empty_log.start()

    def __start_monitor(self):
        from apps.web_status.models import Web_Site
        web_list = Web_Site.objects.all()
        # with ThreadPoolExecutor(max_workers=5) as pool:
        #     futures = [pool.submit(self.__getWebStatus, web) for web in web_list]
        for web in web_list:
            # self.__thread_pool.submit(self.__getWebStatus, web, )
            # self.__thread_pool.shutdown()
            Thread(target=self.__getWebStatus, args=(web,)).start()

    def __getWebStatus(self, web):
        from apps.web_status.utils import webUtil
        host = web.host
        result = None
        delay = 0
        code: int = 200
        try:
            config = apps.get_app_config('setting').get_config
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            }
            host = web.host if web.host.startswith('http') else 'http://' + web.host
            timeout = config().web_status.timeout
            result = requests.get(url=host, headers=headers, timeout=timeout)
            delay = result.elapsed.microseconds / 1000
        except TimeoutError as e:
            code = 408
        except requests.exceptions.ConnectionError as e:
            code = 500
        except requests.exceptions.Timeout as e:
            code = 408
        except requests.exceptions.RequestException as e:
            code = 500
        except Exception as e:
            code = 500
            Log.debug(e)
        finally:
            code = result.status_code if result else code
            self.error_host = webUtil.handleError(web.id, str(code), self.error_host)
            log = webUtil.createLog(web.id, code, delay)
            cache.set(f'web_status_log_{web.id}', log, 60)
            if not str(code).startswith('2'):
                # Log.debug(f'{host} 错误 {code}')
                pass
            return

    def __auto_empty_log(self):
        from apps.web_status.models import Web_Site_Log
        Web_Site_Log.objects.all().delete()
