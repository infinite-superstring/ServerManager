from django.http import HttpRequest, HttpResponse

from apps.node_manager.models import Cluster_Execute
from apps.node_manager.utils.groupUtil import node_group_id_exists, get_node_group_by_id
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.pageUtils import get_page_content
from util.result import api_error, error, success
from util.logger import Log


def createTask(request: HttpRequest) -> HttpResponse:
    """
    创建Shell执行任务
    """
    if not request.method == "POST":
        return api_error("请求方式不正确")
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
    if not node_group_id_exists(group):
        return error("节点组不存在")
    Cluster_Execute.objects.create(
        group=get_node_group_by_id(group),
        user=user,
        base_path=base_path,
        shell=shell
    )


def getResultList(request: HttpRequest) -> HttpResponse:
    """
    获取Shell执行返回列表
    """
    if not request.method == "GET":
        return api_error("请求方式不正确")
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

def getResult(request: HttpRequest) -> HttpResponse:
    """
    获取Shell执行返回
    """
