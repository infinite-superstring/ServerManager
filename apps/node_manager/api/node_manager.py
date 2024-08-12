import secrets
from typing import Callable

from django.apps import apps

from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from tempfile import NamedTemporaryFile

from apps.audit.util.auditTools import write_audit, write_access_log
from apps.group.manager.models import Node_Group
from apps.node_manager.entity.auth_restrictions import AuthRestrictions
from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.groupUtil import get_node_group_by_id, node_group_id_exists
from apps.node_manager.utils.nodeUtil import get_node_by_uuid, node_uuid_exists, node_name_exists, \
    init_node_alarm_setting, filter_user_available_nodes, is_node_available_for_user, get_import_node_list_excel_object
from apps.node_manager.utils.searchUtil import extract_search_info
from apps.node_manager.utils.tagUtil import add_tags, get_node_tags
from apps.auth.utils.otpUtils import verify_otp_for_request
from apps.permission_manager.util.api_permission import api_permission
from apps.permission_manager.util.permission import groupPermission
from apps.user_manager.util.userUtils import get_user_by_id
from util import uploadFile
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.asgi_file import get_file_response
from util.listUtil import is_exist_by_double_list_index
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from util.passwordUtils import encrypt_password
from apps.setting.entity.Config import config
from util.excelUtils import *

config: Callable[[], config] = apps.get_app_config('setting').get_config
FILE_SAVE_BASE_PATH = os.path.join(os.getcwd(), "data", "temp", "import_node_list")

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


@require_POST
@api_permission("editNode")
def add_node(req):
    """添加节点"""
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    node_name = req_json.get('node_name')
    node_description = req_json.get('node_description')
    node_tags = req_json.get('node_tags')
    node_group = req_json.get('node_group')
    auth_restrictions: dict = req_json.get('node_auth_restrictions')
    uid = req.session['userID']
    user = get_user_by_id(uid)
    if not node_name and not auth_restrictions:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    auth_restrictions: AuthRestrictions = AuthRestrictions(
        auth_restrictions.get("enable"),
        auth_restrictions.get("method"),
        auth_restrictions.get("value")
    )
    if auth_restrictions.enable and (not auth_restrictions.method or not auth_restrictions.value):
        if not auth_restrictions.method: return ResponseJson({"status": 0, 'msg': "认证限制类型未填写"})
        if not auth_restrictions.value: return ResponseJson({"status": 0, "msg": "认证限制值未填写"})
        return ResponseJson({"status": 0, "msg": "未知错误"})
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
        creator=user,
        auth_restrictions_enable=auth_restrictions.enable,
        auth_restrictions_method=auth_restrictions.method if auth_restrictions.enable else None,
        auth_restrictions_value=auth_restrictions.value if auth_restrictions.enable else None,
    )
    if node_group:
        node.group = get_node_group_by_id(node_group)
    if node_tags is not None:
        tags = add_tags(node_tags)
        for tag in tags:
            node.tags.add(tag)
    node.save()
    init_node_alarm_setting(node)
    server_token = config().base.server_token
    write_audit(req.session['userID'], "创建节点", "节点管理", f"UUID: {node.uuid} 节点名：{node.name}")
    return ResponseJson({
        "status": 1,
        "msg": "节点创建成功",
        "data": {
            "node_name": node.name,
            "token": token,
            'server_token': server_token,
        }})


@require_POST
@api_permission("editNode")
def del_node(req):
    """删除节点"""
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
        write_audit(req.session['userID'], "删除节点", "节点管理", f"UUID: {node_id}")
        return ResponseJson({"status": 1, "msg": "节点已删除"})
    else:
        return ResponseJson({"status": 0, "msg": "节点不存在"})


@require_POST
@api_permission("editNode")
def reset_node_token(req):
    """重置节点Token"""
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
    if not group_utils.check_group_permission("viewAllNode") and not is_node_available_for_user(user, node):
        return ResponseJson({'status': 0, 'msg': "当前无权限操作该节点"})
    token = secrets.token_hex(32)
    hashed_token, salt = encrypt_password(token)
    node.token_hash = hashed_token
    node.token_salt = salt
    node.save()
    server_token = config().base.server_token
    write_audit(req.session['userID'], "重置节点Token", "节点管理", f"UUID: {node.uuid}")
    return ResponseJson({
        "status": 1,
        "msg": "Token重置成功",
        "data": {
            "token": token,
            'server_token': server_token,
        }
    })


