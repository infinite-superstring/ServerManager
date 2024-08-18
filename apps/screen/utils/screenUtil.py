import time

from apps.node_manager.models import Node, Node_BaseInfo
from apps.screen.entity.ScreenCacheKey import ScreenCacheKey
from apps.screen.utils.CacheUtil import CacheUtil
from apps.user_manager.models import User

cache = CacheUtil()
keys = ScreenCacheKey()


def node_go_online(node_info: dict):
    """一个节点上线"""
    node_online_info: dict = cache.get(keys.on_line_count)
    if node_online_info.get(node_info.get('uuid')) is not None:
        return
    node_online_info[node_info.get('uuid')] = node_info
    cache.set(keys.on_line_count, node_online_info)


def node_go_offline(node_uuid):
    """一个节点下线"""
    node_online_info: dict = cache.get(keys.on_line_count)
    del node_online_info[node_uuid]
    cache.set(keys.on_line_count, node_online_info)


def node_in_task():
    """一个节点进入任务"""
    cache.set(keys.tasking_count, cache.get(keys.tasking_count) + 1)


def node_out_task():
    """一个节点退出任务"""
    cache.set(keys.tasking_count, cache.get(keys.tasking_count) - 1)


def new_node():
    """新增一个节点"""
    cache.delete(keys.node_count)


def remove_node():
    """移除一个节点"""
    cache.delete(keys.node_count)


def new_alarming(node_uuid: str, alarming_status: dict):
    """进来一个新的告警事件"""
    node_is_alarming = _is_alarm_of(alarming_status)
    alarming_list: list[str] = cache.get(keys.alarm_count)

    if node_uuid not in alarming_list:
        if node_is_alarming:
            alarming_list.append(node_uuid)
            cache.set(keys.alarm_count, alarming_list)
    else:
        if not node_is_alarming:
            alarming_list.pop(alarming_list.index(node_uuid))
            cache.set(keys.alarm_count, alarming_list)


def remove_alarming(node_uuid: str):
    """移除一个告警事件"""
    alarming_list: list[str] = cache.get(keys.alarm_count)
    node_uuid = str(node_uuid)
    if node_uuid in alarming_list:
        alarming_list.pop(alarming_list.index(node_uuid))
        cache.set(keys.alarm_count, alarming_list)


def task_runtime(node_uuid: str, timestamp):
    """节点正在运行任务"""
    runtime_list: dict = cache.get(keys.tasking_count)
    # if node_uuid not in runtime_list:
    runtime_list[node_uuid] = timestamp
    cache.set(keys.tasking_count, runtime_list)


def task_stop(node_uuid: str):
    """节点停止运行任务"""
    runtime_list: dict = cache.get(keys.tasking_count)
    if node_uuid in runtime_list:
        runtime_list.pop(node_uuid)
        cache.set(keys.tasking_count, runtime_list)


def new_user():
    """新增一位用户"""
    cache.set(keys.user_count, cache.get(keys.user_count) + 1)


def remove_user():
    """用户离开"""
    cache.set(keys.user_count, cache.get(keys.user_count) - 1)


def reset_cache():
    """重置缓存"""
    node_count = Node.objects.all().count()
    user_count = User.objects.all().count()

    cache.set(keys.user_count, user_count)
    cache.set(keys.node_count, node_count)
    cache.set(keys.on_line_count, {})
    cache.set(keys.alarm_count, [])
    cache.set(keys.tasking_count, {})


def _is_alarm_of(alarming_status: dict) -> bool:
    """判断是否是告警事件"""
    key = 'alerted'

    def __network_is_alarm_of(network: dict) -> bool:
        """判断网络是否是告警事件"""
        return network.get('send').get(key) or \
            network.get('recv').get(key)

    def __dick_is_alarm_of(disk_status: dict) -> bool:
        """判断硬盘是否是告警事件"""
        disk_list = list(disk_status.keys())
        for d in disk_list:
            if disk_status.get(d).get(key):
                return True
        return False

    if alarming_status.get(keys.alarm_key.cpu).get(key) or \
            __dick_is_alarm_of(alarming_status.get(keys.alarm_key.disk)) or \
            alarming_status.get(keys.alarm_key.memory).get(key) or \
            __network_is_alarm_of(alarming_status.get(keys.alarm_key.network)):
        return True
    return False


def _remove_timeout_task(tasking: dict) -> dict:
    """
    移除超时的任务
    """
    current_time = time.time()  # 获取当前时间的时间戳
    keys_to_remove = []
    for k in list(tasking.keys()):
        timestamp = tasking[k]
        time_diff = current_time - timestamp
        if time_diff < 60:
            keys_to_remove.append(k)
    for key in keys_to_remove:
        del tasking[key]
    return tasking


def pack_node_data():
    node_online_info: dict | None = cache.get(keys.on_line_count)
    base_status: dict = {}

    average_load: list = []
    network: list = []
    memory: list = []
    cpu: list = []
    for node_uuid in node_online_info:
        node_name = node_online_info.get(node_uuid).get('name')
        node_use: dict = cache.get(f"NodeUsageData_{node_uuid}")
        if node_use is None:
            continue
        node_info: dict = node_online_info.get(node_uuid)
        base_info: Node_BaseInfo = node_info.get('baseInfo')
        one_minute = node_use.get('loadavg').get('one_minute')
        load = (one_minute / base_info.processor_count) * 100
        average_load.append({
            'name': node_name,
            'data': load
        })

        network.append({
            'name': node_name,
            'data': {
                'ip': node_info.get('ip'),
                'send': node_use.get('network_io').get('_all').get('bytes_sent'),
                'recv': node_use.get('network_io').get('_all').get('bytes_recv')
            }
        })

        memory.append({
            'name': node_name,
            'data': node_use.get('memory_used')
        })

        cpu_list: dict = node_use.get('cpu_core')
        cpu_usage_rate_list: list = []
        for c in cpu_list:
            cpu_usage_rate_list.append(cpu_list.get(c))
        cpu.append({
            'name': node_name,
            'data': max(cpu_usage_rate_list)
        })
    base_status['host_status'] = _handle_host_status(node_online_info)
    base_status['average_load'] = _handle_top(average_load)
    base_status['network'] = _handle_top(network, top=3, lm=lambda x: x['data']['send'] + x['data']['recv'])
    base_status['memory'] = _handle_top(memory)
    base_status['cpu'] = _handle_top(cpu)
    return base_status


def _handle_host_status(node_online_info: dict) -> list:
    """
    处理主机状态
    """
    node_count: int = cache.get(keys.node_count)
    online: int = len(node_online_info.keys())
    in_alarm: int = len(cache.get(keys.alarm_count))
    # 正常 告警 离线
    return [online - in_alarm, in_alarm, node_count - online]


def _handle_top(data: list, top: int = 10, lm=lambda x: x['data']) -> list:
    """
    处理排序数据
    """
    new_list = sorted(data, key=lm, reverse=True)
    return new_list[0:top]


def get_top_data():
    tasking: dict = cache.get(keys.tasking_count)
    tasking: dict = _remove_timeout_task(tasking)
    tasking_count = len(tasking.keys())
    node_online_count = len(cache.get(keys.on_line_count).keys()) if \
        cache.get(keys.on_line_count) else \
        0
    return {
        'user_count': cache.get(keys.user_count),
        'node_count': cache.get(keys.node_count),
        'on_line_count': node_online_count,
        'tasking_count': tasking_count,
        'alarm_count': cache.get(keys.alarm_count)
    }
