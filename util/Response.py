import json

from django.db.models import QuerySet
from django.shortcuts import HttpResponse
from datetime import date, datetime


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, QuerySet):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def ResponseJson(data: dict):
    return HttpResponse(json.dumps(data, cls=ComplexEncoder), content_type="application/json")
