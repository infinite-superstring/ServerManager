import datetime
import json

from django.http import HttpRequest
from django.http import StreamingHttpResponse

from util.logger import Log


def getTopData(request: HttpRequest):
    """
    获取大屏头部数据
    """
    return {

    }


def getBodyData(request):
    """"""


def view_data(request: HttpRequest):
    """
    大屏 SSE 连接
    """

    def event_stream():

        try:
            yield_data = {
                'top': getTopData(request),
                'body': getBodyData(request),
                'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            Log.debug(yield_data)
            yield json.dumps(yield_data)

        except GeneratorExit as e:  # 用户主动断开走此方法
            Log.error('GeneratorExit' + str(e))
            return

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
