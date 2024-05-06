from django.urls import path
from node_manager.websocket.node_client import node_client

websocket_urlpatterns = [
    # 节点客户端
    path(r"node/websocket/node_cilent", node_client.as_asgi()),
]