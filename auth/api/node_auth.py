from node_manager.models import Node, Node_BaseInfo
from node_manager.utils.nodeUtil import verify_node_token
from util.Request import RequestLoadJson, getClientIp
from util.Response import ResponseJson


def node_auth(req):
    """
    节点认证
    """
    if req.session.get("user"):
        return ResponseJson({"status": 1, "msg": "当前账户已登录"})
    if not req.method == 'POST':
        return ResponseJson({"status": -1, "msg": "请求方法不正确"})
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        return ResponseJson({"status": -1, "msg": "Json解析失败"})
    else:
        node_name = req_json.get("node_name")  # 节点名
        node_token = req_json.get("node_token")  # 节点Token
        node_ip = getClientIp(req)  # 节点认证时IP地址
        server_token = req_json.get("server_token")  # 服务器Token
        if not node_name or node_token or node_ip or server_token:
            return ResponseJson({"status": -1, "msg": "参数不完整"})
        node = Node.objects.get(name=node_name)
        if node and verify_node_token(node, node_token):
            req.session["node_uuid"] = node.uuid
            req.session["node_name"] = node.name
            req.session["authMethod"] = "Node Auth"
            if not Node_BaseInfo.objects.filter(node=node).exists():
                Node_BaseInfo.objects.create(node=node, online=True)
            else:
                Node_BaseInfo.objects.get(node=node).update(online=True)
            return ResponseJson({"status": 1, "msg": "节点认证成功"})
        else:
            return ResponseJson({"status": 0, "msg": "节点认证失败"})