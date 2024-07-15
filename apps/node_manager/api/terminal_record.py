# def get_terminal_record_list():
import os.path

from django.apps import apps
from django.http import HttpRequest, HttpResponse, FileResponse

from apps.node_manager.models import Node, Node_TerminalRecord
from apps.node_manager.utils.nodeUtil import node_uuid_exists, get_node_by_uuid
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import uid_exists, get_user_by_id
from util.Response import ResponseJson


def load_node_list(req: HttpRequest) -> HttpResponse:
    if req.method != "GET":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    temp = [{
        'name': item.name,
        'id': item.uuid,
        'node_type': "node_select",
        'children': []
    } for item in Node.objects.all()]
    return ResponseJson({
        'status': 1,
        'data': temp
    })


def load_terminal_user_list(req: HttpRequest) -> HttpResponse:
    if req.method != "GET":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    node_uuid = req.GET.get('node_uuid', None)
    if not node_uuid:
        return ResponseJson({
            "status": -1,
            "msg": "参数不完整"
        })
    if not node_uuid_exists(node_uuid):
        return ResponseJson({
            "status": 0,
            'msg': "节点不存在"
        })
    node = get_node_by_uuid(node_uuid)
    unique_users_with_records = Node_TerminalRecord.objects.filter(node=node).values('user').distinct()
    users = User.objects.filter(id__in=unique_users_with_records)
    temp = [{
        'name': user.userName,
        'id': {
            'node_uuid': node.uuid,
            'user_id': user.id
        },
        'node_type': 'user_select',
        'children': []
    } for user in users]
    return ResponseJson({
        "status": 1,
        'data': temp
    })


def load_terminal_session_list(req: HttpRequest) -> HttpResponse:
    if req.method != "GET":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    node_uuid = req.GET.get('node_uuid', None)
    user_id = req.GET.get('user_id', None)
    if not node_uuid or not user_id:
        return ResponseJson({
            "status": -1,
            "msg": "参数不完整"
        })
    if not node_uuid_exists(node_uuid):
        return ResponseJson({
            "status": 0,
            'msg': "节点不存在"
        })
    if not uid_exists(user_id):
        return ResponseJson({
            "status": 0,
            'msg': '用户不存在'
        })
    node = get_node_by_uuid(node_uuid)
    user = get_user_by_id(user_id)
    temp = [{
        'name': item.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'node_uuid': node_uuid,
        'id': {
            "node_uuid": node_uuid,
            "user_id": user_id,
            "session_uuid": item.session_id
        },
        'node_type': 'select_session'
    } for item in Node_TerminalRecord.objects.filter(node=node, user=user)]
    return ResponseJson({
        "status": 1,
        'data': temp
    })


def load_terminal_session_record(req: HttpRequest) -> HttpResponse | FileResponse:
    if req.method != "GET":
        return ResponseJson({"status": -1, "msg": "请求方式不正确"}, 405)
    node_uuid: str = req.GET.get('node_uuid', None)
    session_id: str = req.GET.get('session_uuid', None)
    if not node_uuid or not session_id:
        return ResponseJson({
            "status": -1,
            "msg": "参数不完整"
        })
    if not node_uuid_exists(node_uuid):
        return ResponseJson({
            "status": 0,
            'msg': "节点不存在"
        }, 404)
    node_record = os.path.join(apps.get_app_config('node_manager').terminal_record_save_dir, node_uuid)
    session_file = os.path.join(node_record, session_id + ".txt")
    if not os.path.exists(session_file):
        return ResponseJson({
            "status": 0,
            'msg': "会话不存在"
        }, 404)

    return FileResponse(open(session_file, 'rb'), as_attachment=True)
