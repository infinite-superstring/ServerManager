from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from util.logger import Log

@Log.catch
def init_tty(sender, **kwargs):
    node_uuid = kwargs['node_uuid']
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"NodeClient_{node_uuid}", {
        'type': 'init_tty',
        'sender': sender,
    })
