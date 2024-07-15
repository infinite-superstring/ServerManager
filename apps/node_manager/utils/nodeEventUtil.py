from datetime import datetime

from asgiref.sync import sync_to_async

from apps.node_manager.models import Node, Node_Event
from util.logger import Log


class NodeEventUtil:
    __stop: bool = False
    __event: Node_Event = None

    def __init__(self, node: Node, type: str, desc: str, level: str = 'Info', end_directly=False):
        """
        新建节点事件
        :param node: Node 节点对象
        :param type: str 事件类型
        :param desc: str 事件描述
        :param level: str 事件等级
        :param end_directly: bool 直接结束事件
        """
        self.__event = Node_Event.objects.create(
            node=node,
            type=type,
            description=desc,
            level=level,
        )
        if end_directly:
            self.__event.end_time = datetime.now()
            self.__stop = True
        Log.debug("Created NodeEvent")

    def __del__(self):
        self.__event.end_time = datetime.now()
        self.__event.save()
        self.__stop = True
        Log.debug("Deleting NodeEvent")

    def createPhase(self, title: str, data: str = ""):
        """
        创建事件阶段（要在关闭前）
        :param title: str 事件阶段标题
        :param data: str 事件阶段数据
        """
        if self.isStopped():
            raise RuntimeError("Event Status is Stop")
        phase = Node_Event.EventPhase.objects.create(
            node=self.__event,
            title=title,
            description=data,
        )
        self.__event.phase.add(phase)
        self.__event.save()
        Log.debug("Created Phase")

    def stopEvent(self):
        """
        结束该事件
        """
        if self.isStopped():
            raise RuntimeError("Event Status is Stop")
        self.__event.end_time = datetime.now()
        self.__event.save()
        Log.debug(f"Event {self.__event.id} stopped")
        self.__stop = True

    def isStopped(self):
        """
        该事件是否已结束
        """
        return self.__stop


def getNodeEvents(node: Node):
    """获取节点事件列表"""
    return Node_Event.objects.filter(node=node)


async def createEvent(node: Node, type: str, desc: str, level: str = 'Info', end_directly=False) -> Node_Event:
    """
    创建事件实例
    :param node: Node 节点对象
    :param type: str 事件类型
    :param desc: str 事件介绍
    :param level: str 事件等级
    :param end_directly: bool 立即停止事件
    :return: Node_Event
    """
    event = await Node_Event.objects.acreate(
        node=node,
        type=type,
        description=desc,
        level=level,
    )
    if end_directly:
        event.end_time = datetime.now()
        await event.asave()
    return event


async def eventStatusIsStopped(event: Node_Event) -> bool:
    """
    事件状态是否为已停止
    :param event: Node_Event 事件对象
    :return: bool
    """
    if event.end_time:
        return True
    return False


async def stopEvent(event: Node_Event) -> Node_Event:
    """
    停止事件
    :param event: Node_Event 事件对象
    :return: Node_Event
    """
    if await eventStatusIsStopped(event):
        Log.warning("Event status is Stop")
        return event
    event.end_time = datetime.now()
    await event.asave()
    return event


async def createPhase(event: Node_Event, title: str, data: str = "") -> Node_Event:
    """
    创建事件步骤
    :param event: Node_Event 事件对象
    :param title: str 步骤标题
    :param data: str 步骤数据
    :return: Node_Event
    """
    if await eventStatusIsStopped(event):
        Log.warning("Event status is Stop")
        return event
    await sync_to_async(event.phase.add)(await Node_Event.EventPhase.objects.acreate(
        title=title,
        description=data,
    ))
    return event


def event_id_exists(event_id) -> bool:
    """检查事件ID是否存在"""
    return Node_Event.objects.filter(id=event_id).exists()


async def event_id_aexists(event_id) -> bool:
    """检查事件ID是否存在"""
    return await Node_Event.objects.filter(id=event_id).aexists()


def get_event_by_id(event_id) -> Node_Event:
    """使用ID获取事件信息"""
    if not event_id_exists(event_id):
        raise RuntimeError("Event is not exist")
    return Node_Event.objects.get(id=event_id)


async def aget_event_by_id(event_id) -> Node_Event:
    """使用ID获取事件信息"""
    if not await event_id_aexists(event_id):
        raise RuntimeError("Event is not exist")
    return await Node_Event.objects.aget(id=event_id)
