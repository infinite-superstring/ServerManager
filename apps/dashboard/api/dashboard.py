from util.Response import *
from util.Request import *
from util.logger import Log
from apps.node_manager.utils.nodeUtil import get_node_count, get_node_online_count, get_node_offline_count, get_node_warning_count
from django.http.request import HttpRequest


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
    pass


def get_statistics(req: HttpRequest):
    """获取统计信息"""
    pass


def get_tasks(req: HttpRequest):
    """获取任务列表"""
    pass