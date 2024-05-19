from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from util.logger import Log

@Log.catch
def node_usage_update(sender, **kwargs):
    node_uuid = f"NodeControl_{sender}"
    usage_data = kwargs['usage_data']
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(node_uuid, {
        'type': 'update_node_usage_data',
        'usage_data': usage_data
    })

@Log.catch
def node_offline(sender, **kwargs):
    node_uuid = f"NodeControl_{sender}"
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(node_uuid, {
        'type': 'node_offline'
    })

@Log.catch
def node_online(sender, **kwargs):
    node_uuid = f"NodeControl_{sender}"
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(node_uuid, {
        'type': 'node_online'
    })