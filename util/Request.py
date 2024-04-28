import json

def RequestLoadJson(request):
    """
    接收Json数据
    :param request: 请求体
    :return:
    """
    return json.loads(request.body.decode("utf-8"))

def getClientIp(request):
    """
    获取客户端IP地址
    :param request: 请求体
    :return: IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip