from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from util.logger import Log
# @receiver(node_usage_update_signal)

@Log.catch
def node_usage_update_signal_receiver(sender, **kwargs):
    node_uuid = str(sender)
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(node_uuid, {
        'type': 'update_node_usage_data'
    })