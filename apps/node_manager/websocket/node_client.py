import asyncio
import json
import time
import uuid
from uuid import UUID
from datetime import datetime
from threading import Thread

from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.core.cache import cache

from apps.audit.util.auditTools import write_node_session_log
from apps.node_manager.models import Node, Node_BaseInfo
from apps.node_manager.utils.nodeUtil import update_disk_partition, refresh_node_info, save_node_usage_to_database
from apps.setting.entity import Config
from util.calculate import calculate_percentage
from util.dictUtils import get_key_by_value
from util.jsonEncoder import ComplexEncoder

from util.logger import Log


class node_client(AsyncWebsocketConsumer):
    __auth: bool = False
    __get_process_list: bool = False
    __check_get_process_list_activity_thread: Thread
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
        if not (self.scope["session"]["node_uuid"] or self.scope["session"]["node_name"]):
            Log.warning("node未认证")
            return await self.close(-1)
        if (self.__node_uuid or node_name) is None:
            Log.error("Node uuid or node name is empty")
            return await self.close(-1)
        if not Node.objects.filter(uuid=self.__node_uuid, name=node_name).aexists():
            Log.warning(f"Node {node_name} does not exist")
            return await self.close(-1)
        node = await Node.objects.filter(uuid=self.__node_uuid, name=node_name).afirst()
        self.__config = apps.get_app_config('setting').get_config()
        if cache.get(f"node_client_online_{self.__node_uuid}") is not None:
            Log.warning(f"Node {node.name} has been online, unable to connect")
            return await self.close(1000)
        cache.add(f"NodeClient_{self.__node_uuid}", self.channel_name, timeout=self.__config.node.timeout)
        self.__node = node
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

        clientIP = self.scope['client'][0]
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, write_node_session_log, self.__node.uuid, "上线", clientIP)
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
            cache.delete(f"node_client_online_{self.__node.uuid}")
            await self.__node_offline()
            clientIP = self.scope['client'][0]
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, write_node_session_log, self.__node.uuid, "上线", clientIP)
            Log.success(f"节点：{node_name}已断开({close_code})")
        raise StopConsumer

    @Log.catch
    async def receive(self, text_data=None, bytes_data=None):
        await self.__update_cache_timeout()
        # 处理接收到的消息
        if text_data:
            try:
                json_data = json.loads(text_data)
            except Exception as e:
                Log.error(f"解析Websocket消息时发生错误：\n{e}")
                return
            action = json_data.get('action')
            print(action)
            data = json_data.get('data')
            match action:
                case 'upload_running_data':
                    await self.__save_running_data(data)
                case 'refresh_node_info':
                    await self.__refresh_node_info(data)
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
                    channel = get_key_by_value(self.__tty_uuid, data['uuid'], True)
                    if channel:
                        await self.channel_layer.send(channel, {
                            'type': "terminal_output",
                            'output': data['output']
                        })
                case "process_list":
                    await self.__process_list(data)
                case 'ping':
                    pass
                case _:
                    Log.warning(f'Unknown action:{action}')

    @Log.catch
    async def send_json(self, data):
        await self.send(json.dumps(data, cls=ComplexEncoder))

    @Log.catch
    async def connect_terminal(self, event):
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
        if sender in self.__tty_uuid:
            await self.send_json({
                'action': 'close_terminal',
                'data': {
                    'uuid': self.__tty_uuid[sender]
                }
            })
            self.__tty_uuid.pop(sender)
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def input_command(self, event):
        sender = event['sender']
        command = event['command']
        if sender in self.__tty_uuid:
            await self.send_json({
                'action': 'input_command',
                'data': {
                    'command': command,
                    'uuid': self.__tty_uuid[sender]
                }
            })
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def start_get_process_list(self, event):
        """开始获取进程列表"""
        Log.debug("用户请求获取进程列表")
        if self.__get_process_list is False:
            await self.send_json({
                'action': 'start_get_process_list',
            })
            # 启动检查线程
            self.__check_get_process_list_activity_thread = Thread(target=self.__check_get_process_list_activity, args=())
            self.__check_get_process_list_activity_thread.start()
            self.__get_process_list = True

    @Log.catch
    async def __refresh_node_info(self, data):
        """刷新节点信息"""
        self.__node_base_info.system = data['system']
        self.__node_base_info.system_release = data['system_release']
        self.__node_base_info.system_build_version = data['system_build_version']
        self.__node_base_info.hostname = data['hostname']
        self.__node_base_info.boot_time = data['boot_time']
        self.__node_base_info.architecture = data['cpu']['architecture']
        self.__node_base_info.core_count = data['cpu']['core']
        self.__node_base_info.processor_count = data['cpu']['processor']
        await update_disk_partition(self.__node, data['disks'])
        await self.__node_base_info.asave()

    async def __save_running_data(self, data):
        """上传节点数据"""
        cpu_data = data.get('cpu')
        memory_data = data.get('memory')
        swap_data = data.get('swap')
        disk_data = data.get('disk')
        network_data = data.get('network')
        loadavg_data = data.get('loadavg')
        await refresh_node_info(self.__node, data)
        await update_disk_partition(self.__node, disk_data['partition_list'])
        cache_key: str = f"node_{self.__node.uuid}_usage_last_update_time"
        # 检查存储粒度
        if cache.get(cache_key) is None:
            cache.add(
                cache_key,
                datetime.now().timestamp(),
                timeout=self.__config.node_usage.data_save_interval * 60
            )
            await save_node_usage_to_database(self.__node, data)
        await self.__update_node_usage_update({
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
            'disk_space': disk_data['partition_list'],
            "network_io": network_data['io'],
            'loadavg': {
                "one_minute": loadavg_data[0],
                "five_minute": loadavg_data[1],
                "fifteen_minute": loadavg_data[2],
            }
        })

    @Log.catch
    async def __update_node_usage_update(self, usage_data):
        """更新节点使用率数据"""
        cache.set(f"NodeUsageData_{self.__node.uuid}", usage_data, timeout=self.__config.node_usage.upload_data_interval+3)
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

    @Log.catch
    async def __update_cache_timeout(self):
        cache.set(f"node_client_online_{self.__node.uuid}", self.channel_name, timeout=self.__config.node.heartbeat_time)

    @Log.catch
    async def __process_list(self, data):
        cache.set(f"node_{self.__node_uuid}_process_list", data, 5)
        await self.channel_layer.group_send(f"NodeControl_{self.__node_uuid}", {
            'type': 'show_process_list',
            'process_list': data
        })

    @Log.catch
    def __check_get_process_list_activity(self):
        """线程: 检查获取进程列表活动"""
        Log.debug("开始检查[获取进程列表]活动状态")
        while cache.get(f"node_{self.__node_uuid}_get_process_list_activity", False):
            time.sleep(1)
        # 缓存被销毁时发出结束获取进程列表信号
        Log.debug("停止获取进程列表")
        self.__get_process_list = False
        asyncio.run(self.send_json({
            'action': 'stop_get_process_list',
        }))