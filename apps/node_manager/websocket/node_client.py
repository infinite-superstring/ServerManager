import json
import uuid
from uuid import UUID
from datetime import datetime

from asgiref.sync import sync_to_async
from cffi.backend_ctypes import unicode
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.core.cache import cache

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.nodeUtil import update_disk_partition, refresh_node_info, save_node_usage_to_database
from apps.setting.entity import Config
from util.calculate import calculate_percentage
from util.dictUtils import get_key_by_value
from util.jsonEncoder import ComplexEncoder

from util.logger import Log


class node_client(AsyncWebsocketConsumer):
    __auth: bool = False
    __config: Config
    __node_uuid: str
    __node: Node
    __node_base_info: Node_BaseInfo
    __init_tty_queue: dict[str:str] = {}
    __tty_uuid: dict[str:str] = {}

    async def connect(self):
        # 在建立连接时执行的操作
        self.__node_uuid = self.scope["session"].get("node_uuid")
        node_name = self.scope["session"].get("node_name")
        if (self.__node_uuid or node_name) is None:
            Log.error("Node uuid or node name is empty")
            return self.close(-1)
        if not Node.objects.filter(uuid=self.__node_uuid, name=node_name).aexists():
            Log.warning(f"Node {node_name} does not exist")
            return self.close(-1)

        node = await Node.objects.filter(uuid=self.__node_uuid, name=node_name).afirst()
        self.__node = node
        self.__config = apps.get_app_config('setting').get_config()
        self.__node_base_info = await Node_BaseInfo.objects.aget(node=node)
        self.__node_base_info.online = True
        await self.__node_base_info.asave()
        await self.accept()
        self.__auth = True
        # 加入组
        await self.channel_layer.group_add(
            f"NodeClient_{self.__node.uuid}",
            self.channel_name
        )
        await self.send_json({
            'action': 'init_node_config',
            'data': {
                'heartbeat_time': self.__config.node.heartbeat_time,
                'upload_data_interval': self.__config.node_usage.upload_data_interval,
            }
        })
        await self.__node_online()
        Log.success(f"节点：{node_name}已连接")

    async def disconnect(self, close_code):
        if self.__auth:
            # 在断开连接时执行的操作
            node_name = self.scope["session"].get("node_name")
            self.__node_base_info.online = False
            await self.__node_base_info.asave()
            await self.channel_layer.group_discard(
                f"NodeClient_{self.__node.uuid}",
                self.channel_name
            )
            cache.delete(f"node_{self.__node.uuid}_usage_last_update_time")
            await self.__node_offline()
            Log.success(f"节点：{node_name}已断开({close_code})")
        raise StopConsumer

    async def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        if text_data:
            try:
                json_data = json.loads(text_data)
            except Exception as e:
                Log.error(f"解析Websocket消息时发生错误：\n{e}")
            else:
                action = json_data.get('action')
                data = json_data.get('data')
                cpu_data = data.get('cpu')
                memory_data = data.get('memory')
                swap_data = data.get('swap')
                disk_data = data.get('disk')
                loadavg_data = data.get('loadavg')
                match action:
                    case 'upload_running_data':
                        """上传节点数据"""
                        sync_to_async(refresh_node_info)(self.__node, data)
                        sync_to_async(update_disk_partition)(self.__node, disk_data['partition_list'])
                        cache_key: str = f"node_{self.__node.uuid}_usage_last_update_time"
                        # 检查存储粒度
                        if cache.get(cache_key) is None:
                            cache.add(cache_key, datetime.now().timestamp(),
                                      timeout=self.__config.node_usage.data_save_interval * 60)
                            sync_to_async(save_node_usage_to_database)(self.__node, data)
                        usage_data = {
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'cpu_core': {f'CPU {index}': data for index, data in enumerate(cpu_data["core_usage"])},
                            "cpu_usage": cpu_data['usage'],
                            'memory': memory_data['used'],
                            "memory_used": calculate_percentage(
                                memory_data['used'],
                                self.__node_base_info.memory_total
                            ),
                            'swap': swap_data['used'],
                            'disk_io': {
                                'read': disk_data['io']['read_bytes'],
                                'write': disk_data['io']['write_bytes'],
                            },
                            'loadavg': {
                                "one_minute": loadavg_data[0],
                                "five_minute": loadavg_data[1],
                                "fifteen_minute": loadavg_data[2],
                            }
                        }
                        await self.__update_node_usage_update(usage_data)

                    case 'refresh_node_info':
                        """刷新node信息"""
                        self.__node_base_info.system = data['system']
                        self.__node_base_info.system_release = data['system_release']
                        self.__node_base_info.system_build_version = data['system_build_version']
                        self.__node_base_info.hostname = data['hostname']
                        self.__node_base_info.boot_time = data['boot_time']
                        self.__node_base_info.architecture = data['cpu']['architecture']
                        self.__node_base_info.core_count = data['cpu']['core']
                        self.__node_base_info.processor_count = data['cpu']['processor']
                        disks = data['disks']  # 客户端发送的磁盘数据
                        sync_to_async(update_disk_partition)(self.__node, disks)
                        await self.__node_base_info.asave()

                    case 'create_terminal_session':
                        """创建tty会话返回"""
                        index = UUID(data['index'])
                        sid = data['uuid']
                        Log.debug(self.__init_tty_queue)
                        Log.debug(index)
                        if index not in self.__init_tty_queue.keys():
                            await self.send_json({
                                'action': 'close_terminal',
                                'data': {
                                    'uuid': sid
                                }
                            })
                        else:
                            self.__tty_uuid.update({self.__init_tty_queue[index]: sid})
                            self.__init_tty_queue.pop(index)

                    case "terminal_output":
                        """终端内容输出"""
                        uuid = data['uuid']
                        output = data['output']
                        channel = get_key_by_value(self.__tty_uuid, uuid, True)
                        if channel:
                            await self.channel_layer.send(channel, {
                                'type': "terminal_output",
                                'output': output
                            })

                    case 'ping':
                        pass
                    case _:
                        Log.warning(f'Unknown action:{action}')

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    @Log.catch
    async def connect_terminal(self, event):
        Log.debug("init terminal")
        index = uuid.uuid1()
        sender = event['sender']
        self.__init_tty_queue[index] = sender
        await self.send_json({
            'action': 'init_terminal',
            'data': {
                'index': index
            }
        })

    @Log.catch
    async def close_terminal(self, event):
        sender = event['sender']
        if sender in self.__init_tty_queue:
            await self.send_json({
                'action': 'close_terminal',
                'data': {
                    'uuid': self.__tty_uuid[sender]
                }
            })
            self.__init_tty_queue.pop(sender)
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def __update_node_usage_update(self, usage_data):
        """更新节点使用率数据"""
        await self.channel_layer.group_send(f"NodeControl_{self.__node.uuid}", {
            'type': 'update_node_usage_data',
            'usage_data': usage_data
        })

    @Log.catch
    async def __node_offline(self):
        """节点离线"""
        await self.channel_layer.group_send(f"NodeControl_{self.__node.uuid}", {
            'type': 'node_offline',
        })

    @Log.catch
    async def __node_online(self):
        """节点上线"""
        await self.channel_layer.group_send(f"NodeControl_{self.__node.uuid}", {
            'type': 'node_online',
        })