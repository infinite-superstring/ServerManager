import asyncio
import os
import urllib

import aiofiles
from django.http import StreamingHttpResponse


async def __async_file_iterator(file_path, chunk_size=8192):
    async with aiofiles.open(file_path, mode='rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def get_file_response(file_path: str, file_name: str = None, chunk_size: int=8192):
    """同步返回文件"""
    # from asgiref.sync import async_to_sync
    iterator = __async_file_iterator(file_path, chunk_size)
    response = StreamingHttpResponse(iterator)
    response['Content-Type'] = 'application/octet-stream'
    encoded_file_name = urllib.parse.quote(file_name if file_name is not None else os.path.basename(file_path))
    response['Content-Disposition'] = f'attachment; filename={encoded_file_name}'
    return response

async def async_file_response(file_path: str, file_name: str = None, chunk_size: int=8192):
    """异步返回文件"""
    response = StreamingHttpResponse(__async_file_iterator(file_path, chunk_size))
    response['Content-Type'] = 'application/octet-stream'
    encoded_file_name = urllib.parse.quote(file_name if file_name is not None else os.path.basename(file_path))
    response['Content-Disposition'] = f'attachment; filename={encoded_file_name}'
    return response
