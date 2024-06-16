from apps.node_manager.models import Node_Group, Node_MessageRecipientRule
from apps.node_manager.utils.groupUtil import create_message_recipient_rules, node_group_id_exists, \
    get_node_group_by_id, get_group_nodes
from apps.node_manager.utils.nodeUtil import node_uuid_exists, get_node_by_uuid, node_set_group
from apps.user_manager.util.userUtils import uid_exists, get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from django.http.request import HttpRequest


def get_group_list(req: HttpRequest):
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    PageContent: list = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    search = req_json.get("search", "")
    result = Node_Group.objects.filter(name__icontains=search)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "group_id": item.get("id"),
                "group_name": item.get("name"),
                "group_leader": get_user_by_id(item.get("leader_id")).userName,
                "group_desc": item.get("description"),
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


def create_group(req: HttpRequest):
    """创建组"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    # 组名
    group_name: str = req_json.get('group_name')
    # 组介绍
    group_desc: str = req_json.get('group_desc')
    # 组负责人
    group_leader: int = req_json.get('group_leader')
    # 组节点列表
    group_nodes: list = req_json.get('group_nodes')
    # 组消息发送规则
    rules: list = req_json.get('rules')
    if not (group_name and group_leader and rules):
        return ResponseJson({'status': -1, 'msg': '参数不完整'})
    if Node_Group.objects.filter(name=group_name).exists():
        return ResponseJson({"status": 0, "msg": "节点组已存在"})
    if not uid_exists(group_leader):
        return ResponseJson({'status': 0, 'msg': '节点组负责人不存在'})
    group = Node_Group.objects.create(
        name=group_name,
        description=group_desc,
        leader=get_user_by_id(group_leader)
    )
    for node in group_nodes:
        if not node_uuid_exists(node):
            Log.warning(f"节点{node}不存在")
            continue
        node_set_group(node, group.id)
    rules = create_message_recipient_rules(rules)
    for rule in rules:
        group.time_slot_recipient.add(rule)
    return ResponseJson({'status': 1, 'msg': '节点组创建成功'})


def del_group(req: HttpRequest):
    """删除组"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    group_id: int = req_json.get('group_id')
    if not group_id:
        return ResponseJson({'status': -1, 'msg': "参数不完整"}, 400)
    if not node_group_id_exists(group_id):
        return ResponseJson({'status': 0, 'msg': '节点组不存在'})
    group = get_node_group_by_id(group_id)
    nodes = get_group_nodes(group)
    for node in nodes:
        node.group = None
        node.save()
    for rule in group.time_slot_recipient.all():
        group.time_slot_recipient.remove(rule)
        rule.delete()
    group.delete()
    return ResponseJson({'status': 1, 'msg': '节点组删除成功'})


def edit_group(req: HttpRequest):
    """编辑组"""


def get_group_by_id(req: HttpRequest):
    """获取组详细"""

    def _get_week_list(item: Node_MessageRecipientRule):
        """根据布尔值返回对应的星期列表"""
        week_list = []
        if item.monday:
            week_list.append('星期一')
        if item.tuesday:
            week_list.append('星期二')
        if item.wednesday:
            week_list.append('星期三')
        if item.thursday:
            week_list.append('星期四')
        if item.friday:
            week_list.append('星期五')
        if item.saturday:
            week_list.append('星期六')
        if item.sunday:
            week_list.append('星期日')
        return week_list

    if req.method != 'GET':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    group_id: int = req.GET.get('group_id')
    if not group_id:
        return ResponseJson({'status': -1, 'msg': "参数不完整"}, 400)
    if not node_group_id_exists(group_id):
        return ResponseJson({'status': 0, 'msg': '节点组不存在'})
    group = get_node_group_by_id(group_id)
    return ResponseJson({
        "status": 1,
        "data": {
            "group_id": group.id,
            "group_name": group.name,
            "group_leader": group.leader.userName,
            "group_desc": group.description,
            "node_list": [{
                'uuid': item.uuid,
                'name': item.name,
                'description': item.description,
                'leader': item.group.leader.userName,
            } for item in get_group_nodes(group)],
            "rules": [{
                'week': _get_week_list(item),
                'start_time': item.start_time.strftime("%H:%M"),
                'end_time': item.end_time.strftime("%H:%M"),
                'recipients': [user.userName for user in item.recipients.all()]
            } for item in group.time_slot_recipient.all()]
        }
    })
