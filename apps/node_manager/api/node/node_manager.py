import secrets

from django.db.models import Q

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.groupUtil import get_node_group_by_id, node_group_id_exists
from apps.node_manager.utils.nodeUtil import get_node_by_uuid, node_uuid_exists, node_name_exists, \
    init_node_alarm_setting, filter_user_available_nodes, is_node_available_for_user
from apps.node_manager.utils.searchUtil import extract_search_info
from apps.node_manager.utils.tagUtil import add_tags, get_node_tags
from apps.auth.utils.otpUtils import verify_otp_for_request
from apps.permission_manager.util.permission import groupPermission
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from util.passwordUtils import encrypt_password


def __advanced_search(search: str):
    """
    高级搜索节点列表
    """
    normal_search_info, tags, groups, status = extract_search_info(search)
    query = Q(name__icontains=normal_search_info) if search else Q()
    # 如果tags非空，则添加tags的过滤条件
    if tags:
        query &= Q(tags__tag_name__in=tags)
    # 如果groups非空，则添加groups的过滤条件
    if groups:
        query &= Q(group__name__in=groups)
    # 搜索节点状态
    match status:
        case "online":
            query |= Q(node_baseinfo__online=True)
        case "offline":
            query |= Q(node_baseinfo__online=False)
        case "uninitialized":
            query |= Q(node_baseinfo__online=None)
        case "warning":
            query |= Q(node_event__level__in=["Warning", "Error"], node_event__end_time=None)
    return Node.objects.filter(query)


def add_node(req):
    """添加节点"""
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_name = req_json.get('node_name')
    node_description = req_json.get('node_description')
    node_tags = req_json.get('node_tags')
    node_group = req_json.get('node_group')
    uid = req.session['userID']
    user = get_user_by_id(uid)
    if not node_name:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if node_name_exists(node_name):
        return ResponseJson({"status": 0, "msg": "节点已存在"})
    if node_group and not node_group_id_exists(node_group):
        return ResponseJson({'status': 0, 'msg': '节点组不存在'})
    token = secrets.token_hex(32)
    hashed_token, salt = encrypt_password(token)
    node = Node.objects.create(
        name=node_name,
        description=node_description,
        token_hash=hashed_token,
        token_salt=salt,
        creator=user
    )
    if node_group:
        node.group = get_node_group_by_id(node_group)
    if node_tags is not None:
        tags = add_tags(node_tags)
        for tag in tags:
            node.tags.add(tag)
    node.save()
    init_node_alarm_setting(node)
    return ResponseJson({
        "status": 1,
        "msg": "节点创建成功",
        "data": {
            "node_name": node.name,
            "token": token
        }})


