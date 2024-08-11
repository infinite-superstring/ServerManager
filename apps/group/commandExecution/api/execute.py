import os.path
from typing import Callable

from django.apps import apps
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET

from apps.audit.util.auditTools import write_audit
from apps.auth.utils.otpUtils import verify_otp_for_request
from apps.group.commandExecution.models import Cluster_Execute, Cluster_ExecuteResult
from apps.group.commandExecution.utils.group_command_util import executeGroupCommand
from apps.group.group_task.utils import group_task_util
from apps.group.group_task.utils.group_task_util import is_uuid
from apps.node_manager.models import Node
from apps.node_manager.utils.groupUtil import get_node_group_by_id
from apps.node_manager.utils.groupUtil import node_group_id_exists
from apps.permission_manager.util.permission import groupPermission
from apps.setting.entity.Config import config
from apps.user_manager.util.userUtils import get_user_by_id
from util import result, file_util
from util.Request import RequestLoadJson
from util.file_util import SizeType
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from util.result import api_error, error, success, file

config: Callable[[], config] = apps.get_app_config('setting').get_config


@require_POST
def createTask(request: HttpRequest) -> HttpResponse:
    """
    创建Shell执行任务
    """
    try:
        req_json = RequestLoadJson(request)
    except Exception as e:
        Log.error(e)
        return api_error("JSON解析失败")
    uid = request.session['userID']
    user = get_user_by_id(uid)
    group = req_json.get('node_group')
    base_path = req_json.get('base_path')
    shell = req_json.get('shell')
    Log.debug(f"group: {group}, base_path: {base_path}, shell: {shell}")
    if not group or not shell:
        return api_error("参数不完整")
    group = get_node_group_by_id(group)
    if not node_group_id_exists(group.id):
        return error("节点组不存在")
    command_list = config().terminal_audit.disable_command_list
    gp = groupPermission(get_user_by_id(request.session.get("userID")).permission)
    if not gp.is_superuser() and not group_task_util.command_legal(shell, command_list.split("\n")):
        return error("禁用命令不可执行")
    task = Cluster_Execute.objects.create(
        group=group,
        user=user,
        base_path=base_path,
        shell=shell
    )
    # g_util = GroupUtil(group)
    # g_util.send_event_to_all_nodes("run_shell", {
    #     'task_uuid': str(task.uuid),
    #     "shell": shell,
    #     'base_path': base_path
    # })
    executeGroupCommand(task)
    write_audit(request.session['userID'], "创建执行器", "集群命令",
                f"集群：{group.name}(gid: {group.id}) 运行目录：{base_path if base_path else 'Default'} shell: {shell}")
    return success()


@require_GET
def getResultList(request: HttpRequest) -> HttpResponse:
    """
    获取Shell执行返回列表
    """
    PageContent: list = []
    page = int(request.GET.get("page", 1))
    pageSize = int(request.GET.get("pageSize", 20))
    result = Cluster_Execute.objects.all()
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                'uuid': item.get("uuid"),
                'user': get_user_by_id(item.get("user_id")).userName,
                'group': get_node_group_by_id(item.get("group_id")).name,
                'shell': str(item.get("shell"))[:10] if len(item.get("shell")) > 10 else item.get("shell"),
                'timestamp': item.get("timestamp"),
            })
    return success({
        "maxPage": get_max_page(result.all().count(), pageSize),
        "currentPage": page,
        "PageContent": PageContent
    })


@require_GET
def getResult(request: HttpRequest) -> HttpResponse:
    """
    获取Shell执行返回
    """

    r_uuid = request.GET.get("uuid")
    if not r_uuid:
        return error("uuid不能为空")
    if not is_uuid(r_uuid):
        return error("参数错误")
    save_dir = apps.get_app_config('node_manager').group_command_result_save_dir
    file_path = os.path.join(save_dir, r_uuid)
    too_big = file_util.file_to_size(str(file_path), SizeType.MB) > 3
    lines = file_util.read_text_file(file_path=str(file_path),
                                     encoding=file_util.file_encode(str(file_path)),
                                     read_lines=4000, is_asc=False) if too_big else \
        file_util.read_text_file(file_path=str(file_path), encoding=file_util.file_encode(str(file_path)))
    return success({
        "tooBig": too_big,
        "lines": lines
    })


@require_GET
def getNodeResultList(request: HttpRequest) -> HttpResponse:
    """
    根据指令UUID获取节点运行结果列表
    """
    uuid = request.GET.get("uuid")
    if not uuid:
        result.error("uuid不能为空")
    cluster_execute: Cluster_Execute = Cluster_Execute.objects.filter(uuid=uuid).first()
    if not cluster_execute:
        return error("指令不存在")
    group = cluster_execute.group
    nodes = Node.objects.filter(group=group)
    have_nodes = Cluster_ExecuteResult.objects.filter(node__uuid__in=[node.uuid for node in nodes],
                                                      task=cluster_execute)
    result_list = []
    for node in nodes:
        is_success = node.uuid in [item.node.uuid for item in have_nodes]
        have_node: Cluster_ExecuteResult = have_nodes.filter(node__uuid=node.uuid).first()
        result_list.append({
            "nodeName": node.name,
            "success": is_success,
            'resultUuid': have_node.result_uuid if have_node else False,
        })
    return result.success(result_list)


def getCommandInfo(request: HttpRequest):
    """
    获取指令信息
    """
    uuid = request.GET.get("uuid")
    if not uuid:
        return error("uuid不能为空")
    if not is_uuid(uuid):
        return error("参数错误")
    cluster_execute: Cluster_Execute = Cluster_Execute.objects.filter(uuid=uuid).first()
    if not cluster_execute:
        return error("指令不存在")
    return success({
        "group": cluster_execute.group.id,
        "shell": cluster_execute.shell,
        "basePath": cluster_execute.base_path,
    })


def deleteByUUID(request: HttpRequest):
    """
    根据UUID删除指令
    """
    uuid = request.GET.get("uuid")
    code = request.GET.get("code")
    if not uuid:
        return error("uuid不能为空")
    if not is_uuid(uuid):
        return error("参数错误")
    if not verify_otp_for_request(request, code):
        return error("操作验证失败，请检查您的手机令牌")
    Cluster_Execute.objects.filter(uuid=uuid).delete()
    write_audit(request.session['userID'], "删除执行器", "集群命令", f"指令UUID: {uuid}")
    return success(msg="删除成功")


def downloadResult(request: HttpRequest):
    uuid = request.GET.get("uuid")
    if not is_uuid(uuid):
        return error("参数错误")
    save_dir = apps.get_app_config('node_manager').group_command_result_save_dir
    file_path = os.path.join(save_dir, uuid)
    return file(str(file_path))
