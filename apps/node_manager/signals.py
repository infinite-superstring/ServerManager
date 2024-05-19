from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import Signal
from .receivers import *

# 信号 - 节点使用率更新
node_usage_update_signal = Signal()
# 信号 - 节点上线
node_online_signal = Signal()
# 信号 - 节点下线
node_offline_signal = Signal()

node_usage_update_signal.connect(node_usage_update)
node_online_signal.connect(node_online)
node_offline_signal.connect(node_offline)

