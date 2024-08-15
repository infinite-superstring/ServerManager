from django.views.decorators.http import require_POST, require_GET

from apps.audit.util.auditTools import write_audit, write_access_log
from apps.group.manager.models import Node_Group, Group_User_Permission
from apps.group.manager.utils.groupUtil import create_node_group_user_permission_rules, node_group_id_exists, \
    get_node_group_by_id, get_group_nodes
from apps.node_manager.utils.nodeUtil import node_uuid_exists, node_set_group, node_remove_group
from apps.permission_manager.util.api_permission import api_permission
from apps.user_manager.util.userUtils import uid_exists, get_user_by_id
from apps.auth.utils.otpUtils import verify_otp_for_request
from util import result
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from django.http.request import HttpRequest


@require_POST
@api_permission("editNodeGroup")
def get_group_list(req: HttpRequest):
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    PageContent: list = []
    page = req_json.get("page", 1)
    pageSize = req_json.get("pageSize", 20)
    search = req_json.get("search", "")
    result = Node_Group.objects.filter(name__icontains=search if search else "")
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "group_id": item.get("id"),
                "group_name": item.get("name"),
                "group_leader": get_user_by_id(item.get("leader_id")).userName,
                "group_desc": item.get("description"),
            })
    write_access_log(req.session["userID"], req, "集群管理",
                     f"获取集群列表(搜索条件: {search if search else '无'} 页码: {page} 页大小: {pageSize})")
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
@api_permission("editNodeGroup")
def create_group(req: HttpRequest):
    """创建组"""
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
    if not (group_name and group_leader):
        return ResponseJson({'status': -1, 'msg': '参数不完整'})
    if Node_Group.objects.filter(name=group_name).exists():
        return ResponseJson({"status": 0, "msg": "集群已存在"})
    if not uid_exists(group_leader):
        return ResponseJson({'status': 0, 'msg': '负责人不存在'})
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
    if group_nodes:
        rules = create_node_group_user_permission_rules(rules)
        for rule in rules:
            group.user_permission.add(rule)
    write_audit(req.session['userID'], "创建集群", "集群管理", f"集群：{group.name}(gid: {group.id})")
    return ResponseJson({'status': 1, 'msg': '创建集群成功'})


@require_POST
@api_permission("editNodeGroup")
def del_group(req: HttpRequest):
    """删除组"""
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    group_id: int = req_json.get('group_id')
    code = req_json.get('code')
    if not group_id or code is None:
        return ResponseJson({'status': -1, 'msg': "参数不完整"}, 400)
    if not verify_otp_for_request(req, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    if not node_group_id_exists(group_id):
        return ResponseJson({'status': 0, 'msg': '集群不存在'})
    group = get_node_group_by_id(group_id)
    nodes = get_group_nodes(group)
    for node in nodes:
        node.group = None
        node.save()
    for rule in group.user_permission.all():
        group.user_permission.remove(rule)
        rule.delete()
    group.delete()
    write_audit(req.session['userID'], "删除集群", "集群管理", f"gid: {group_id}")
    return ResponseJson({'status': 1, 'msg': '删除集群成功'})


@require_POST
@api_permission("editNodeGroup")
def edit_group(req: HttpRequest):
    """编辑组"""


@require_GET
@api_permission("editNodeGroup")
def get_group_by_id(req: HttpRequest):
    """获取组详细"""

    def _get_week_list(item: Group_User_Permission):
        """根据布尔值返回对应的星期列表"""
        week_list = []
        if item.monday:
            week_list.append({"title": "星期一", "value": "monday"})
        if item.tuesday:
            week_list.append({"title": "星期二", "value": "tuesday"})
        if item.wednesday:
            week_list.append({"title": "星期三", "value": "wednesday"})
        if item.thursday:
            week_list.append({"title": "星期四", "value": "thursday"})
        if item.friday:
            week_list.append({"title": "星期五", "value": "friday"})
        if item.saturday:
            week_list.append({"title": "星期六", "value": "saturday"})
        if item.sunday:
            week_list.append({"title": "星期日", "value": "sunday"})
        return week_list

    group_id: int = req.GET.get('group_id')
    if not group_id:
        return ResponseJson({'status': -1, 'msg': "参数不完整"}, 400)
    if not node_group_id_exists(group_id):
        return ResponseJson({'status': 0, 'msg': '节点组不存在'})
    group = get_node_group_by_id(group_id)
    write_access_log(req.session["userID"], req, "集群管理", f"获取集群信息：{group.name}(gid: {group.id})")
    r = {
        "group_id": group.id,
        "group_name": group.name,
        "group_leader": {
            "id": group.leader.id,
            "userName": group.leader.userName
        },
        "group_desc": group.description,
        "node_list": [{
            'uuid': item.uuid,
            'name': item.name,
        } for item in get_group_nodes(group)],
        "rules": [{
            'week': _get_week_list(item),
            'start_time': item.start_time.strftime("%H:%M"),
            'end_time': item.end_time.strftime("%H:%M"),
            'users': [{
                "id": user.id,
                "userName": user.userName
            } for user in item.user_list.all()]
        } for item in group.user_permission.all()]
    }
    return result.success(r)


@require_POST
@api_permission("editNodeGroup")
def editNodeGroup(req: HttpRequest):
    """编辑组"""
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return result.api_error("JSON解析失败")
    group_id: int = req_json.get('group_id')
    group_name: str = req_json.get('group_name')
    group_desc: str = req_json.get('group_desc')
    group_leader: int = req_json.get('group_leader')
    group_nodes: list = req_json.get('group_nodes')
    rules: list = req_json.get('rules')
    if not (group_id and group_name and group_leader):
        return result.api_error("参数不完整")
    if not node_group_id_exists(group_id):
        return result.api_error("集群不存在")
    if not uid_exists(group_leader):
        return result.api_error("负责人不存在")
    group = get_node_group_by_id(group_id)
    if group.name != group_name:
        group.name = group_name
    if group.description != group_desc:
        group.description = group_desc
    if group.leader.id != group_leader:
        group.leader = get_user_by_id(group_leader)
    if not group_nodes:
        return result.api_error("节点列表不能为空")
    if group_nodes:
        for node in get_group_nodes(group):
            node_remove_group(node.uuid)
        for node in group_nodes:
            node_set_group(node.get('uuid'), group.id)
    group.name = group_name
    group.user_permission.all().delete()
    permission_rules = create_node_group_user_permission_rules(rules)
    for rule in permission_rules:
        group.user_permission.add(rule)
    group.save()
    return result.success(msg="编辑成功")
