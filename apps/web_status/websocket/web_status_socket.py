import json

from consumers.AsyncConsumer import AsyncBaseConsumer
from util.jsonEncoder import ComplexEncoder
from util.logger import Log


class WebStatusClient(AsyncBaseConsumer):
    __NAME = 'WebStatusClient_'
    __url_base64 = None
    __userID = None

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    async def connect(self):
        self.__userID = self.scope['session']['userID']
        self.__url_base64 = self.scope['url_route']['kwargs']['url_base64']
        if not self.__userID:
            await self.close(0)
            return
        # 校验通过
        await self.accept()
        await self.channel_layer.group_add(
            f"{self.__NAME}{self.__url_base64}",
            self.channel_name
        )
        await self.send_json({
            "type": "connect",
            "data": 'hello'
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.__NAME}{self.__userID}",
            self.channel_name
        )
        await self.close()

    async def receive(self, **kwargs):
        await self.send_json({
            "type": "receive",
            "data": "over!"
        })
