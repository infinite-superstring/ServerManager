import json
from datetime import datetime

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.signals import *
from apps.node_manager.utils.nodeUtil import update_disk_partition
from apps.setting.entity import Config
from util.calculate import calculate_percentage

from util.logger import Log


class node_client(WebsocketConsumer):
    __auth: bool = False
    __config: Config
    __node_uuid: str
    __node: Node
    __node_base_info: Node_BaseInfo

    def connect(self):
        # 在建立连接时执行的操作
        self.__node_uuid = self.scope["session"].get("node_uuid")
        node_name = self.scope["session"].get("node_name")
        if (self.__node_uuid or node_name) is None:
            Log.error("Node uuid or node name is empty")
            return self.close(-1)
        node = Node.objects.filter(uuid=self.__node_uuid, name=node_name)
        if not node.exists():
            Log.warning(f"Node {node_name} does not exist")
            return self.close(-1)

        node = node.first()
        self.__node = node
        self.__config = apps.get_app_config('setting').get_config()
        self.__node_base_info = Node_BaseInfo.objects.get(node=node)
        self.__node_base_info.online = True
        self.__node_base_info.save()
        self.accept()
        self.__auth = True
        self.send_json({
            'action': 'init_node_config',
            'data': {
                'heartbeat_time': self.__config.node.heartbeat_time,
                'upload_data_interval': self.__config.node.upload_data_interval,
            }
        })
        Log.success(f"节点：{node_name}已连接")
        node_online_signal.send(sender=self.__node_uuid)

    def disconnect(self, close_code):
        if self.__auth:
            # 在断开连接时执行的操作
            node_name = self.scope["session"].get("node_name")
            self.__node_base_info.online = False
            self.__node_base_info.save()
            Log.success(f"节点：{node_name}已断开({close_code})")
            node_offline_signal.send(sender=self.__node_uuid)
        raise StopConsumer

    def receive(self, text_data=None, bytes_data=None):
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
                        core_usage = [Node_UsageData.CpuCoreUsage.objects.create(core_index=index, usage=data) for
                                      index, data in enumerate(cpu_data["core_usage"])]
                        loadavg = Node_UsageData.Loadavg.objects.create(one_minute=loadavg_data[0], five_minute=loadavg_data[1], fifteen_minute=loadavg_data[2])
                        usage_data = Node_UsageData.objects.create(
                            node=self.__node,
                            cpu_usage=cpu_data['usage'],
                            memory_used=memory_data['used'],
                            swap_used=swap_data['used'],
                            disk_io_read_bytes=disk_data['io']['read_bytes'],
                            disk_io_write_bytes=disk_data['io']['write_bytes'],
                            system_loadavg=loadavg
                        )
                        for core_usage_item in core_usage:
                            usage_data.cpu_core_usage.add(core_usage_item)
                        usage_data.save()
                        flag = False
                        if self.__node_base_info.memory_total != memory_data['total']:
                            flag = True
                            self.__node_base_info.memory_total = memory_data['total']
                        if self.__node_base_info.swap_total != swap_data['total']:
                            flag = True
                            self.__node_base_info.swap_total = swap_data['total']
                        if flag:
                            self.__node_base_info.save()
                        update_disk_partition(self.__node, disk_data['partition_list'])
                        usage_data = {
                            "timestamp": usage_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'cpu_core': {f'CPU {index}' : data for index, data in enumerate(cpu_data["core_usage"])},
                            "cpu_usage": cpu_data['usage'],
                            'memory': memory_data['used'],
                            "memory_used": calculate_percentage(memory_data['used'], self.__node_base_info.memory_total),
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
                        node_usage_update_signal.send(sender=self.__node.uuid, usage_data=usage_data)
                    case 'refresh_node_info':
                        self.__node_base_info.system = data['system']
                        self.__node_base_info.system_release = data['system_release']
                        self.__node_base_info.system_build_version = data['system_build_version']
                        self.__node_base_info.hostname = data['hostname']
                        self.__node_base_info.boot_time = data['boot_time']
                        self.__node_base_info.architecture = data['cpu']['architecture']
                        self.__node_base_info.core_count = data['cpu']['core']
                        self.__node_base_info.processor_count = data['cpu']['processor']
                        disks = data['disks']  # 客户端发送的磁盘数据
                        update_disk_partition(self.__node, disks)
                        self.__node_base_info.save()
                    case 'ping':
                        pass
                    case _:
                        Log.warning(f'Unknown action:{action}')

    @Log.catch
    def send_json(self, data):
        self.send(json.dumps(data))
