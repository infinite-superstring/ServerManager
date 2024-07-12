import json
import time

from asgiref.sync import sync_to_async
from django.utils import timezone
from uuid import UUID, uuid1

from channels.exceptions import StopConsumer
from django.core.cache import cache

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData, Node_TerminalRecord, Node_Event
from apps.node_manager.utils.nodeUtil import read_performance_record, is_node_available_for_user
from apps.node_manager.utils.tagUtil import aget_node_tags
from apps.setting.entity import Config
from apps.user_manager.models import User
from consumers.AsyncConsumer import AsyncBaseConsumer
from apps.user_manager.util.userUtils import uid_aexists
from apps.node_manager.utils.nodeEventUtil import createEvent, stopEvent, createPhase
from apps.permission_manager.util.permission import groupPermission
from util.logger import Log


class node_control(AsyncBaseConsumer):
    __connect_terminal_flag: bool = False
    __node_uuid: UUID = None
    __userID: int = None
    __user: User = None
    __clientIP: str = None
    __client_UUID: str = None
    __config: Config = None
    __node: Node = None
    __node_base_info: Node_BaseInfo = None
    __terminal_connect_event: Node_Event

    async def connect(self):
        # 在建立连接时执行的操作
        self.__clientIP = self.scope["client"][0]
        if (not (self.scope["session"].get("userID") or self.scope["session"].get("user")) and
                self.scope["session"].get("auth_method") != 'Node Auth'):
            Log.warning("非法访问：用户未登录")
            await self.close(0)
        self.__userID = self.scope["session"].get("userID")
        if await uid_aexists(self.__userID):
            self.__user = await User.objects.aget(id=self.__userID)
        else:
            Log.warning("非法访问：用户不存在")
            await self.close(0)
        if not self.scope['url_route']['kwargs']['node_uuid']:
            Log.debug("参数不完整")
            return self.close(-1)
        self.__node_uuid = UUID(self.scope['url_route']['kwargs']['node_uuid'])
        if not await Node.objects.filter(uuid=self.__node_uuid).aexists():
            Log.info(f"用户{self.__user.userName}尝试连接的节点{self.__node_uuid}不存在，连接已断开")
            return self.close(0)
        self.__node = await Node.objects.aget(uuid=self.__node_uuid)
        if not await sync_to_async(is_node_available_for_user)(self.__user, self.__node):
            Log.warning(f"用户{self.__user.userName}当前无权限操作节点，连接已断开")
            return self.close(0)
        # 加入组
        await self.channel_layer.group_add(
            f"NodeControl_{self.__node.uuid}",
            self.channel_name
        )
        self.__client_UUID = str(uuid1())
        await self.accept()
        await self.__init_data()

    async def disconnect(self, close_code):
        if self.__node:
            # 离开组
            await self.channel_layer.group_discard(
                f"NodeControl_{self.__node.uuid}",
                self.channel_name
            )
        if self.__connect_terminal_flag:
            await self.__close_terminal()
        raise StopConsumer

    async def receive(self, *args, **kwargs):
        """处理节点收到信息时"""
        if not await sync_to_async(is_node_available_for_user)(self.__user, self.__node):
            Log.warning(f"用户{self.__user.userName}当前无权限操作节点")
            return self.close(0)
        await super().receive(*args, **kwargs)

    @Log.catch
    async def __init_data(self):
        """初始化页面数据"""
        usage_data = None
        node_system_info = None
        if await Node_BaseInfo.objects.filter(node=self.__node).aexists():
            self.__node_base_info = await Node_BaseInfo.objects.aget(node=self.__node)
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
        if node_system_info and await Node_UsageData.objects.filter(node=self.__node).aexists():
            usage_data: dict = cache.get(f"NodeUsageData_{self.__node.uuid}")
        node_group = await sync_to_async(lambda: self.__node.group)()
        await self.send_action('init', {
            "base_info": {
                "node_uuid": self.__node_uuid,
                "node_name": self.__node.name,
                "node_online": self.__node_base_info.online if self.__node_base_info else False,
                "node_description": self.__node.description,
                "node_group": node_group.name if node_group else None,
                "node_tags": await aget_node_tags(self.__node),
                "node_system_info": node_system_info,
            },
            "usage": usage_data if usage_data else None
        })

    @Log.catch
    async def update_node_usage_data(self, event):
        """
        更新节点使用率数据
        """
        await self.send_action('node:update_usage_data', event['usage_data'])

    @Log.catch
    async def node_online(self, event):
        """节点上线"""
        await self.send_action('node:online')
        await self.__init_data()

    @Log.catch
    async def node_offline(self, event):
        """节点离线"""
        await self.send_action('node:offline')

    @Log.catch
    async def terminal_output(self, event):
        """显示终端输出"""
        await self.send_action('terminal:output', event['output'])

    @Log.catch
    async def terminal_ready(self, event):
        """终端就绪"""
        await createPhase(self.__terminal_connect_event, "终端就绪")
        await Node_TerminalRecord.objects.acreate(
            user=self.__user,
            user_ip_address=self.__clientIP,
            node=self.__node,
            session_id=event['session_id'],
        )
        await self.send_action('terminal:ready')

    @Log.catch
    async def terminal_login_failed(self, event):
        """终端登录错误"""
        await createPhase(self.__terminal_connect_event, "终端SSH登录失败")
        await stopEvent(self.__terminal_connect_event)
        self.__connect_terminal_flag = False
        await self.send_action('terminal:login_failed')

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:input")
    async def terminal_input(self, command):
        """终端输入"""
        if not self.__connect_terminal_flag:
            raise RuntimeError("Terminal not connected")
        await self.__send_group_to_client('input_command', {
            "command": command,
            'sender': self.channel_name,
        })

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:login")
    async def terminal_login(self, payload):
        """终端登录"""
        if self.__connect_terminal_flag:
            raise RuntimeError("Terminal is already connected")
        self.__terminal_connect_event = await createEvent(
            node=self.__node,
            type='终端连接',
            desc=f'用户: {self.__user.userName}({self.__user.id})',
        )
        self.__connect_terminal_flag = True
        if self.__node_base_info.system != "Windows":
            await createPhase(self.__terminal_connect_event, f"发起SSH登录，用户名: {payload.get('username')}")
        await self.__send_group_to_client('connect_terminal', {
            'host': payload.get('host', "127.0.0.1"),
            'port': payload.get('port', 22),
            'username': payload.get('username'),
            'password': payload.get('password'),
            'sender': self.channel_name
        })

    @Log.catch
    @AsyncBaseConsumer.action_handler('terminal:resize')
    async def terminal_resize(self, payload):
        """调整终端大小"""
        if not self.__connect_terminal_flag:
            raise RuntimeError("Terminal not connected")
        await self.__send_group_to_client('terminal_resize', {
            'sender': self.channel_name,
            'cols': payload['cols'],
            'rows': payload['rows'],
        })

    @Log.catch
    async def show_process_list(self, event):
        """展示进程列表"""
        await self.send_action('process_list:show', event['process_list'])

    @Log.catch
    @AsyncBaseConsumer.action_handler("terminal:close")
    async def __close_terminal(self):
        """用户发起终端关闭请求"""
        if not self.__connect_terminal_flag:
            raise RuntimeError("Terminal not connected")
        await createPhase(self.__terminal_connect_event, "终端连接关闭(用户发起)")
        await stopEvent(self.__terminal_connect_event)
        self.__connect_terminal_flag = False
        await self.__send_group_to_client('close_terminal', {
            'sender': self.channel_name,
        })

    @Log.catch
    @AsyncBaseConsumer.action_handler("process_list:load")
    async def __get_process_list(self):
        """获取进程列表"""
        cache.set(f"node_{self.__node_uuid}_get_process_list_activity", time.time(), timeout=10)
        await self.channel_layer.group_send(f"NodeClient_{self.__node_uuid}", {
            'type': 'start_get_process_list',
            'sender': self.channel_name,
        })
        if cache.get(f"node_{self.__node_uuid}_process_list"):
            await self.send_action('process_list:show', cache.get(f"node_{self.__node_uuid}_process_list"))

    @Log.catch
    @AsyncBaseConsumer.action_handler("process_list:heartbeat")
    async def __update_process_list_heartbeat(self):
        """更新进程列表 - 心跳"""
        cache.set(f"node_{self.__node_uuid}_get_process_list_activity", time.time(), timeout=10)

    @Log.catch
    @AsyncBaseConsumer.action_handler("process_list:kill")
    async def __kill_process(self, data):
        """杀死进程"""
        await self.__send_group_to_client('kill_process', {
            'pid': data.get('pid'),
            'tree_mode': data.get('tree_mode')
        })

    @Log.catch
    @AsyncBaseConsumer.action_handler("performance_record:get")
    async def __get_performance_record(self, data):
        """
        获取性能记录
        start_time: 开始时间
        end_time: 结束时间
        device: 设备，默认获取所有
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        device = data.get('device', "_all")
        if start_time and end_time:
            await self.__load_performance_record(start_time, end_time, device)

    @Log.catch
    @AsyncBaseConsumer.action_handler("performance_record:load")
    async def __load_performance_record(self, start_time=None, end_time=None, device="_all"):
        """
        加载性能记录
        """
        start_time = (timezone.now() - timezone.timedelta(days=1)).strftime(
            '%Y-%m-%d %H:%M:%S') if not start_time else start_time
        end_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S') if not end_time else end_time
        performance_record = await read_performance_record(self.__node, start_time, end_time)
        temp = []
        async for record in performance_record:
            item = {
                "timestamp": record.timestamp,
            }
            if device == "_all" or device == "cpu":
                item.update({
                    "cpu_usage": record.cpu_usage,
                    "cpu_cores_usage": [],
                })
                async for core in record.cpu_core_usage.all():
                    item["cpu_cores_usage"].append({
                        "core": core.core_index,
                        "usage": core.usage,
                    })
            if device == "_all" or device == "memory":
                item.update({
                    "memory_total": self.__node_base_info.memory_total,
                    "memory_used": record.memory_used,
                })
            if device == "_all" or device == "disk_io":
                item.update({
                    "disk_io_read_bytes": record.disk_io_read_bytes,
                    "disk_io_write_bytes": record.disk_io_write_bytes,
                })
            if device == "_all" or device == "network":
                item.update({
                    "network_usage": [],
                })
                async for network_port in record.network_usage.all():
                    item["network_usage"].append({
                        "name": network_port.port_name,
                        "bytes_sent": network_port.bytes_sent,
                        "bytes_recv": network_port.bytes_recv,
                    })
            if device == "_all" or device == "loadavg":
                system_loadavg = await sync_to_async(lambda: record.system_loadavg)()
                item.update({
                    "system_loadavg": {
                        "processor_count": self.__node_base_info.processor_count,
                        "one_minute": system_loadavg.one_minute,
                        "five_minute": system_loadavg.five_minute,
                        "fifteen_minute": system_loadavg.fifteen_minute,
                    }
                })
            temp.append(item)
        await self.send_action('performance_record:show', {
            "device": device,
            "start_time": start_time,
            "end_time": end_time,
            "usage_data": temp
        })

    async def __send_group_to_client(self, type: str, data: dict):
        await self.channel_layer.group_send(f"NodeClient_{self.__node_uuid}", {**{
            'type': type,
        }, **data})
