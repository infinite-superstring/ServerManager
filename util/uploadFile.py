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

    def _read_io(f_io, hash_obj):
        while True:
            chunk = f_io.read(1024)
            if not chunk:
                break
            hash_obj.update(chunk)
        return hash_obj

    if isinstance(file, InMemoryUploadedFile):
        """
        输入Django Form文件流时
        """
        for chunk in file.chunks():
            sha256.update(chunk)
    elif isinstance(file, str):
        """
        输入文件名时
        """
        with open(file, 'rb') as f:
            sha256 = _read_io(f, sha256)
    else:
        sha256 = _read_io(file, sha256)
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
    output_hash = calculate_file_hash(file)
    if chunk_hash != output_hash:
        Log.debug(f"{chunk_hash} != {output_hash}")
        return JsonResponse({"status": 0, "msg": "文件块校验失败"}, status=400)

    SAVE_FILE = os.path.join(TEMP_DIR, f"{chunk_hash}.tmp")

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    elif os.path.exists(SAVE_FILE):
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
def merge_chunks(request, save_path, rename_to_hash=False, remove_chunks=False) -> [bool, str]:
    """
    合并文件块
    :param request: 请求体
    :param save_path: 文件保存路径
    :param rename_to_hash: 重命名为文件哈希值
    :param remove_chunks: 完成后删除文件块

    :return: bool, str 状态 保存后的文件名
    """
    file_name = request.POST.get('file_name')
    chunk_count = int(request.POST.get('chunk_count'))
    chunk_hash_list = request.POST.get('chunk_hash_list').split(",")
    user: User = get_user_by_id(request.session['userID'])
    if not file_name or chunk_count <= 0 or not chunk_hash_list:
        Log.warning("参数不完整")
        return False, None
    # 创建一个单独的文件来存储合并后的文件
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    output_file_path = os.path.join(save_path, file_name)
    with open(output_file_path, 'wb+') as output_file:
        for chunk_hash in chunk_hash_list:
            chunk_file = os.path.join(TEMP_DIR, f"{chunk_hash}.tmp")
            if not os.path.exists(chunk_file):
                write_system_log(2, "文件上传", f"切片文件{chunk_hash}.tmp丢失，文件合并失败")
                Log.error(f"切片文件{chunk_hash}.tmp不存在")
                return False, None
            with open(chunk_file, 'rb') as chunk:
                output_file.write(chunk.read())
    # 如有需求，计算文件哈希并重命名文件
    if rename_to_hash:
        output_hash = calculate_file_hash(output_file_path)
        if not os.path.exists(output_file_path):
            os.rename(output_file_path, os.path.join(save_path, f"{output_hash}.file"))
        else:
            os.remove(output_file_path)
        output_file_path = os.path.join(save_path, f"{output_hash}.file")
    if remove_chunks:
        for chunk_hash in chunk_hash_list:
            os.remove(os.path.join(TEMP_DIR, f"{chunk_hash}.tmp"))
    write_file_change_log(user, "合并文件", output_file_path.__str__())
    return True, os.path.basename(output_file_path)
