import asyncio
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asgiref.sync import async_to_sync, sync_to_async
from django.core.cache import cache

from apps.web_status.models import Web_Site_Log, Web_Site
from consumers.AsyncConsumer import AsyncBaseConsumer
from util.jsonEncoder import ComplexEncoder
from util.logger import Log


class WebStatusClient(AsyncBaseConsumer):
    __NAME = 'WebStatusClient_'
    __userID = None
    __web_list = []
    _polling_send = None

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
        self.__web_list = Web_Site.objects.all()
        runtime_data = await self._getRuntime()
        await self.send_json({
            'type': 'initData',
            'data': runtime_data
        })
        # 开始轮询发送消息
        self._startPolling()
        await sync_to_async(cache.set)(f'{self.__NAME}web_list', self.__web_list)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.__NAME}{self.__userID}",
            self.channel_name
        )
        self._polling_send.shutdown()
        Log.debug("已断开网络监控套接字")
        await self.close()

    async def receive(self, **kwargs):
        await self.send_json({
            "type": "receive",
            "data": "over!"
        })

    async def _getRuntime(self):
        log_data = (
            Web_Site_Log.objects
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
        w = cache.get(f'{self.__NAME}web_list')
        if not w:
            self.__web_list = Web_Site.objects.all()
        async for web in self.__web_list:
            runtime: Web_Site_Log = cache.get(f'web_status_log_{web.id}')
            await self.send_json(
                {
                    'type': 'newData',
                    'data': {
                        web.host: {
                            'time': runtime.time.strftime("%H:%M:%S") if runtime else None,
                            'data': int(runtime.delay) if runtime else None,
                            'online': str(runtime.status).startswith('2')  if runtime else None,
                            'status_code': runtime.status  if runtime else None
                        }
                    }
                }
            )
