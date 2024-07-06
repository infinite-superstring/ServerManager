import asyncio
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models import QuerySet

from apps.web_status.models import Web_Site_Log, Web_Site
from consumers.AsyncConsumer import AsyncBaseConsumer
from util import pageUtils
from util.jsonEncoder import ComplexEncoder
from util.logger import Log


class WebStatusClient(AsyncBaseConsumer):
    __NAME = 'WebStatusClient_'
    __userID = None
    __web_list = []
    _polling_send = None
    __page = 1
    __pageSize = 6
    __name = ''

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    async def connect(self):
        self.__userID = self.scope['session']['userID']
        if not self.__userID:
            await self.close(0)
            return
        # 校验通过
        await self.accept()
        await self.channel_layer.group_add(
            f"{self.__NAME}{self.__userID}",
            self.channel_name
        )
        self.__page = self.scope['url_route']['kwargs']['page']
        self.__name = self.scope['url_route']['kwargs'].get('name', '')
        self.__web_list = Web_Site.objects.filter(title__contains=self.__name, host__contains=self.__name,
                                                  description__contains=self.__name).order_by('id')
        await self.send_json({
            'type': 'hello',
        })
        await sync_to_async(cache.set)(f'web_status_web_list', self.__web_list)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.__NAME}{self.__userID}",
            self.channel_name
        )
        self._polling_send.shutdown() if self._polling_send else None
        Log.debug("已断开网络监控套接字")
        await self.close()

    async def receive(self, **kwargs):
        channel = get_channel_layer()
        t = json.loads(kwargs['text_data']).get('type', '')
        d = json.loads(kwargs['text_data']).get('data', {})
        await channel.group_send(
            f'{self.__NAME}{self.__userID}', {
                'type': t,
                'data': d
            })

    async def initData(self, data):
        runtime_data = await self.__getRuntime()
        await self.send_json({
            'type': 'initData',
            'data': runtime_data
        })
        # 开始轮询发送消息
        self._startPolling()

    async def __getRuntime(self):
        page_web = await self.pagination()
        if page_web is None:
            return
        log_data = (
            Web_Site_Log.objects
            .filter(web_id__in=[web['id'] async for web in page_web])
            .values('web__host', 'time', 'delay', 'status')
            .order_by('web__host', 'time')  # 假设按host和time排序以保证数据连续性
        )
        result = {}
        current_host = None
        times = []
        datas = []
        statuses = []

        async for log in log_data:
            if current_host != log['web__host']:
                if current_host is not None:
                    # 处理完上一组数据
                    result[current_host] = {
                        'time': times,
                        'data': datas,
                        'online': bool(str(statuses[-1]).startswith('2')),
                        'status_code': statuses
                    }
                current_host = log['web__host']
                times = []  # 重置列表
                datas = []  # 重置列表
                statuses = []  # 重置状态码列表

            times.append(log['time'].strftime("%H:%M:%S"))
            datas.append(str(log['delay']))
            statuses.append(log['status'])

        # 处理最后一个host的数据
        if current_host is not None:
            result[current_host] = {
                'time': times,
                'data': datas,
                'online': bool(str(statuses[-1]).startswith('2')),
                'status_code': statuses
            }
        return result

    def _startPolling(self):
        loop = asyncio.get_event_loop()
        # 开启定时任务
        self._polling_send = AsyncIOScheduler(event_loop=loop)
        self._polling_send.add_job(self._sendNewData, IntervalTrigger(seconds=5))  # 每5秒执行一次
        self._polling_send.start()

    async def _sendNewData(self):
        self.__web_list = cache.get(f'web_status_web_list')
        if not self.__web_list:
            self.__web_list = Web_Site.objects.filter(title__contains=self.__name, host__contains=self.__name,
                                                      description__contains=self.__name).order_by('id')
        page_web = await self.pagination()
        if page_web is None:
            return
        page_web: QuerySet[Web_Site] = Web_Site.objects.filter(id__in=[web['id'] async for web in page_web])
        async for web in page_web:
            runtime: Web_Site_Log = cache.get(f'web_status_log_{web.id}')
            await self.send_json(
                {
                    'type': 'newData',
                    'data': {
                        web.host: {
                            'time': runtime.time.strftime("%H:%M:%S") if runtime else None,
                            'data': int(runtime.delay) if runtime else None,
                            'online': str(runtime.status).startswith('2') if runtime else None,
                            'status_code': runtime.status if runtime else None
                        }
                    }
                }
            )

    async def pagination(self):
        if not await self.__web_list.aexists():
            return None
        return await sync_to_async(pageUtils.get_page_content)(self.__web_list, int(self.__page), int(self.__pageSize))
