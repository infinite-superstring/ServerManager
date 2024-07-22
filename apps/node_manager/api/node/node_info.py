from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpRequest

from apps.audit.util.auditTools import write_access_log, write_audit
from apps.node_manager.models import Node_DiskPartition, Node_AlarmSetting
from apps.node_manager.utils.nodeUtil import node_uuid_exists, get_node_by_uuid, init_node_alarm_setting
from apps.permission_manager.util.api_permission import api_permission
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
    write_access_log(req.session['userID'], req, "节点信息", f"获取节点{node.name}(uuid:{node.uuid})磁盘列表")
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
    disk_rules = alarm_setting.disk_used_rules.all() if alarm_setting and alarm_setting.disk_used_rules.exists() else []
    write_access_log(req.session['userID'], req, "节点信息", f"获取节点{node.name}(uuid:{node.uuid})告警设置")
    return ResponseJson({
        'status': 1,
        'data': {
            'enable': alarm_setting.enable if alarm_setting else False,
            'delay_seconds': alarm_setting.delay_seconds if alarm_setting else None,
            'cpu': {
                'enable': cpu_rule.enable if cpu_rule else False,
                'threshold': cpu_rule.threshold if cpu_rule else None,
                'updated_at': cpu_rule.updated_at if cpu_rule else None,
            },
            'memory': {
                'enable': memory_rule.enable if memory_rule else False,
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
                    'device': i.device.device,
                    'threshold': i.threshold
                } for i in disk_rules
            ]
        }
    })

@api_permission("editNode")
def save_alarm_setting(req: HttpRequest):
    """保存节点告警设置"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_uuid: str = req_json.get('node_uuid')
    setting: dict = req_json.get('setting')
    if not (node_uuid and setting):
        ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not node_uuid_exists(node_uuid):
        ResponseJson({'status': 0, 'msg': '节点不存在'})
    node = get_node_by_uuid(node_uuid)
    if not Node_AlarmSetting.objects.filter(node=node).exists():
        a_setting = init_node_alarm_setting(node)
    else:
        a_setting = Node_AlarmSetting.objects.filter(node=node).first()
    for key, value in setting.items():
        match key:
            case 'enable':
                a_setting.enable = value
            case 'delay_seconds':
                a_setting.delay_seconds = value
            case 'cpu':
                cpu_rule = a_setting.general_rules.filter(module="CPU").first()
                cpu_rule.enable = value.get("enable")
                cpu_rule.threshold = value.get("threshold")
                cpu_rule.save()
            case 'memory':
                memory_rule = a_setting.general_rules.filter(module="Memory").first()
                memory_rule.enable = value.get("enable")
                memory_rule.threshold = value.get("threshold")
                memory_rule.save()
            case 'network':
                network_rule = a_setting.network_rule
                network_rule.enable = value.get("enable")
                network_rule.send_threshold = value.get("send_threshold")
                network_rule.receive_threshold = value.get("receive_threshold")
                network_rule.save()
            case 'disk':
                disk_rules = a_setting.disk_used_rules
                devices = []
                for i in value:
                    if not i.get('device'):
                        continue
                    device = Node_DiskPartition.objects.filter(node=node, device=i.get('device')).first()
                    if not device:
                        Log.warning(f"Disk {i.get('device')} does not exist")
                        continue
                    if device in devices:
                        Log.warning(f"{i.get('device')} disk has been used")
                        continue
                    devices.append(device)
                    if disk_rules.filter(device=device).exists():
                        rule = disk_rules.filter(device=device).first()
                        rule.threshold = i.get('threshold')
                        rule.save()
                    else:
                        a_setting.disk_used_rules.add(Node_AlarmSetting.DiskUsedAlarmRule.objects.create(
                            device=device,
                            threshold=i.get('threshold'),
                        ))
                disk_rules.exclude(device__in=devices).delete()
    a_setting.save()
    write_audit(req.session['userID'], "编辑节点告警设置", "节点信息", f"设置数据：{setting}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'NodeClient_{node_uuid}', {
        'type': 'reload_alarm_setting',
    })
    return ResponseJson({
        'status': 1,
        'msg': '保存成功'
    })
