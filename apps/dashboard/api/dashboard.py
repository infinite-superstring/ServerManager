from django.db.models import QuerySet

from apps.audit.models import Node_Session_Log
from apps.node_manager.models import Node, Node_BaseInfo, Node_Event
from util import result
from util.Response import *
from util.Request import *
from util.logger import Log
from apps.dashboard.utils.api_call_count import get_hourly_api_call_count, get_alarm_trend
from apps.node_manager.utils.nodeUtil import get_node_count, get_node_online_count, get_node_offline_count, \
    get_node_warning_count
from django.http.request import HttpRequest
from apps.task.api.task import getList


def get_overview(req: HttpRequest):
    """获取总览信息"""
    return ResponseJson({
        'status': 1,
        'data': {
            'node_count': get_node_count(),
            'node_online_count': get_node_online_count(),
            'node_offline_count': get_node_offline_count(),
            'node_warning_count': get_node_warning_count(),
        }
    })


def get_node_list(req: HttpRequest):
    """获取仪表盘用节点列表"""
    if req.method != 'GET':
        return result.api_error('请求方式错误')
    nodes: QuerySet[Node] = Node.objects.order_by('?')[:5]
    r = []
    for node in nodes:
        node_log: Node_Session_Log = Node_Session_Log.objects.filter(node=node).order_by('-time').first()
        node_base: Node_BaseInfo = Node_BaseInfo.objects.filter(node=node).first()
        node_event: Node_Event = Node_Event.objects.filter(node=node).first()
        r.append({
            'uuid': node.uuid,
            'name': node.name,
            'auth_ip': node_log.ip if node_log and node_base.online else False,
            'online': node_base.online if node_base else None,
            'warning': node_event.level if node_event and node_base.online else False
        })
    return result.success(r)


def get_statistics(req: HttpRequest):
    """获取统计信息"""
    return ResponseJson({
        'status': 1,
        'data': {
            'API_Speed': get_hourly_api_call_count(),
            "alarm_trend": get_alarm_trend()
        }
    })


def get_tasks(req: HttpRequest):
    """获取任务列表"""
    return getList(req)
