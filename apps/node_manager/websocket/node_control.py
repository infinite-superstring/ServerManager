import json
from datetime import datetime
from uuid import UUID

from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.tagUtil import get_node_tags
from apps.setting.entity import Config
from util.jsonEncoder import ComplexEncoder

from util.logger import Log


class node_control(AsyncWebsocketConsumer):
    __node_uuid: UUID = None
    __userID: int = None
    __clientIP: str = None
    __config: Config = None
    __node: Node = None
    __node_base_info: Node_BaseInfo = None

    async def connect(self):
        # 在建立连接时执行的操作
        self.__clientIP = self.scope["client"][0]
        if not self.scope['url_route']['kwargs']['node_uuid']:
            Log.debug("参数不完整")
            return self.disconnect(-1)
        self.__node_uuid = UUID(self.scope['url_route']['kwargs']['node_uuid'])
        if not await sync_to_async(Node.objects.filter(uuid=self.__node_uuid).exists)():
            Log.info(f"节点{self.__node_uuid}不存在")
            return self.disconnect(0)
        self.__node = await sync_to_async(Node.objects.get)(uuid=self.__node_uuid)
        # 加入组
        await self.channel_layer.group_add(
            f"NodeControl_{self.__node.uuid}",
            self.channel_name
        )
        await self.accept()
        await self.__init_data()


    async def disconnect(self, close_code):
        if self.__node:
            # 离开组
            await self.channel_layer.group_discard(
                f"NodeControl_{self.__node.uuid}",
                self.channel_name
            )
        raise StopConsumer

    async def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        if text_data:
            try:
                json_data = await sync_to_async(json.loads)(text_data)
            except Exception as e:
                Log.error(f"解析Websocket消息时发生错误：\n{e}")
            else:
                pass

    @Log.catch
    async def send_json(self, data):
        await self.send(await sync_to_async(json.dumps)(data, cls=ComplexEncoder))

    @Log.catch
    async def __init_data(self):
        """初始化页面数据"""
        usage_data = None
        node_system_info = None
        if await sync_to_async(Node_BaseInfo.objects.filter(node=self.__node).exists)():
            self.__node_base_info = await sync_to_async(Node_BaseInfo.objects.get)(node=self.__node)
            node_system_info = {
                "hostname": self.__node_base_info.hostname,
                "system_type": self.__node_base_info.system,
                "system_version": self.__node_base_info.system_release,
                "system_build_version": self.__node_base_info.system_build_version,
                "system_boot_time": self.__node_base_info.boot_time,
                "cpu_architecture": self.__node_base_info.architecture,
                "memory_total": self.__node_base_info.memory_total,
                "swap_total": self.__node_base_info.swap_total,
                'core_count': self.__node_base_info.core_count,
                'processor_count': self.__node_base_info.processor_count,
            }
        if node_system_info and await sync_to_async(Node_UsageData.objects.filter(node=self.__node).exists)():
            usage_data: Node_UsageData = await sync_to_async(Node_UsageData.objects.filter(node=self.__node).last)()
            loadavg_data = await sync_to_async(lambda: usage_data.system_loadavg)()
            usage_data: dict = {
                "timestamp": usage_data.timestamp,
                'cpu_core': {f"CPU {core.core_index}": core.usage async for core in
                             await sync_to_async(usage_data.cpu_core_usage.all)()} if usage_data.cpu_core_usage else {},
                "cpu_usage": usage_data.cpu_usage,
                'memory': usage_data.memory_used,
                "memory_used": round((usage_data.memory_used / self.__node_base_info.memory_total) * 100, 1),
                'swap': usage_data.swap_used,
                'disk_io': {
                    'read': usage_data.disk_io_read_bytes,
                    'write': usage_data.disk_io_write_bytes,
                },
                'loadavg': {
                    "one_minute": loadavg_data.one_minute,
                    "five_minute": loadavg_data.five_minute,
                    "fifteen_minute": loadavg_data.fifteen_minute,
                }
            }
        await self.send_json({
            "action": "init",
            "data": {
                "base_info": {
                    "node_uuid": self.__node_uuid,
                    "node_name": self.__node.name,
                    "node_online": self.__node_base_info.online if self.__node_base_info else False,
                    "node_description": self.__node.description,
                    "node_tags": get_node_tags(self.__node),
                    "node_system_info": node_system_info,
                },
                "usage": usage_data if usage_data else None
            }
        })

    @Log.catch
    async def update_node_usage_data(self, event):
        """
        更新节点使用率数据
        """
        await self.send_json({
            'action': 'update_node_usage_data',
            'data': event['usage_data']
        })

    @Log.catch
    async def node_online(self, event):
        """节点上线"""
        await self.send_json({'action': 'node_online'})
        await self.__init_data()

    @Log.catch
    async def node_offline(self, event):
        """节点离线"""
        await self.send_json({'action': 'node_offline'})