@require_POST
def get_node_list(req):
    """获取节点列表"""
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
    write_access_log(req.session["userID"], req, "节点管理",
                     f"获取节点列表(搜索条件: {search if search else '无'} 页码: {page} 页大小: {pageSize})")
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), pageSize),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
def get_base_node_list(req):
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
    write_access_log(req.session["userID"], req, "节点管理",
                     f"获取节点列表-基础(搜索条件: {search if search else '无'} 页码: {page} 页大小: {pageSize})")
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), 20),
            "currentPage": page,
            "PageContent": PageContent
        }
    })


@require_POST
def get_node_info(req):
    """获取节点信息"""
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
    write_access_log(req.session["userID"], req, "节点管理", f"获取节点信息：{node.name}(uuid: {node.uuid})")
    return ResponseJson({
        "status": 1,
        "data": {
            "node_uuid": node.uuid,
            "node_name": node.name,
            "node_desc": node.description,
            "node_group": {"group_id": node.group.id, "group_name": node.group.name} if node.group else None,
            "node_tags": list(get_node_tags(node.uuid)),
            "auth_restrictions": {
                "enable": node.auth_restrictions_enable,
                "method": node.auth_restrictions_method,
                "value": node.auth_restrictions_value,
            }
        }
    })


@require_POST
@api_permission("editNode")
def edit_node(req):
    """编辑节点"""
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
    if not node_group and node.group is not None:
        node.group = None
    if node_tags is not None and node_tags != list(get_node_tags(node.uuid)):
        tags_obj = add_tags(node_tags)
        node.tags.clear()
        node.tags.add(*tags_obj)
    node.save()
    audit_msg = f"节点名：{node.name}({node.uuid})"
    if node.group:
        audit_msg += f"集群归属：{node.group.name}(gid: {node.group.id})"
    write_audit(req.session['userID'], "编辑节点", "节点管理", audit_msg)
    return ResponseJson({
        "status": 1,
        "msg": "节点信息保存成功",
        # "data": {
        #     "uuid": node.uuid,
        #     "name": node.name,
        #     "description": node.description,
        #     "group": node.group.id if node.group else None,
        #     "group_name": node.group.name if node.group else None,
        #     "tags": list(get_node_tags(node.uuid)),
        #
        # }
    })


@api_permission("editNode")
@require_GET
def download_node_table_template(req):
    from tempfile import NamedTemporaryFile
    eutils: ExcelUtils = get_import_node_list_excel_object()
    with NamedTemporaryFile(delete=False) as tmp:
        eutils.createExcelTemplate(tmp.name)
        return get_file_response(tmp.name, "节点导入模板.xlsx")


@api_permission("editNode")
@require_POST
def upload_node_list_file_chunk(req):
    """
    上传节点列表文件块
    """
    return uploadFile.upload_chunk(req)


@api_permission("editNode")
@require_POST
def merge_node_list_file(req):
    """
    合并节点列表文件块并解析
    """
    user = get_user_by_id(req.session["userID"])
    if not os.path.exists(FILE_SAVE_BASE_PATH):
        os.makedirs(FILE_SAVE_BASE_PATH)
    merge_status, hash256 = uploadFile.merge_chunks(req, FILE_SAVE_BASE_PATH)
    if not merge_status:
        return ResponseJson({'status': 0, "msg": "文件上传失败"})
    eutils: ExcelUtils = get_import_node_list_excel_object()
    try:
        eutils.loadExcel(os.path.join(FILE_SAVE_BASE_PATH, hash256))
    except Exception as e:
        Log.error(e)
        return ResponseJson({'status': 0, 'msg': '表格解析失败'})
    datas = []
    errors = []
    error_msgs = []
    node_list_table = eutils.tables.get("节点列表")
    for index, row in enumerate(node_list_table.rows):
        data = []
        # 检查节点名
        if not row.error[0]:
            if node_name_exists(row.data[0]):
                row.error[0] = True
                row.error_message[0] = f"节点 {row.data[0]} 已存在"
            elif is_exist_by_double_list_index(datas, 0, row.data[0]):
                row.error[0] = True
                row.error_message[0] = f"节点 {row.data[0]} 已重复"
        # 切分节点tag
        if not row.error[1] and row.data[1]:
            row.data[1] = str(row.data[1]).split(",")
        datas.append(row.data)
        errors.append(row.error)
        error_msgs.append(row.error_message)
    return ResponseJson({'status': 1, "data": {
        "results": {
            "col_names": [col.column_name for col in node_list_table.cols],
            "datas": datas,
            "errors": errors,
            "error_msgs": error_msgs,
        }
    }})