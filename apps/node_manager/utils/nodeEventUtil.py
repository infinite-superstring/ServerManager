from datetime import datetime

from node_manager.models import Node, Node_Event
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
        :param endDirectly: bool 直接结束事件
        """
        self.__event = Node_Event.objects.create(
            node=node,
            type=type,
            description=desc,
            level=level,
        )
        Log.debug("Created NodeEvent")

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
            data=data,
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
