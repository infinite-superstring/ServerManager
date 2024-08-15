import os.path

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from apps.audit.util.auditTools import write_audit
from apps.group.file_send.models import FileDistribution_FileList
from apps.user_manager.util.userUtils import get_user_by_id
from util import uploadFile

FILE_SAVE_BASE_PATH = os.path.join(os.getcwd(), "data", "file_distribution")


@require_POST
def upload_file_chunk(req: HttpRequest) -> HttpResponse:
    return uploadFile.upload_chunk(req)


@require_POST
def merge_file(req: HttpRequest) -> HttpResponse:
    user = get_user_by_id(req.session["userID"])
    file_name = req.POST.get("file_name")
    if not os.path.exists(FILE_SAVE_BASE_PATH):
        os.makedirs(FILE_SAVE_BASE_PATH)
    merge_status, hash256 = uploadFile.merge_chunks(req, FILE_SAVE_BASE_PATH, True)
    if merge_status:
        write_audit(user, "上传文件", "集群文件分发", f"{file_name} (hash256: {hash256})")
        return JsonResponse({'status': 1, 'data': {
            'file_name': file_name,
            'hash': hash256,
        }})
    return JsonResponse({'status': 0})
