import os.path

from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET

from apps.group.file_send.models import File_DistributionTask, FileDistribution_FileList
from apps.group.manager.utils.groupUtil import node_group_id_exists, get_node_group_by_id
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log

UPLOAD_FILE_PATH = os.path.join(os.getcwd(), "data", "file_distribution")

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

    user = get_user_by_id(request.session["userID"])

    group_id: int = req_json.get('group_id')
    files: list = req_json.get('files')
    receive_directory: str = req_json.get('receive_directory')
    if not node_group_id_exists(group_id):
        return ResponseJson({'status': -1, 'msg': '集群不存在'})
    group = get_node_group_by_id(group_id)
    task: File_DistributionTask = File_DistributionTask.objects.create(
        group=group,
        receive_directory=receive_directory,
        creator=user
    )
    for file in files:
        file_name = file.get('file_name')
        file_hash = file.get('hash')
        if not os.path.exists(os.path.join(UPLOAD_FILE_PATH, file_hash)):
            task.delete()
            return ResponseJson({
                "status": 0,
                "msg": f"文件 {file_name} 不存在于服务器中！"
            })
        f = FileDistribution_FileList.objects.filter(file_hash=file_hash)
        fn = FileDistribution_FileList.FileName.objects.create(name=file_name, task=task)
        if f.exists():
            f = f.first()
            f.file_name.add(fn)
        else:
            f = FileDistribution_FileList.objects.create(file_hash=file_hash, uploader=user)
            f.file_name.add(fn)
        f.save()
        task.files.add(f)
    return ResponseJson({
        "status": 1,
        "msg": "开始文件分发"
    })

@require_GET
def get_distribution_task_info(request: HttpRequest) -> HttpResponse:
    """
    获取文件分发任务信息
    """