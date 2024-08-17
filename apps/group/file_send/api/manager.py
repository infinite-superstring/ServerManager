import os.path

from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET

from apps.audit.util.auditTools import write_access_log, write_audit
from apps.group.file_send.models import File_DistributionTask, FileDistribution_FileList
from apps.group.file_send.utils.taskUtils import exists_task_by_uuid, get_task_by_uuid
from apps.group.manager.utils.groupUtil import node_group_id_exists, get_node_group_by_id, GroupUtil
from apps.node_manager.models import Node_BaseInfo
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.asgi_file import get_file_response
from util.logger import Log
from util.pageUtils import get_page_content, get_max_page

UPLOAD_FILE_PATH = os.path.join(os.getcwd(), "data", "file_distribution")

@require_GET
def get_distribution_tasks(request: HttpRequest) -> HttpResponse:
    """
    获取文件分发任务列表
    """
    page_index = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))
    result = File_DistributionTask.objects.all()
    pageQuery = get_page_content(result, page_index if page_index > 0 else 1, page_size)
    PageContent: list = []
    if pageQuery:
        for task in pageQuery:
            task: File_DistributionTask = File_DistributionTask.objects.get(uuid=task.get('uuid'))
            PageContent.append({
                'uuid': task.uuid,
                'group': {
                    'id': task.group.id,
                    'name': task.group.name,
                },
                'receive_directory': task.receive_directory,
                'ctime': task.creation_time,
                'creator': {
                    'id': task.creator.id,
                    'user_name': task.creator.userName
                },
                'progress': {
                    'activity': task.progress.filter(status='Activity').count(),
                    'success': task.progress.filter(status='Success').count(),
                    'failure': task.progress.filter(status='Failure').count(),
                    'offline': task.progress.filter(status='Offline').count(),
                }
            })
    write_access_log(
        request.session["userID"],
        request,
        "节点管理",
        f"获取节点列表(页码: {page_index} 页大小: {page_size})"
    )
    return ResponseJson({
        "status": 1,
        "data": {
            "maxPage": get_max_page(result.all().count(), page_size),
            "currentPage": page_index,
            "PageContent": PageContent
        }
    })


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
    for node in GroupUtil(group).get_node_list():
        node_info = Node_BaseInfo.objects.filter(node=node)
        task.progress.add(File_DistributionTask.Progress.objects.create(
            node=node,
            status='Activity' if node_info.exists() and node_info.filter().online else 'Offline'
        ))
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
    write_audit(
        user,
        '创建任务',
        '集群文件分发',
        f'集群：{group.name} 任务uuid: {task.uuid}',
    )
    return ResponseJson({
        "status": 1,
        "msg": "开始文件分发"
    })


@require_GET
def get_distribution_task_info(request: HttpRequest) -> HttpResponse:
    """
    获取文件分发任务信息
    """
    task_id = request.GET.get('uuid')
    if not task_id:
        return ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not exists_task_by_uuid(task_id):
        return ResponseJson({'status': 0, 'msg': '分发任务不存在'})
    task = get_task_by_uuid(task_id)
    return ResponseJson({
        "status": 1,
        "msg": "获取成功",
        "data": {
            "uuid": task.uuid,
            "group": {
                "id": task.group.id,
                "name": task.group.name,
            },
            "file_list": [{
                "file_name": file.file_name.filter(task=task).first().name,
                "hash": file.file_hash
            } for file in task.files.all()],
            "ctime": task.creation_time,
            "creator": {
                'id': task.creator.id,
                'user_name': task.creator.userName
            },
            "progress": {
                progress.node.name: {
                    'status': progress.status,
                    'success_files': [file.file_name for file in progress.success_files.all()],
                    'failure_files': [file.file_name for file in progress.failure_files.all()]
                } for progress in task.progress.all()
            }
        }
    })


@require_GET
def download_file(request: HttpRequest) -> HttpResponse:
    task_id = request.GET.get('task')
    file_id = request.GET.get('file')
    if not task_id or not file_id:
        return ResponseJson({'status': -1, 'msg': '参数不完整'})
    if not exists_task_by_uuid(task_id):
        return ResponseJson({'status': 0, 'msg': '分发任务不存在'})
    task = get_task_by_uuid(task_id)
    file = task.files.all().filter(file_hash=file_id)
    save_path = os.path.join(UPLOAD_FILE_PATH, file_id)
    Log.debug(file.exists())
    Log.debug(save_path)
    Log.debug(os.path.exists(save_path))
    if not file.exists() or not os.path.exists(save_path):
        return ResponseJson({'status': 0, 'msg': '文件不存在'})
    file = file.first()
    return get_file_response(save_path, file.file_name.all().filter(task=task).first().name)