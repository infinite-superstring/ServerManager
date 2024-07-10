from django.apps import apps
from django.http import HttpRequest

from apps.node_manager.models import Node, Node_BaseInfo
from apps.node_manager.utils.nodeUtil import verify_node_token
from util.Request import RequestLoadJson, getClientIp
from util.Response import ResponseJson
from util.logger import Log
from util.passwordUtils import encrypt_password

config = apps.get_app_config('setting').get_config

def node_auth(req: HttpRequest):
    """
    节点认证
    """
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方法不正确"}, 405)
    try:
        req_json = RequestLoadJson(req)
        Log.debug(str(req_json))
    except:
        return ResponseJson({"status": -1, "msg": "Json解析失败"}, 400)
    node_name = req_json.get("node_name")  # 节点名
    node_token = req_json.get("node_token")  # 节点Token
    node_ip = getClientIp(req)  # 节点认证时IP地址
    if not (node_name or node_token or node_ip):
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    if not Node.objects.filter(name=node_name).exists():
        return ResponseJson({"status": 0, "msg": "节点不存在"})
    node = Node.objects.get(name=node_name)
    if (node and verify_node_token(node, node_token)):
        req.session["node_uuid"] = str(node.uuid)
        req.session["node_name"] = node.name
        req.session["auth_method"] = "Node Auth"
        req.session.set_expiry = 0
        if not Node_BaseInfo.objects.filter(node=node).exists():
            Node_BaseInfo.objects.create(node=node, node_version="")

        hashed_token, salt = encrypt_password(config().base.server_token)

        return ResponseJson({"status": 1, "data": {
            'server_token': {
                'hash': str(hashed_token),
                'salt': salt
            },
            'server_name': config().base.website_name,
        }})
    else:
        return ResponseJson({"status": 0, "msg": "节点认证失败"})
