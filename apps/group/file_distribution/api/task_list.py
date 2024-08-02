from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET

from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log

@require_GET
def get_distribution_tasks(request: HttpRequest) -> HttpResponse:
    """
    获取文件分发任务列表
    """


@require_POST
def create_distribution_task(request: HttpRequest) -> HttpResponse:
    """
    创建文件分发任务
    """
    try:
        req_json = RequestLoadJson(request)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)

    node_name: str = req_json.get('node_name')
    group: int = req_json.get('group_id')
    files: list = req_json.get('files')
    receive_directory: str = req_json.get('receive_directory')



@require_GET
def get_distribution_task_info(request: HttpRequest) -> HttpResponse:
    """
    获取文件分发任务信息
    """