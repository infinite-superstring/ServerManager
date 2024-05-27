import json

from django.shortcuts import HttpResponse
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseGone

from util.jsonEncoder import ComplexEncoder
from util.logger import Log

def ResponseJson(data: dict, status: int = 200):
    res_method = None
    match status:
        case 200:
            res_method = HttpResponse
        case 400:
            res_method = HttpResponseBadRequest
        case 403:
            res_method = HttpResponseForbidden
        case 404:
            res_method = HttpResponseNotFound
        case 405:
            res_method = HttpResponseNotAllowed
        case 410:
            res_method = HttpResponseGone
        case 500:
            res_method = HttpResponseServerError
        case _:
            Log.error(f"Unknown HTTP Status: {status}")
            return HttpResponseServerError(json.dumps({"status": "-1", "msg": "Server Error!"}))
    try:
        return res_method(json.dumps(data, cls=ComplexEncoder), content_type="application/json")
    except Exception as e:
        Log.error(f"Exception when calling ResponseJson: {e}")
        return HttpResponseServerError(json.dumps({"status": "-1", "msg": "Server Error!"}))
