import json

from util.jsonEncoder import ComplexEncoder
from util.logger import Log

from channels.generic.websocket import AsyncWebsocketConsumer


class MessageClient(AsyncWebsocketConsumer):
    __userID: int = None

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    async def connect(self):
        self.__userID = self.scope['session'].get('userID')
        if not self.__userID:
            await self.close(0)
            return
        # 校验通过
        await self.accept()
        await self.channel_layer.group_add(
            f"message_client_{self.__userID}",
            self.channel_name
        )
        await self.send_json({
            "type": "connect",
            "data": 'hello'
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"message_client_{self.__userID}",
            self.channel_name
        )
        await self.close()

    async def receive(self, **kwargs):
        await self.send_json({
            "type": "receive",
            "data": "over!"
        })

    async def newMessage(self, event):
        await self.send_json({
            "type": event['data']['type'],
            "data": event['data']['data']
        })
