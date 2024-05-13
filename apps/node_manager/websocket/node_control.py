import json
from uuid import UUID

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.tagUtil import get_node_tags
from apps.setting.entity import Config
from util.jsonEncoder import ComplexEncoder

from util.logger import Log

links = {}


class node_control(WebsocketConsumer):
    __node_uuid: UUID = None
    __userID: int = None
    __clientIP: str = None
    __config: Config
    __node: Node
    __node_base_info: Node_BaseInfo

    def connect(self):
        # 在建立连接时执行的操作
        user = self.scope["session"].get("user")
        self.__userID = self.scope["session"].get("userID")
        self.__clientIP = self.scope["client"][0]
        if not (user and self.__userID and self.scope['url_route']['kwargs']['node_uuid']):
            Log.debug("未登录或参数不完整")
            return self.disconnect(-1)
        self.__node_uuid = UUID(self.scope['url_route']['kwargs']['node_uuid'])
        if not Node.objects .filter(uuid=self.__node_uuid).exists():
            Log.info("节点不存在")
            return self.disconnect(0)
        self.__node = Node.objects.get(uuid=self.__node_uuid)
        self.__node_base_info = Node_BaseInfo.objects.get(node=self.__node)
        self.accept()
        self.send_json({
            "action": "init",
            "data": {
                "node_uuid": self.__node_uuid,
                "node_name": self.__node.name,
                "node_description": self.__node.description,
                "node_tags": get_node_tags(self.__node),
                "node_hostname": self.__node_base_info.hostname,
                "node_system_type": self.__node_base_info.system,
                "node_system_version": self.__node_base_info.system_release,
                "node_system_build_version": self.__node_base_info.system_build_version,
                "node_system_boot_time": str(self.__node_base_info.boot_time),
                "node_memory_total": self.__node_base_info.memory_total,
                "node_swap_total": self.__node_base_info.swap_total,
            }
        })

    def disconnect(self, close_code):
        raise StopConsumer

    def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        if text_data:
            try:
                json_data = json.loads(text_data)
            except Exception as e:
                print(f"解析Websocket消息时发生错误：\n{e}")
            else:
                pass

    @Log.catch
    def send_json(self, data):
        self.send(json.dumps(data, cls=ComplexEncoder))
