import json

from django.shortcuts import HttpResponse

from util.jsonEncoder import ComplexEncoder


def ResponseJson(data: dict):
    return HttpResponse(json.dumps(data, cls=ComplexEncoder), content_type="application/json")
