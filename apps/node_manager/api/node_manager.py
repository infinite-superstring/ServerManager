import secrets

from django.db.models import Q

from apps.node_manager.models import Node, Node_BaseInfo, Node_UsageData
from apps.node_manager.utils.searchUtil import extract_search_info
from apps.node_manager.utils.tagUtil import add_tags, get_node_tags
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from util.passwordUtils import encrypt_password


def add_node(req):
    """添加节点"""
    if req.method == 'POST':
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": "JSON解析失败"})
        else:
            node_name = req_json.get('node_name')
            node_description = req_json.get('node_description')
            node_tags = req_json.get('node_tags')
            node_group = req_json.get('node_group')
            if node_name is not None:
                if Node.objects.filter(name=node_name).exists():
                    return ResponseJson({"status": 0, "msg": "节点已存在"})
                token = secrets.token_hex(32)
                hashed_token, salt = encrypt_password(token)
                node = Node.objects.create(
                    name=node_name,
                    description=node_description,
                    token_hash=hashed_token,
                    token_salt=salt,
                )
                if node_tags is not None:
                    tags = add_tags(node_tags)
                    for tag in tags:
                        node.tags.add(tag)
                node.save()
                # write_audit()
                return ResponseJson({
                    "status": 1,
                    "msg": "节点创建成功",
                    "data": {
                        "node_name": node.name,
                        "token": token
                    }})
            else:
                return ResponseJson({"status": -1, "msg": "参数不完整"})

    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})


def del_node(req):
    """删除节点"""
    if req.method == 'POST':
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": "JSON解析失败"})
        else:
            node_id = req_json.get('uuid')
            if node_id is None:
                return ResponseJson({"status": -1, "msg": "参数不完整"})
            if Node.objects.filter(uuid=node_id).exists():
                Node.objects.filter(uuid=node_id).delete()
                return ResponseJson({"status": 1, "msg": "节点已删除"})
            else:
                return ResponseJson({"status": 0, "msg": "节点不存在"})

    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})


def reset_node_token(req):
    """重置节点Token"""
    if req.method == 'POST':
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": "JSON解析失败"})
        else:
            node_id = req_json.get('uuid')
            if node_id is None:
                return ResponseJson({"status": -1, "msg": "参数不完整"})
            if Node.objects.filter(uuid=node_id).exists():
                token = secrets.token_hex(32)
                node = Node.objects.get(uuid=node_id)
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
            else:
                return ResponseJson({"status": 0, "msg": "节点不存在"})

    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})


def edit_node(req):
    """编辑节点"""


def get_node_list(req):
    """获取节点列表"""
    if req.method == 'POST':
        try:
            req_json = RequestLoadJson(req)
        except Exception as e:
            Log.error(e)
            return ResponseJson({"status": -1, "msg": "JSON解析失败"})
        else:
            PageContent: list = []
            page = req_json.get("page", 1)
            pageSize = req_json.get("pageSize", 20)
            search = req_json.get("search", "")
            normal_search_info, tags, groups = extract_search_info(search)
            query = Q(name__icontains=normal_search_info) if search else Q()
            # 如果tags非空，则添加tags的过滤条件
            if tags:
                query &= Q(tags__tag_name__in=tags)
            # 如果groups非空，则添加groups的过滤条件
            if groups:
                query &= Q(group__name__in=groups)

            result = Node.objects.filter(query)
            pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
            if pageQuery:
                for item in pageQuery:
                    node = Node.objects.get(uuid=item.get("uuid"))
                    node_base_info = Node_BaseInfo.objects.filter(node=node).first()
                    node_usage = Node_UsageData.objects.filter(node=node).last()
                    online = node_base_info.online if node_base_info else False
                    PageContent.append({
                        "uuid": item.get("uuid"),
                        "name": item.get("name"),
                        "description": item.get("description"),
                        "tags": get_node_tags(item.get("uuid")),
                        "baseData": {
                            "platform": node_base_info.system if node_base_info else "未知",
                            "hostname": node_base_info.hostname if node_base_info else "未知",
                            "online": online,
                            "cpu_usage": f"{node_usage.cpu_usage if node_usage else 0}%",
                            "memory_used": f"{round((node_usage.memory_used / node_base_info.memory_total) * 100, 1)}%" if online and node_base_info else "0%",
                        }
                    })
            return ResponseJson({
                "status": 1,
                "data": {
                    "maxPage": get_max_page(result.all().count(), 20),
                    "currentPage": page,
                    "PageContent": PageContent
                }
            })
    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})



def get_node_info(req):
    """获取节点信息"""
