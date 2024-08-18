import datetime

from django.http import HttpRequest

from apps.screen.utils import screenUtil
from util import result


def getBodyData(request):
    """"""


def view_data(request: HttpRequest):
    """
    大屏 数据
    """
    data = {
        'top': screenUtil.get_top_data(),
        'body': screenUtil.pack_node_data(),
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return result.success(data)
