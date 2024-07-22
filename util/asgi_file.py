import asyncio
import os

import aiofiles
from django.http import StreamingHttpResponse


async def __async_file_iterator(file_path, chunk_size=8192):
    async with aiofiles.open(file_path, mode='rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def get_file_response(file_path, chunk_size=8192):
    """同步返回文件"""
    # from asgiref.sync import async_to_sync
    iterator = __async_file_iterator(file_path, chunk_size)
    response = StreamingHttpResponse(iterator)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response

async def async_file_response(file_path, chunk_size=8192):
    """异步返回文件"""
    response = StreamingHttpResponse(__async_file_iterator(file_path, chunk_size))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response
