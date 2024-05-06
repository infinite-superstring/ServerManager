from node_manager.models import Node, Node_BaseInfo
from util.passwordUtils import verify_password


def verify_node_token(node: Node, token):
    """
    验证节点Token
    """
    if not isinstance(node, Node):
        return False

    return verify_password(node.token_hash, token, node.token_salt)

def refresh_node_info(node: Node, data):
    node_info = Node_BaseInfo(node=node)

