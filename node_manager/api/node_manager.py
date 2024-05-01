import secrets

from audit.util.auditTools import write_audit
from node_manager.models import Node
from node_manager.utils.tagUtil import add_tags
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from util.passwordUtils import PasswordToMd5


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
                token = secrets.token_hex(64)

                node = Node.objects.create(
                    name=node_name,
                    description=node_description,
                    token=PasswordToMd5(token),
                )
                if node_tags is not None:
                    tags = add_tags(node_tags)
                    for tag in tags:
                        node.tags.add(tag)
                node.save()
                write_audit()
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
            node_id = req_json.get('id')
            if node_id is None:
                return ResponseJson({"status": -1, "msg": "参数不完整"})
            if Node.objects.filter(id=node_id).exists():
                Node.objects.filter(id=node_id).delete()
                return ResponseJson({"status": 1, "msg": "节点已删除"})
            else:
                return ResponseJson({"status": 0, "msg": "节点不存在"})

    else:
        return ResponseJson({"status": -1, "msg": "请求方式不正确"})


def reset_node_token(req):
    """重置节点Token"""


def edit_node(req):
    """编辑节点"""


def get_node_list(req):
    """获取节点列表"""


def get_node_info(req):
    """获取节点信息"""
