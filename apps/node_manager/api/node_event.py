from django.http import HttpRequest

from apps.node_manager.utils.nodeUtil import node_uuid_exists
from apps.node_manager.utils.nodeEventUtil import getNodeEvents, event_id_exists, get_event_by_id
from apps.node_manager.models import Node_Event
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.pageUtils import get_page_content, get_max_page
from util.logger import Log


def get_node_events(req: HttpRequest):
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node = req_json.get('node_uuid')
    if not node:
        return ResponseJson({'status': -1, 'msg': '参数不完整'}, 400)
    if not node_uuid_exists(node):
        return ResponseJson({'status': 0, 'msg': '节点不存在'})
    PageContent: list = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    result = getNodeEvents(node)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                'event_id': item.get('id'),
                'type': item.get('type'),
                'desc': item.get('description'),
                'level': item.get('level'),
                'update_time': item.get('update_time'),
                'closed': True if item.get('end_time') else False,
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


def get_event_info(req: HttpRequest):
    """获取节点事件信息"""
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    event = req_json.get('event_id')
    if not event:
        return ResponseJson({'status': -1, 'msg': '参数不完整'}, 400)
    if not event_id_exists(event):
        return ResponseJson({'status': 0, 'msg': '事件ID不存在'})
    event: Node_Event = get_event_by_id(event)
    return ResponseJson({'status': 1, 'data': {
        "start_time": event.start_time,
        "update_time": event.update_time,
        "end_time": event.end_time,
        'phase': [{'title': i.title, 'desc': i.description} for i in event.phase.all()]
    }})