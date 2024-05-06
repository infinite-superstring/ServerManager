import json
import uuid

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps

from node_manager.models import Node, Node_BaseInfo
from setting.entity import Config

from util.logger import Log

links = {}


class node_client(WebsocketConsumer):
    __auth: bool = False
    __config: Config
    __node_base_info: Node_BaseInfo

    def connect(self):
        # 在建立连接时执行的操作
        node_uuid = self.scope["session"].get("node_uuid")
        node_name = self.scope["session"].get("node_name")
        print(node_uuid, node_name)
        if (node_uuid or node_name) is None:
            Log.error("Node uuid or node name is empty")
            return self.close(-1)
        node = Node.objects.filter(uuid=node_uuid, name=node_name)
        if not node.exists():
            Log.warning(f"Node {node_name} does not exist")
            return self.close(-1)

        node = node.first()
        self.__config = apps.get_app_config('setting').get_config()
        self.__node_base_info = Node_BaseInfo.objects.get(node=node)
        self.__node_base_info.online = True
        self.accept()
        self.__auth = True
        self.send_json({
            'action': 'init_node_config',
            'data': {
                'heartbeat_time': self.__config.node.heartbeat_time,
                'upload_data_interval': self.__config.node.upload_data_interval,
            }
        })
        links.update({node_uuid: self})
        Log.success(f"节点：{node_name}已连接")

    def disconnect(self, close_code):
        if self.__auth:
            # 在断开连接时执行的操作
            node_uuid = self.scope["session"].get("node_uuid")
            node_name = self.scope["session"].get("node_name")
            self.__node_base_info.online = False
            self.__node_base_info.save()
            links.pop(node_uuid)
            Log.success(f"节点：{node_name}已断开({close_code})")
        raise StopConsumer

    def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        if text_data:
            try:
                json_data = json.loads(text_data)
            except Exception as e:
                print(f"解析Websocket消息时发生错误：\n{e}")
            else:
                action = json_data.get('action')
                data = json_data.get('data')
                match action:
                    case 'upload_running_data':
                        print(data)
                    case 'refresh_node_info':
                        print(data)
                    case 'ping':
                        pass
                    case _:
                        Log.warning(f'Unknown action:{action}')

    @Log.catch
    def send_json(self, data):
        self.send(json.dumps(data))
