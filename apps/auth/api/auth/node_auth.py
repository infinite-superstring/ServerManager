from django.apps import apps
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from apps.node_manager.models import Node, Node_BaseInfo
from apps.node_manager.utils.nodeUtil import verify_node_token
from util.Request import RequestLoadJson, getClientIp
from util.Response import ResponseJson
from util.logger import Log
from util.passwordUtils import encrypt_password

config = apps.get_app_config('setting').get_config

@require_POST
def node_auth(req: HttpRequest):
    """
    节点认证
    """
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
    if not (node and verify_node_token(node, node_token)):
        return ResponseJson({"status": 0, "msg": "节点认证失败"})
    if node.auth_restrictions_enable:
        match node.auth_restrictions_method:
            case 1:
                import ipaddress
                if ipaddress.ip_address('192.168.1.1').version != 4:
                    return ResponseJson({"status": 0, "msg": "暂不支持验证IPV6网段"})
                if str(ipaddress.ip_network(node_ip)) != node.auth_restrictions_value:
                    Log.warning(f"节点{node.name}({node.uuid})认证失败：网段错误，目标网段为{node.auth_restrictions_value}实际网段{ipaddress.ip_network(node_ip)}")
                    return ResponseJson({"status": 0, "msg": "节点认证失败"})
            case 2:
                if node_ip != node.auth_restrictions_value:
                    Log.warning(f"节点{node.name}({node.uuid})认证失败：IP错误，目标IP为{node.auth_restrictions_value}实际IP{node_ip}")
                    return ResponseJson({"status": 0, "msg": "节点认证失败"})
            case 3:
                # TODO MAC验证未实现
                pass
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

