from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import Signal
from .receivers import node_usage_update_signal_receiver

# 信号 - 节点使用率更新
node_usage_update_signal = Signal()

node_usage_update_signal.connect(node_usage_update_signal_receiver)

