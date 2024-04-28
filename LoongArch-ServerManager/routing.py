from django.urls import path
from file_manager.websocket.fileManager import fileManagerPageWebSocket

websocket_urlpatterns = [
    # 文件管理页
    path(r"api/websocket/fileManager", fileManagerPageWebSocket.as_asgi())
]