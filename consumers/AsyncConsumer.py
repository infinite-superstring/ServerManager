import json

from channels.generic.websocket import AsyncWebsocketConsumer
from abc import ABC, abstractmethod

from util.jsonEncoder import ComplexEncoder
from util.logger import Log


class AsyncBaseConsumer(AsyncWebsocketConsumer, ABC):
    actions = {}

    @classmethod
    def action_handler(cls, action):
        """
        类方法，装饰器，用于将函数注册为特定 action 的处理函数。
        :param action: 字符串，表示要处理的 action 类型
        """

        def decorator(func):
            # 为函数添加一个 _actions 属性，用于存储处理的 action 列表
            if not hasattr(func, '_actions'):
                func._actions = []
            func._actions.append(action)
            return func

        return decorator

    @classmethod
    def register_action(cls, action, func):
        """
        类方法，用于注册 action 和处理函数的映射关系。
        :param action: 字符串，表示 action 类型
        :param func: 函数，处理该 action 的函数
        """
        if action not in cls.actions:
            cls.actions[action] = func

    @classmethod
    def register_all_actions(cls):
        """
        类方法，用于注册所有带有 action_handler 装饰器的处理函数。
        """
        for name, method in cls.__dict__.items():
            if hasattr(method, '_actions'):
                for action in method._actions:
                    cls.register_action(action, method)

    def __init_subclass__(cls, **kwargs):
        """
        子类初始化时调用，用于注册所有带有 action_handler 装饰器的处理函数。
        """
        super().__init_subclass__(**kwargs)
        cls.register_all_actions()

    @abstractmethod
    async def connect(self):
        """
        WebSocket 连接建立时调用的异步方法。
        """
        pass

    @abstractmethod
    async def disconnect(self, close_code):
        """
        WebSocket 连接断开时调用的异步方法。
        :param close_code: 关闭代码
        """
        pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        WebSocket 接收到消息时调用的异步方法。
        :param text_data: 接收到的文本数据，通常为 JSON 格式
        """
        if bytes_data:
            return self.handle_bytes_data(bytes_data)
        if not text_data:
            Log.warning("Text data is None")
        try:
            data = json.loads(text_data)  # 将接收到的 JSON 文本数据解析为字典
        except Exception as e:
            return Log.error(f"try load json error: {e}")
        action = data.get('action')  # 获取 action 类型
        payload = data.get('data', None)  # 获取可选参数 data
        Log.debug(f"action: {action}, payload: {payload}")
        # 根据 action 类型调用相应的处理函数
        if action in self.actions:
            if payload is not None:
                await self.actions[action](self, payload)  # 带有 payload 调用
            else:
                await self.actions[action](self)  # 不带 payload 调用
        else:
            Log.error("Invalid action")

    async def handle_bytes_data(self, data):
        """处理二进制数据"""
        pass

    @Log.catch
    async def send_json(self, data: dict):
        """发送Json数据"""
        await self.send(json.dumps(data, cls=ComplexEncoder))