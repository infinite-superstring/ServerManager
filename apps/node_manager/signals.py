from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import Signal
from .receivers import *
# 控制端刷新
control_refresh = Signal()
# 连接终端
connect_terminal = Signal()

connect_terminal.connect(init_tty)
