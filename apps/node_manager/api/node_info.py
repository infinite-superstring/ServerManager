from django.http import HttpRequest

from apps.node_manager.models import Node_DiskPartition, Node_AlarmSetting
from apps.node_manager.utils.nodeUtil import node_uuid_exists, get_node_by_uuid
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log


def get_disk_partition_list(req: HttpRequest):
    """获取节点磁盘分区列表"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_uuid = req_json.get('node_uuid')
    if node_uuid is None:
        ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not node_uuid_exists(node_uuid):
        ResponseJson({'status': 0, 'msg': '节点不存在'})
    node = get_node_by_uuid(node_uuid)
    return ResponseJson({
        'status': 1,
        'data': {
            'disk_partition': list(Node_DiskPartition.objects.filter(node=node).values_list('device', flat=True))
        }
    })

def get_alarm_setting(req: HttpRequest):
    """获取节点告警设置"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_uuid = req_json.get('node_uuid')
    if node_uuid is None:
        ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not node_uuid_exists(node_uuid):
        ResponseJson({'status': 0, 'msg': '节点不存在'})
    node = get_node_by_uuid(node_uuid)
    alarm_setting = Node_AlarmSetting.objects.filter(node=node).first()
    cpu_rule = alarm_setting.general_rules.filter(module="CPU").first() if alarm_setting else None
    memory_rule = alarm_setting.general_rules.filter(module="Memory").first() if alarm_setting else None
    network_rule = alarm_setting.network_rule if alarm_setting else None
    disk_rules = alarm_setting.disk_used_rules if alarm_setting and alarm_setting.disk_used_rules.exists() else []
    return ResponseJson({
        'status': 1,
        'data': {
            'enable': alarm_setting.enable if alarm_setting else False,
            'delay_seconds': alarm_setting.delay_seconds if alarm_setting else None,
            'cpu': {
                'enabled': cpu_rule.enable if cpu_rule else False,
                'threshold': cpu_rule.threshold if cpu_rule else None,
                'updated_at': cpu_rule.updated_at if cpu_rule else None,
            },
            'memory': {
                'enabled': memory_rule.enable if memory_rule else False,
                'threshold': memory_rule.threshold if memory_rule else None,
                'updated_at': memory_rule.updated_at if memory_rule else None,
            },
            'network': {
                'enable': network_rule.enable if network_rule else False,
                'send_threshold': network_rule.send_threshold if network_rule else None,
                'receive_threshold': network_rule.receive_threshold if network_rule else None,
                'updated_at': network_rule.updated_at if network_rule else None,
            },
            'disk': [
                {
                    'enable': i.enable,
                    'device': i.device,
                    'threshold': i.threshold
                } for i in disk_rules
            ]
        }
    })


def save_alarm_setting(req: HttpRequest):
    """保存节点告警设置"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_uuid = req_json.get('node_uuid')
    if node_uuid is None:
        ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not node_uuid_exists(node_uuid):
        ResponseJson({'status': 0, 'msg': '节点不存在'})
    node = get_node_by_uuid(node_uuid)
