from urllib.parse import quote

from django.http import StreamingHttpResponse

from util import file_util
from util.Response import ResponseJson


def success(data='', msg='success', http_code=200, result_code=1):
    return ResponseJson(status=http_code, data={
        'status': result_code,
        'msg': msg,
        'data': data
    })


def error(msg='error', http_code=200, result_code=0):
    return ResponseJson(
        status=http_code,
        data={
            'status': result_code,
            'msg': msg,
            'data': ''
        }
    )


def api_error(msg='error', http_code=403, result_code=-1):
    return ResponseJson(
        status=http_code,
        data={
            'status': result_code,
            'msg': msg,
            'data': ''
        }
    )


def file(file_path: str, file_name='', is_cors: bool = True):
    """
    返回一个下载文件
    """
    if not file_util.is_file(file_path):
        return error(msg='文件不存在')

    if not file_name:
        file_name = file_util.getFileName(file_path)

    file_name = quote(file_name)

    response = StreamingHttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    if is_cors:
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    response.streaming_content = file_util.file_iterator(file_path)

    return response
