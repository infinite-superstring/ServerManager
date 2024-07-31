import os
import hashlib

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from apps.audit.util.auditTools import write_system_log, write_file_change_log
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id
from util.logger import Log

TEMP_DIR = 'data/temp'  # 临时文件保存目录

def calculate_file_hash(file):
    sha256 = hashlib.sha256()
    if isinstance(file, InMemoryUploadedFile):
        for chunk in file.chunks():
            sha256.update(chunk)
    else:
        while True:
            data = file.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def upload_chunk(request: HttpRequest):
    """
    上传文件块
    :param request: 请求体
    """
    file = request.FILES.get('file')
    chunk_index = request.POST.get('index')
    chunk_hash = request.POST.get('hash')

    if not file or chunk_index is None or not chunk_hash:
        return JsonResponse({"status": -1, "msg": "参数不完整"}, status=400)

    # 校验切片文件
    if chunk_hash != calculate_file_hash(file):
        Log.debug(f"{chunk_hash} != {calculate_file_hash(file)}")
        return JsonResponse({"status": 0, "msg": "文件块校验失败"}, status=400)

    SAVE_FILE = os.path.join(TEMP_DIR, f"{chunk_hash}.tmp")

    if os.path.exists(SAVE_FILE):
        return JsonResponse({"status": 1, "data": {
            "pass": True,
            "index": chunk_index,
        }})

    # 保存切片文件
    file_path = os.path.join(TEMP_DIR, f'{chunk_hash}.tmp')
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return JsonResponse({'status': 1, "data": {
        "pass": False,
        "index": chunk_index,
    }})


@csrf_exempt
def merge_chunks(request, save_path, remove_chunks=False):
    """
    合并文件块
    :param request: 请求体
    :param save_path: 文件保存路径
    :param remove_chunks: 完成后删除文件块
    """
    file_name = request.POST.get('file_name')
    chunk_count = int(request.POST.get('chunk_count'))
    chunk_hash_list = request.POST.get('chunk_hash_list').split(",")
    user: User = get_user_by_id(request.session['userID'])
    if not file_name or chunk_count <= 0 or not chunk_hash_list:
        return JsonResponse({'status': -1, 'msg': '参数不完整'}, status=400)
    # 创建一个单独的文件来存储合并后的文件
    output_file_path = os.path.join(save_path, file_name)
    with open(output_file_path, 'wb+') as output_file:
        for chunk_hash in chunk_hash_list:
            chunk_file = os.path.join(TEMP_DIR, f"{chunk_hash}.tmp")
            if not os.path.exists(chunk_file):
                write_system_log(2, "文件上传", f"切片文件{chunk_hash}.tmp丢失，文件合并失败")
                return JsonResponse({'status': 0, 'msg': f"切片文件{chunk_hash}.tmp不存在"}, status=404)
            with open(chunk_file, 'rb') as chunk:
                output_file.write(chunk.read())
    for chunk_hash in chunk_hash_list:
        os.remove(os.path.join(TEMP_DIR, f"{chunk_hash}.tmp"))
    if remove_chunks:
        write_file_change_log(user, "合并文件", output_file_path.__str__())
    return JsonResponse({'status': 1})
