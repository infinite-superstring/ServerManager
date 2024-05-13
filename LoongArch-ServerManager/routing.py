from django.urls import path
from apps.node_manager.websocket.node_client import node_client
from apps.node_manager.websocket.node_control import node_control

websocket_urlpatterns = [
    # 节点客户端
    path(r"node/websocket/node_cilent", node_client.as_asgi()),
    # 节点控制器
    path(r"node_manager/websocket/node_control/<str:node_uuid>/", node_control.as_asgi())
]