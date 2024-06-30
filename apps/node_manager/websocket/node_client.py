import asyncio
import json
import threading
import time
import uuid
from uuid import UUID
from datetime import datetime
from threading import Thread

from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from consumers.AsyncConsumer import AsyncBaseConsumer
from django.apps import apps
from django.core.cache import cache

from apps.audit.util.auditTools import write_node_session_log
from apps.node_manager.entity.alarm_setting import AlarmSetting
from apps.node_manager.models import Node, Node_BaseInfo, Node_AlarmSetting
from apps.node_manager.utils.nodeUtil import update_disk_partition, refresh_node_info, save_node_usage_to_database, \
    a_load_node_alarm_setting
from apps.message.models import MessageBody
from apps.message.api.message import send_email
from apps.setting.entity import Config
from apps.node_manager.utils.nodeEventUtil import NodeEventUtil, createEvent, createPhase, stopEvent
from util.calculate import calculate_percentage
from util.dictUtils import get_key_by_value
from util.format import format_bytes
from util.logger import Log


class node_client(AsyncBaseConsumer):
    __auth: bool = False
    __alarm: bool = False
    __alarm_setting: AlarmSetting
    __alarm_status: dict
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
        await self.__load_alarm_setting()
        clientIP = self.scope['client'][0]
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, write_node_session_log, self.__node.uuid, 0, clientIP)
        threading.Thread(target=self.__check_node_timeout, args=()).start()
        await createEvent(node, "节点已连接", "", end_directly=True)
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
            clientIP = self.scope['client'][0]
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, write_node_session_log, self.__node.uuid, 1, clientIP)
            await self.__node_offline()
            await createEvent(self.__node, "节点已断开", "", end_directly=True)
            Log.success(f"节点：{node_name}已断开({close_code})")
        raise StopConsumer

    async def receive(self, *args, **kwargs):
        await self.__update_cache_timeout()
        await super().receive(*args, **kwargs)

    @Log.catch
    async def connect_terminal(self, event):
        index = uuid.uuid1()
        sender = event['sender']
        self.__init_tty_queue[index] = sender
        await self.send_json({
            'action': 'init_terminal',
            'data': {
                'index': index,
                'web_id':'127.0.0.1',
                'port':22,
                'username':'fsj',
                'password':'123456'
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
            self.__check_get_process_list_activity_thread = Thread(
                target=self.__check_get_process_list_activity,
                args=()
            )
            self.__check_get_process_list_activity_thread.start()
            self.__get_process_list = True

    @Log.catch
    async def kill_process(self, event):
        """结束进程"""
        Log.warning("kill_process")
        pid: int = event['pid']
        tree_mode = event['tree_mode']
        if pid:
            await self.send_json({
                'action': 'kill_process',
                'data': {
                    'pid': pid,
                    'tree_mode': tree_mode
                }
            })

    @Log.catch
    async def reload_alarm_setting(self, event):
        Log.info("重新加载告警设置......")
        try:
            if self.__alarm_status['cpu']['event'] is not None: await stopEvent(self.__alarm_status['cpu']['event'])
            if self.__alarm_status['memory']['event'] is not None: await stopEvent(self.__alarm_status['memory']['event'])
            if self.__alarm_status['network']['send']['event'] is not None: await stopEvent(self.__alarm_status['network']['send']['event'])
            if self.__alarm_status['network']['recv']['event'] is not None: await stopEvent(self.__alarm_status['network']['recv']['event'])
            for i in self.__alarm_status['disk']:
                if i['event'] is not None: await stopEvent(i['event'])
        except Exception as e:
            Log.error(e)
        await self.__load_alarm_setting()

    @Log.catch
    @AsyncBaseConsumer.action_handler("refresh_node_info")
    async def __refresh_node_info(self, payload=None):
        """刷新节点信息"""
        self.__node_base_info.system = payload['system']
        self.__node_base_info.system_release = payload['system_release']
        self.__node_base_info.system_build_version = payload['system_build_version']
        self.__node_base_info.hostname = payload['hostname']
        self.__node_base_info.boot_time = payload['boot_time']
        self.__node_base_info.architecture = payload['cpu']['architecture']
        self.__node_base_info.core_count = payload['cpu']['core']
        self.__node_base_info.processor_count = payload['cpu']['processor']
        self.__node_base_info.memory_total = payload['memory_total']
        await update_disk_partition(self.__node, payload['disks'])
        await self.__node_base_info.asave()
        self.__node_base_info = self.__node_base_info

    @AsyncBaseConsumer.action_handler("upload_running_data")
    async def __save_running_data(self, payload=None):
        """上传节点数据"""
        cpu_data = payload.get('cpu')
        memory_data = payload.get('memory')
        swap_data = payload.get('swap')
        disk_data = payload.get('disk')
        network_data = payload.get('network')
        loadavg_data = payload.get('loadavg')
        await refresh_node_info(self.__node, payload)
        await update_disk_partition(self.__node, disk_data['partition_list'])
        await self.__handle_alarm_event(payload)
        cache_key: str = f"node_{self.__node.uuid}_usage_last_update_time"
        # 检查存储粒度
        if cache.get(cache_key) is None:
            cache.add(
                cache_key,
                datetime.now().timestamp(),
                timeout=self.__config.node_usage.data_save_interval * 60
            )
            await save_node_usage_to_database(self.__node, payload)
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
    @AsyncBaseConsumer.action_handler("upload_node_msg")
    async def __upload_node_msg(self, payload):
        type = payload.get('type')
        desc = payload.get('desc')
        level = payload.get('level', "Info")
        await createEvent(self.__node, type, desc, level, end_directly=True)

    @Log.catch
    @AsyncBaseConsumer.action_handler("create_terminal_session")
    async def __create_terminal_session(self, payload=None):
        index = UUID(payload['index'])
        sid = payload['uuid']
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

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal_output")
    async def __handle_terminal_output(self, payload=None):
        """终端内容输出"""
        channel = get_key_by_value(self.__tty_uuid, payload['uuid'], True)
        if channel:
            await self.channel_layer.send(channel, {
                'type': "terminal_output",
                'output': payload['output']
            })

    @Log.catch
    @AsyncBaseConsumer.action_handler("ping")
    async def __handle_ping(self):
        await self.send_json({
            'action': 'pong',
        })

    @Log.catch
    async def __update_node_usage_update(self, usage_data):
        """更新节点使用率数据"""
        cache.set(f"NodeUsageData_{self.__node.uuid}", usage_data,
                  timeout=self.__config.node_usage.upload_data_interval + 3)
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
        await self.__update_cache_timeout()
        """节点上线"""
        await self.channel_layer.group_send(f"NodeControl_{self.__node.uuid}", {
            'type': 'node_online',
        })

    @Log.catch
    async def __update_cache_timeout(self):
        # 更新缓存超时时间
        cache.set(
            f"node_client_online_{self.__node.uuid}",
            self.channel_name,
            timeout=self.__config.node.timeout / 1000
        )

    @Log.catch
    @AsyncBaseConsumer.action_handler("process_list")
    async def __process_list(self, data):
        cache.set(f"node_{self.__node_uuid}_process_list", data, 5)
        await self.channel_layer.group_send(f"NodeControl_{self.__node_uuid}", {
            'type': 'show_process_list',
            'process_list': data
        })

    @Log.catch
    async def __load_alarm_setting(self):
        setting = await Node_AlarmSetting.objects.filter(node=self.__node).afirst()
        if setting and setting.enable:
            Log.debug(f"节点{self.__node.name}已启用告警")
            self.__alarm = True
            self.__alarm_status = {
                'cpu': {
                    'alerted': False,
                    'event_start_time': None,
                    'event_end_time': None,
                    'event': None
                },
                'memory': {
                    'alerted': False,
                    'event_start_time': None,
                    'event_end_time': None,
                    'event': None
                },
                'network': {
                    'send': {
                        'alerted': False,
                        'event_start_time': None,
                        'event_end_time': None,
                        'event': None
                    },
                    'recv': {
                        'alerted': False,
                        'event_start_time': None,
                        'event_end_time': None,
                        'event': None
                    }
                },
                'disk': {}
            }
            self.__alarm_setting = await a_load_node_alarm_setting(self.__node)
        else:
            self.__alarm = False

    @Log.catch
    async def __handle_alarm_event(self, data):
        """处理告警事件"""
        if not self.__alarm:
            return
        cpu_data = data.get('cpu')
        memory_data = data.get('memory')
        disk_data = data.get('disk')
        network_data = data.get('network')
        # 处理CPU告警
        if (
                self.__alarm_setting.cpu.is_enable() and
                self.__alarm_setting.cpu.threshold <= cpu_data.get('usage')
        ):
            if not self.__alarm_status['cpu']['event_start_time']:
                self.__alarm_status['cpu']['event_start_time'] = datetime.now().timestamp()
            await self.__general_send_alarm_event('cpu', cpu_data.get('usage'))
        else:
            if self.__alarm_status['cpu']['event_start_time']:
                self.__alarm_status['cpu']['event_end_time'] = datetime.now().timestamp()
                await self.__general_send_alarm_event('cpu', end=True)

        # 处理内存告警
        if (
                self.__alarm_setting.memory.is_enable() and
                self.__alarm_setting.memory.threshold <= calculate_percentage(
                    memory_data.get('used'),
                    self.__node_base_info.memory_total
                )
        ):
            if not self.__alarm_status['memory']['event_start_time']:
                self.__alarm_status['memory']['event_start_time'] = datetime.now().timestamp()
            await self.__general_send_alarm_event('memory', calculate_percentage(memory_data.get('used'),
                                                                                 self.__node_base_info.memory_total))
        else:
            if self.__alarm_status['memory']['event_start_time']:
                self.__alarm_status['memory']['event_end_time'] = datetime.now().timestamp()
                await self.__general_send_alarm_event('memory', end=True)
        # 处理发送流量告警
        if (
                self.__alarm_setting.network.is_enable() and
                self.__alarm_setting.network.send_threshold <= network_data['io']['_all']['bytes_sent']
        ):
            if not self.__alarm_status['network']['send']['event_start_time']:
                self.__alarm_status['network']['send']['event_start_time'] = datetime.now().timestamp()
            await self.__network_send_alarm_event('send', network_data['io']['_all']['bytes_sent'])
        else:
            if self.__alarm_status['network']['send']['event_start_time']:
                self.__alarm_status['network']['send']['event_start_time'] = datetime.now().timestamp()
                await self.__network_send_alarm_event('send', end=True)
        # 处理接收流量告警
        if (
                self.__alarm_setting.network.is_enable() and
                self.__alarm_setting.network.send_threshold <= network_data['io']['_all']['bytes_recv']
        ):
            if not self.__alarm_status['network']['recv']['event_start_time']:
                self.__alarm_status['network']['recv']['event_start_time'] = datetime.now().timestamp()
            await self.__network_send_alarm_event('recv', network_data['io']['_all']['bytes_recv'])
        else:
            if self.__alarm_status['network']['recv']['event_start_time']:
                self.__alarm_status['network']['recv']['event_start_time'] = datetime.now().timestamp()
                await self.__network_send_alarm_event('recv', end=True)
        # 处理磁盘告警
        for disk_rule in self.__alarm_setting.disk:
            if not disk_rule.is_enable:
                continue
            for disk in disk_data['partition_list']:
                if disk['device'] != disk_rule.device:
                    continue
                if disk_rule.threshold <= calculate_percentage(
                    disk['used'],
                    disk['total']
                ):
                    if not self.__alarm_status['disk'].get(disk_rule.device): self.__alarm_status['disk'][disk_rule.device] = {
                        'alerted': False,
                        'event_start_time': None,
                        'event_end_time': None,
                        'event': None
                    }
                    if not self.__alarm_status['disk'][disk_rule.device]['event_start_time']:
                        self.__alarm_status['disk'][disk_rule.device]['event_start_time'] = datetime.now().timestamp()
                    await self.__disk_send_alarm_event(disk_rule.device, calculate_percentage(disk['used'], disk['total']))
                else:
                    if self.__alarm_status['disk'].get(disk_rule.device) and self.__alarm_status['disk'][disk_rule.device]['event_start_time']:
                        self.__alarm_status['disk'][disk_rule.device]['event_end_time'] = datetime.now().timestamp()
                    await self.__disk_send_alarm_event(disk_rule.device, calculate_percentage(disk['used'], disk['total']), end=True)

    @Log.catch
    async def __general_send_alarm_event(self, device, value: int = 0, end: bool = False):
        """
        通用发送告警事件
        :param device: 设备
        :param value: 告警值
        :param end: 结束告警事件
        """
        device_name_mapping = {
            "cpu": "cpu",
            "memory": "内存",
        }

        node_group = await sync_to_async(lambda: self.__node.group)()
        # 处理开始告警消息
        if (
                (self.__alarm_status[device][
                     'event_start_time'] + self.__alarm_setting.delay_seconds < datetime.now().timestamp()) and
                # 验证结束时间
                (self.__alarm_status[device]['event_end_time'] is None or self.__alarm_status[device][
                    'event_end_time'] + self.__alarm_setting.interval < datetime.now().timestamp())
        ):
            if not self.__alarm_status[device]['event']:
                self.__alarm_status[device]['event'] = await createEvent(
                    self.__node,
                    f"{device_name_mapping.get(device, device)}占用率超过告警阈值",
                    f"告警值{value}%",
                    "Warning"
                )
            else:
                await createPhase(
                    self.__alarm_status[device]['event'],
                    "占用率",
                    f"{value}%"
                )

            if node_group and not self.__alarm_status[device]['alerted']:
                Log.debug(f"发送告警开始消息：{device}")
                start_time = datetime.fromtimestamp(self.__alarm_status[device]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
                await sync_to_async(send_email)(MessageBody(
                    title=f"节点：{self.__node.name}告警触发！",
                    content=f"节点：{self.__node.name}<br>事件：{device_name_mapping.get(device, device)}占用率已达到设定阈值触发告警<br>触发时值: {value}%<br>触发时间: {start_time}",
                    node_groups=node_group
                ))
                self.__alarm_status[device]['alerted'] = True

        # 处理结束告警消息
        if self.__alarm_status[device]['event_start_time'] and end:
            if self.__alarm_status[device]['alerted']:
                # 关闭事件
                if self.__alarm_status[device]['event']:
                    await stopEvent(self.__alarm_status[device]['event'])
                Log.debug(f"发送告警结束消息：{device}")
                self.__alarm_status[device]['alerted'] = False
                if node_group:
                    start_time = datetime.fromtimestamp(self.__alarm_status[device]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
                    end_time = datetime.fromtimestamp(self.__alarm_status[device]['event_end_time']).strftime('%Y-%m-%d %H:%M:%S')
                    await sync_to_async(send_email)(MessageBody(
                        title=f"节点：{self.__node.name}告警结束！",
                        content=f"节点：{self.__node.name}<br>事件：{device_name_mapping.get(device, device)}占用率离开设定阈值触发告警区间<br>开始时间: {start_time}<br>结束时间: {end_time}",
                        node_groups=node_group
                    ))
                else:
                    Log.warning("未绑定节点组，无法发送消息")
            self.__alarm_status[device]['event_start_time'] = None

    @Log.catch
    async def __network_send_alarm_event(self, data_direction, value: int = 0, end: bool = False):
        """
        发送网络告警事件
        :param data_direction: 数据方向
        :param value: 告警值
        :param end: 结束告警事件
        """
        data_direction_mapping = {
            'send': '发送',
            'recv': '接收'
        }
        node_group = await sync_to_async(lambda: self.__node.group)()
        if data_direction not in data_direction_mapping.keys():
            raise RuntimeError(f"Invalid data direction {data_direction}")
        # 处理开始告警消息
        if (
                (self.__alarm_status['network'][data_direction]['event_start_time'] + self.__alarm_setting.delay_seconds < datetime.now().timestamp()) and
                # 验证结束时间
                (self.__alarm_status['network'][data_direction]['event_end_time'] is None or
                 self.__alarm_status['network'][data_direction]['event_end_time'] + self.__alarm_setting.interval < datetime.now().timestamp())
        ):
            if not self.__alarm_status['network'][data_direction]['event']:
                self.__alarm_status['network'][data_direction]['event'] = await createEvent(
                    self.__node,
                    f"{data_direction_mapping.get(data_direction)}数据量超过告警阈值",
                    f"告警值{format_bytes(value)}",
                    "Warning"
                )
            else:
                await createPhase(
                    self.__alarm_status['network'][data_direction]['event'],
                    f"{data_direction_mapping.get(data_direction)}已超过阈值",
                    format_bytes(value)
                )
            if node_group and not self.__alarm_status['network'][data_direction]['alerted']:
                Log.debug(f"发送告警开始消息: {data_direction}")
                start_time = datetime.fromtimestamp(self.__alarm_status['network'][data_direction]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
                await sync_to_async(send_email)(MessageBody(
                    title=f"节点：{self.__node.name}告警触发！",
                    content=f"节点：{self.__node.name}<br>事件：{data_direction_mapping.get(data_direction)}已达到设定阈值触发告警<br>触发时值: {format_bytes(value)}<br>触发时间: {start_time}",
                    node_groups=node_group
                ))
                self.__alarm_status['network'][data_direction]['alerted'] = True

            # 处理结束告警消息
            if self.__alarm_status['network'][data_direction]['event_start_time'] and end:
                if self.__alarm_status['network'][data_direction]['alerted']:
                    # 关闭事件
                    if self.__alarm_status['network'][data_direction]['event']:
                        await stopEvent(self.__alarm_status['network'][data_direction]['event'])
                    self.__alarm_status['network'][data_direction]['alerted'] = False
                    # 发送告警结束信息
                    if node_group:
                        Log.debug(f"发送告警结束消息: {data_direction}")
                        start_time = datetime.fromtimestamp(self.__alarm_status['network'][data_direction]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = datetime.fromtimestamp(self.__alarm_status['network'][data_direction]['event_end_time']).strftime('%Y-%m-%d %H:%M:%S')
                        await sync_to_async(send_email)(MessageBody(
                            title=f"节点：{self.__node.name}告警结束！",
                            content=f"节点：{self.__node.name}<br>事件：{data_direction_mapping.get(data_direction)}离开设定阈值触发告警区间<br>开始时间: {start_time}<br>结束时间: {end_time}",
                            node_groups=node_group
                        ))
                    else:
                        Log.warning("未绑定节点组，无法发送消息")
                self.__alarm_status['network'][data_direction]['event_end_time'] = None

    @Log.catch
    async def __disk_send_alarm_event(self, disk, value: int = 0, end: bool = False):
        """
        发送磁盘空间告警事件
        :param disk: 磁盘设备
        :param value: 告警值
        :param end: 结束告警事件
        """
        node_group = await sync_to_async(lambda: self.__node.group)()
        if disk not in self.__alarm_status['disk'].keys():
            raise RuntimeError(f"Nonexistent disk configuration: {disk}")
        # 处理开始告警消息
        if (
                (self.__alarm_status['disk'][disk][
                     'event_start_time'] + self.__alarm_setting.delay_seconds < datetime.now().timestamp()) and
                # 验证结束时间
                (self.__alarm_status['disk'][disk]['event_end_time'] is None or
                 self.__alarm_status['disk'][disk][
                     'event_end_time'] + self.__alarm_setting.interval < datetime.now().timestamp())
        ):
            if not self.__alarm_status['disk'][disk]['event']:
                self.__alarm_status['disk'][disk]['event'] = await createEvent(
                    self.__node,
                    f"{disk}磁盘使用量超过告警阈值",
                    f"当前值：{value}%",
                    "Warning"
                )
            if node_group and not self.__alarm_status['disk'][disk]['alerted']:
                Log.debug(f"发送告警开始消息: disk：{disk}")
                start_time = datetime.fromtimestamp(
                    self.__alarm_status['disk'][disk]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
                await sync_to_async(send_email)(MessageBody(
                    title=f"节点：{self.__node.name}告警触发！",
                    content=f"节点：{self.__node.name}<br>事件：{disk}使用率已达到设定阈值触发告警<br>触发时: {value}%<br>触发时间: {start_time}",
                    node_groups=node_group
                ))
                self.__alarm_status['disk'][disk]['alerted'] = True

            # 处理结束告警消息
            if self.__alarm_status['disk'][disk]['event_start_time'] and end:
                if self.__alarm_status['disk'][disk]['alerted']:
                    # 关闭事件
                    if self.__alarm_status['disk'][disk]['event']:
                        await stopEvent(self.__alarm_status['disk'][disk]['event'])
                    self.__alarm_status['disk'][disk]['alerted'] = False
                    # 发送告警结束信息
                    if node_group:
                        Log.debug(f"发送告警结束消息: disk：{disk}")
                        start_time = datetime.fromtimestamp(
                            self.__alarm_status['disk'][disk]['event_start_time']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        end_time = datetime.fromtimestamp(
                            self.__alarm_status['disk'][disk]['event_end_time']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        await sync_to_async(send_email)(MessageBody(
                            title=f"节点：{self.__node.name}告警结束！",
                            content=f"节点：{self.__node.name}<br>事件：{disk}使用率离开设定阈值触发告警区间<br>开始时间: {start_time}<br>结束时间: {end_time}",
                            node_groups=node_group
                        ))
                    else:
                        Log.warning("未绑定节点组，无法发送消息")
                self.__alarm_status['disk'][disk]['event_end_time'] = None

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

    @Log.catch
    def __check_node_timeout(self):
        """线程：检查节点是否超时"""
        while cache.get(f"node_client_online_{self.__node.uuid}", False) == self.channel_name:
            time.sleep(1)
        asyncio.run(self.close(3500))
