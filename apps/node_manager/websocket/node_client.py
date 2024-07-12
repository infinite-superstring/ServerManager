import asyncio
import json
import os.path
import threading
import time
import uuid
from uuid import UUID
from datetime import datetime
from threading import Thread

from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from apps.group_task.api import group_task
from apps.group_task.utils.GroupTaskResultUtil import GroupTaskResultUtil
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
from apps.node_manager.utils.nodeEventUtil import createEvent, createPhase, stopEvent
from util.calculate import calculate_percentage
from util.dictUtils import get_key_by_value
from util.format import format_bytes
from util.logger import Log

save_dir_base = apps.get_app_config('node_manager').terminal_record_save_dir


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
    __node_terminal_record_dir: str
    __init_tty_queue: dict[str:str] = {}
    __tty_uuid: dict[str:str] = {}
    __terminal_record_fd: dict[str: any] = {}
    __task: dict = []
    __task_result_util: GroupTaskResultUtil = None

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
        self.__node_terminal_record_dir = os.path.join(save_dir_base, str(self.__node.uuid))
        # 加入组
        await self.channel_layer.group_add(
            f"NodeClient_{self.__node.uuid}",
            self.channel_name
        )
        self.__task = await group_task.by_node_uuid_get_task(node_uuid=self.__node_uuid)

        await self.send_json({
            'action': 'node:init_config',
            'data': {
                'heartbeat_time': self.__config.node.heartbeat_time,
                'upload_data_interval': self.__config.node_usage.upload_data_interval,
                'task': self.__task
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
        """节点断开连接时"""
        if self.__auth:
            node_name = self.scope["session"].get("node_name")
            self.scope["session"].clear()
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
        """处理节点收到信息时"""
        await self.__update_cache_timeout()
        await super().receive(*args, **kwargs)

    @Log.catch
    async def connect_terminal(self, event):
        """连接到终端"""
        index = uuid.uuid1()
        sender = event.get('sender')
        self.__init_tty_queue[index] = sender
        await self.send_action('terminal:create_session', {
            'index': index,
            'host': event.get('host'),
            'port': event.get('port'),
            'username': event.get('username'),
            'password': event.get('password')
        })

    @Log.catch
    async def close_terminal(self, event):
        """断开终端连接"""
        sender = event['sender']
        if sender in self.__tty_uuid:
            await self.send_action('terminal:close_session', {
                'uuid': self.__tty_uuid[sender]
            })
            self.__terminal_record_fd[self.__tty_uuid[sender]].close()
            self.__tty_uuid.pop(sender)
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def terminal_resize(self, event):
        """调整终端大小"""
        sender = event['sender']
        cols = event['cols']
        rows = event['rows']
        if sender in self.__tty_uuid:
            await self.send_action('terminal:resize', {
                'uuid': self.__tty_uuid[sender],
                'cols': cols,
                'rows': rows
            })
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def input_command(self, event):
        """输入终端命令"""
        sender = event['sender']
        command = event['command']
        if sender in self.__tty_uuid:
            await self.send_action('terminal:input', {
                'command': command,
                'uuid': self.__tty_uuid[sender]
            })
        else:
            Log.error(f"{sender} does not own a terminal session")

    @Log.catch
    async def start_get_process_list(self, event):
        """开始获取进程列表"""
        Log.debug("用户请求获取进程列表")
        if self.__get_process_list is False:
            await self.send_action('process_list:start')
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
            await self.send_action('process_list:kill', {
                'pid': pid,
                'tree_mode': tree_mode
            })

    @Log.catch
    async def reload_alarm_setting(self, event):
        Log.info("重新加载告警设置......")
        try:
            if self.__alarm_status['cpu']['event'] is not None: await stopEvent(self.__alarm_status['cpu']['event'])
            if self.__alarm_status['memory']['event'] is not None: await stopEvent(
                self.__alarm_status['memory']['event'])
            if self.__alarm_status['network']['send']['event'] is not None: await stopEvent(
                self.__alarm_status['network']['send']['event'])
            if self.__alarm_status['network']['recv']['event'] is not None: await stopEvent(
                self.__alarm_status['network']['recv']['event'])
            for i in self.__alarm_status['disk']:
                if i['event'] is not None: await stopEvent(i['event'])
        except Exception as e:
            Log.error(e)
        await self.__load_alarm_setting()

    @Log.catch
    async def group_task_change(self, data: dict[str:str | dict]):
        """
        节点任务状态改变
        """
        action = data.get('action', '')
        if not action:
            return
        Log.info(f"节点任务状态改变:{action}")
        await self.send_action(f'task:{action}', payload=data.get('data'))

    @Log.catch
    @AsyncBaseConsumer.action_handler("node:refresh_info")
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

    @AsyncBaseConsumer.action_handler("node:upload_running_data")
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
    @AsyncBaseConsumer.action_handler("node:upload_msg")
    async def __upload_node_msg(self, payload):
        """上传节点消息"""
        type = payload.get('type')
        desc = payload.get('desc')
        level = payload.get('level', "Info")
        await createEvent(self.__node, type, desc, level, end_directly=True)

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:return_session")
    async def __create_terminal_session(self, payload=None):
        """返回终端会话UUID"""
        index = UUID(payload['index'])
        sid = payload['uuid']
        Log.debug(self.__init_tty_queue)
        Log.debug(index)
        # 如果节点录制文件夹不存在则创建
        if not os.path.exists(self.__node_terminal_record_dir):
            os.mkdir(self.__node_terminal_record_dir)
        #  如果返回的是一个未知的index则销毁会话实例
        if index not in self.__init_tty_queue.keys():
            return await self.send_action('terminal:close_session', {
                'uuid': sid
            })
        self.__tty_uuid.update({self.__init_tty_queue[index]: sid})
        self.__init_tty_queue.pop(index)
        self.__terminal_record_fd[sid] = open(
            os.path.join(self.__node_terminal_record_dir, sid + ".txt"),
            "w+",
            encoding='utf-8'
        )
        # 发送节点就绪消息到控制端
        await self.__terminal_ready(sid)

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:login_failed")
    async def __handle_terminal_login_failed(self, payload=None):
        """终端登录错误时"""
        index = payload.get("index")
        Log.debug(self.__init_tty_queue)
        sender = self.__init_tty_queue.get(UUID(index))
        await self.channel_layer.send(sender, {
            'type': "terminal_login_failed",
            'session_id': index
        })
        Log.warning("终端登录错误，已关闭会话")

    @Log.catch
    async def __terminal_ready(self, sid):
        """终端就绪"""
        channel = get_key_by_value(self.__tty_uuid, sid, True)
        if channel:
            await self.channel_layer.send(channel, {
                'type': "terminal_ready",
                'session_id': sid
            })

    @Log.catch
    @AsyncBaseConsumer.action_handler("safe:Terminal_not_enabled")
    async def __terminal_not_enabled(self, payload=None):
        """节点禁用终端返回"""
        index = UUID(payload['index'])
        await self.channel_layer.send(self.__init_tty_queue[index], {
            'type': "terminal_output",
            'output': "节点安全设置:节点终端未启用",
            'update_status': 'close'
        })
        del self.__init_tty_queue[index]

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:output")
    async def __handle_terminal_output(self, payload=None):
        """终端内容输出"""
        channel = get_key_by_value(self.__tty_uuid, payload['uuid'], True)
        if channel:
            print(channel)
            await self.channel_layer.send(channel, {
                'type': "terminal_output",
                'output': payload['output']
            })
            try:
                self.__terminal_record_fd[payload['uuid']].write(payload['output'])
            except Exception as e:
                Log.error(f"终端记录写入错误！{e}")

    @Log.catch
    @AsyncBaseConsumer.action_handler("ping")
    async def __handle_ping(self):
        """处理节点Ping请求"""
        await self.send_action('pong')

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
        """更新缓存超时时间"""
        cache.set(
            f"node_client_online_{self.__node.uuid}",
            self.channel_name,
            timeout=self.__config.node.timeout / 1000
        )

    @Log.catch
    @AsyncBaseConsumer.action_handler("process_list:show")
    async def __process_list(self, data):
        """返回进程列表"""
        cache.set(f"node_{self.__node_uuid}_process_list", data, 5)
        await self.channel_layer.group_send(f"NodeControl_{self.__node_uuid}", {
            'type': 'show_process_list',
            'process_list': data
        })

    @Log.catch
    async def __load_alarm_setting(self):
        """加载节点告警设置"""
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
                    if not self.__alarm_status['disk'].get(disk_rule.device): self.__alarm_status['disk'][
                        disk_rule.device] = {
                        'alerted': False,
                        'event_start_time': None,
                        'event_end_time': None,
                        'event': None
                    }
                    if not self.__alarm_status['disk'][disk_rule.device]['event_start_time']:
                        self.__alarm_status['disk'][disk_rule.device]['event_start_time'] = datetime.now().timestamp()
                    await self.__disk_send_alarm_event(disk_rule.device,
                                                       calculate_percentage(disk['used'], disk['total']))
                else:
                    if self.__alarm_status['disk'].get(disk_rule.device) and \
                            self.__alarm_status['disk'][disk_rule.device]['event_start_time']:
                        self.__alarm_status['disk'][disk_rule.device]['event_end_time'] = datetime.now().timestamp()
                    await self.__disk_send_alarm_event(disk_rule.device,
                                                       calculate_percentage(disk['used'], disk['total']), end=True)

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
                start_time = datetime.fromtimestamp(self.__alarm_status[device]['event_start_time']).strftime(
                    '%Y-%m-%d %H:%M:%S')
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
                    start_time = datetime.fromtimestamp(self.__alarm_status[device]['event_start_time']).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    end_time = datetime.fromtimestamp(self.__alarm_status[device]['event_end_time']).strftime(
                        '%Y-%m-%d %H:%M:%S')
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
                (self.__alarm_status['network'][data_direction][
                     'event_start_time'] + self.__alarm_setting.delay_seconds < datetime.now().timestamp()) and
                # 验证结束时间
                (self.__alarm_status['network'][data_direction]['event_end_time'] is None or
                 self.__alarm_status['network'][data_direction][
                     'event_end_time'] + self.__alarm_setting.interval < datetime.now().timestamp())
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
                start_time = datetime.fromtimestamp(
                    self.__alarm_status['network'][data_direction]['event_start_time']).strftime('%Y-%m-%d %H:%M:%S')
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
                        start_time = datetime.fromtimestamp(
                            self.__alarm_status['network'][data_direction]['event_start_time']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        end_time = datetime.fromtimestamp(
                            self.__alarm_status['network'][data_direction]['event_end_time']).strftime(
                            '%Y-%m-%d %H:%M:%S')
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
    @AsyncBaseConsumer.action_handler("task:process_start")
    async def __task_process_statr(self, data: dict):
        """
        任务开始执行信号
        """
        Log.debug(f'{data.get("uuid")}:任务开始执行信号')
        self.__task_result_util = GroupTaskResultUtil(self.__node_uuid)
        await self.__task_result_util.handle_task_start(data)

    @AsyncBaseConsumer.action_handler("task:process_output")
    async def __task_process_output(self, data: dict):
        """
        任务执行时输出
        """
        Log.debug(f'{data.get("uuid")}:任务输出')
        await self.__task_result_util.handle_task_output(data)

    @AsyncBaseConsumer.action_handler("task:process_stop")
    async def __task_process_stop(self, data: dict):
        """
        任务执行结束信号
        """
        Log.debug(f'{data.get("uuid")}:任务结束信号')
        await self.__task_result_util.handle_task_stop(data)

    @Log.catch
    def __check_get_process_list_activity(self):
        """线程: 检查获取进程列表活动"""
        Log.debug("开始检查[获取进程列表]活动状态")
        while cache.get(f"node_{self.__node_uuid}_get_process_list_activity", False):
            time.sleep(1)
        # 缓存被销毁时发出结束获取进程列表信号
        Log.debug("停止获取进程列表")
        self.__get_process_list = False
        asyncio.run(self.send_action('process_list:stop'))

    @Log.catch
    def __check_node_timeout(self):
        """线程：检查节点是否超时"""
        while cache.get(f"node_client_online_{self.__node.uuid}", False) == self.channel_name:
            time.sleep(1)
        asyncio.run(self.close(3500))
