import json

from apps.user_manager.util.userUtils import get_user_by_id
from util.jsonEncoder import ComplexEncoder
from util.logger import Log

from channels.generic.websocket import AsyncWebsocketConsumer


class MessageClient(AsyncWebsocketConsumer):
    __auth: bool = False
    __config: dict = None
    __userID: int = None
    __clientIP: str = None
    __client_UUID: str = None

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    async def connect(self):
        userId = self.scope['session']['userID']
        if not userId:
            await self.close(0)
            return
        __userId = userId
        # 校验通过
        await self.accept()
        await self.channel_layer.group_add(
            f"message_client_{__userId}",
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

    async def receive(self):
        await self.send_json({
            "type": "receive",
            "data": "over!"
        })

    async def newMessage(self, event):
        await self.send_json({
            "type": "newMessage",
            "data": event['data']
        })
