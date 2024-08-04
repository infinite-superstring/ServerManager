from typing import Callable

from django.apps import apps
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET

from apps.audit.util.auditTools import write_audit
from apps.group.commandExecution.models import Cluster_Execute
from apps.group.commandExecution.utils.group_command_util import executeGroupCommand
from apps.group.group_task.utils import group_task_util
from apps.node_manager.utils.groupUtil import get_node_group_by_id
from apps.node_manager.utils.groupUtil import node_group_id_exists
from apps.permission_manager.util.permission import groupPermission
from apps.setting.entity.Config import config
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page
from util.result import api_error, error, success

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
    page = request.GET.get("page", 1)
    pageSize = request.GET.get("pageSize", 20)
    result = Cluster_Execute.objects.all()
    pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
    if pageQuery:
        for item in pageQuery:
            PageContent.append({
                'uuid': item.get("uuid"),
                'user': get_user_by_id(item.get("user_id")).userName,
                'group': get_node_group_by_id(item.get("group_id")).name,
                'shell': item.get("shell"),
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
