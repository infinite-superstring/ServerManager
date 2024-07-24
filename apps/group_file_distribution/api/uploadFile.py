import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from util.logger import Log

UPLOAD_DIR = 'data/uploads'  # 上传文件保存的目录
TEMP_DIR = 'data/temp'  # 临时文件保存目录

import hashlib


def calculate_file_hash(file):
    sha256 = hashlib.sha256()
    for chunk in file.chunks():
        sha256.update(chunk)
    return sha256.hexdigest()


@csrf_exempt
def upload_chunk(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        chunk_index = request.POST.get('chunkIndex')
        file_name = request.POST.get('fileName')
        chunk_hash = request.POST.get('hash')

        if not file or chunk_index is None or not file_name:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        # 保存切片文件
        file_path = os.path.join(TEMP_DIR, f'{file_name}_part_{chunk_index}.tmp')
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        Log.debug(chunk_index)
        Log.debug(int(chunk_index) == 2)
        if chunk_index == 2:
            return JsonResponse({'error': 'Invalid method'}, status=405)

        # # 校验切片哈希值
        # with open(file_path, 'rb') as f:
        #     calculated_hash = calculate_file_hash(f)
        #     if calculated_hash != chunk_hash:
        #         os.remove(file_path)  # 如果哈希值不匹配，删除文件块
        #         return JsonResponse({'error': 'Hash mismatch'}, status=400)

        return JsonResponse({'status': 'Chunk uploaded successfully'})
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def merge_chunks(request):
    if request.method == 'POST':
        file_name = request.POST.get('fileName')
        total_chunks = int(request.POST.get('totalChunks'))

        if not file_name or total_chunks <= 0:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        # 创建一个单独的文件来存储合并后的文件
        output_file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(output_file_path, 'wb') as output_file:
            for i in range(total_chunks):
                chunk_file_path = os.path.join(TEMP_DIR, f'{file_name}_part_{i}.tmp')
                if os.path.exists(chunk_file_path):
                    with open(chunk_file_path, 'rb') as chunk_file:
                        output_file.write(chunk_file.read())
                    os.remove(chunk_file_path)  # 可选：合并后删除切片文件

        return JsonResponse({'status': 'File merged successfully'})
    return JsonResponse({'error': 'Invalid method'}, status=405)
