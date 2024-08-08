from django.http import HttpResponse

from util.Response import ResponseJson
from util.asgi_file import get_file_response


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


def api_error(msg='error', http_code=200, result_code=-1):
    return ResponseJson(
        status=http_code,
        data={
            'status': result_code,
            'msg': msg,
            'data': ''
        }
    )


def file(file_path: str):
    return get_file_response(file_path)