def del_node(req):
    """删除节点"""
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_id = req_json.get('uuid')
    code = req_json.get('code')
    if not node_id or code is None:
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    if not verify_otp_for_request(req, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    if node_uuid_exists(node_id):
        uid = req.session['userID']
        user = get_user_by_id(uid)
        group_utils = groupPermission(user.permission)
        node = get_node_by_uuid(node_id)
        if not group_utils.check_group_permission("viewAllNode") and not is_node_available_for_user(user, node):
            return ResponseJson({'status': 0, 'msg': "当前无权限操作该节点"})
        node.delete()
        return ResponseJson({"status": 1, "msg": "节点已删除"})
    else:
        return ResponseJson({"status": 0, "msg": "节点不存在"})


def reset_node_token(req):
    """重置节点Token"""
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_id = req_json.get('uuid')
    code = req_json.get('code')
    uid = req.session['userID']
    user = get_user_by_id(uid)
    group_utils = groupPermission(user.permission)
    if node_id is None or code is None:
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    if not verify_otp_for_request(req, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    if not node_uuid_exists(node_id):
        return ResponseJson({"status": 0, "msg": "节点不存在"})
    node = get_node_by_uuid(node_id)
    # if not group_utils.check_group_permission("viewAllNode") and node.creator != user:
    #     return ResponseJson({'status': 0, 'msg': "无权限:无法删除他人的节点"})
    if not group_utils.check_group_permission("viewAllNode") and not is_node_available_for_user(user, node):
        return ResponseJson({'status': 0, 'msg': "当前无权限操作该节点"})
    token = secrets.token_hex(32)
    hashed_token, salt = encrypt_password(token)
    node.token_hash = hashed_token
    node.token_salt = salt
    node.save()
    return ResponseJson({
        "status": 1,
        "msg": "Token重置成功",
        "data": {
            "token": token
        }
    })


def get_node_list(req):
    """获取节点列表"""
    if not req.method == 'POST':
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
    uid = req.session['userID']
    user = get_user_by_id(uid)
    group_utils = groupPermission(user.permission)
    result = __advanced_search(search)
    if not group_utils.check_group_permission("viewAllNode"):
        result = filter_user_available_nodes(user, result)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            node = Node.objects.get(uuid=item.get("uuid"))
            node_base_info = Node_BaseInfo.objects.filter(node=node).first()
            node_usage = Node_UsageData.objects.filter(node=node).last()
            online = node_base_info.online if node_base_info else False
            try:
                memory_used = round((node_usage.memory_used / node_base_info.memory_total) * 100, 1)
            except:
                memory_used = 0
            PageContent.append({
                "uuid": item.get("uuid"),
                "name": item.get("name"),
                "description": item.get("description"),
                "group": get_node_group_by_id(item.get("group_id")).name if item.get("group_id") else None,
                "tags": get_node_tags(item.get("uuid")),
                "creator": get_user_by_id(item.get("creator_id")).userName if item.get("creator_id") else None,
                "baseData": {
                    "platform": node_base_info.system if node_base_info else "未知",
                    "hostname": node_base_info.hostname if node_base_info else "未知",
                    "online": online,
                    "cpu_usage": f"{node_usage.cpu_usage if node_usage else 0}%",
                    "memory_used": f"{memory_used}%" if online and node_base_info.memory_total else "0%",
                }
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), pageSize),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


def get_base_node_list(req):
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
    uid = req.session['userID']
    user = get_user_by_id(uid)
    group_utils = groupPermission(user.permission)
    result = __advanced_search(search)
    if not group_utils.check_group_permission("viewAllNode"):
        result = filter_user_available_nodes(user, result)
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                "uuid": item.get("uuid"),
                "name": item.get("name"),
                "group": True if item.get("group_id") else False,
            })
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


def get_node_info(req):
    """获取节点信息"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_id = req_json.get("uuid")
    if node_id is None:
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    if not node_uuid_exists(node_id):
        return ResponseJson({"status": 0, "msg": "节点不存在"})
    uid = req.session['userID']
    user = get_user_by_id(uid)
    group_utils = groupPermission(user.permission)
    node = get_node_by_uuid(node_id)
    if not group_utils.check_group_permission("viewAllNode") and not is_node_available_for_user(user, node):
        return ResponseJson({'status': 0, 'msg': "当前无权限操作该节点"})
    return ResponseJson({
        "status": 1,
        "data": {
            "node_uuid": node.uuid,
            "node_name": node.name,
            "node_desc": node.description,
            "node_group": node.group.id if node.group else None,
            "group_name": node.group.name if node.group else None,
            "node_tags": list(get_node_tags(node.uuid)),
        }
    })


def edit_node(req):
    """编辑节点"""
    if req.method != 'POST':
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_id = req_json.get("node_uuid")
    node_name = req_json.get("node_name")
    node_description = req_json.get("node_desc")
    node_group = req_json.get("node_group")
    node_tags = req_json.get("node_tags")
    if node_id is None:
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    if not node_uuid_exists(node_id):
        return ResponseJson({"status": 0, "msg": "节点不存在"})
    uid = req.session['userID']
    user = get_user_by_id(uid)
    group_utils = groupPermission(user.permission)
    node = get_node_by_uuid(node_id)
    if not group_utils.check_group_permission("viewAllNode") and not is_node_available_for_user(user, node):
        return ResponseJson({'status': 0, 'msg': "当前无权限操作该节点"})
    if node_name is not None and node_name != node.name:
        node.name = node_name
    if node_description is not None and node_description != node.description:
        node.description = node_description
    if node_group is not None and node_group != node.group:
        if node_group_id_exists(node_group):
            node.group = get_node_group_by_id(node_group)
        else:
            Log.warning(f"Node Group Id: {node_group} is not exist")
    if node_tags is not None and node_tags != list(get_node_tags(node.uuid)):
        tags_obj = add_tags(node_tags)
        node.tags.clear()
        node.tags.add(*tags_obj)
    node.save()
    return ResponseJson({
        "status": 1,
        "msg": "节点信息保存成功",
        "data": {
            "uuid": node.uuid,
            "name": node.name,
            "description": node.description,
            "group": node.group.id if node.group else None,
            "group_name": node.group.name if node.group else None,
            "tags": list(get_node_tags(node.uuid)),
        }
    })
