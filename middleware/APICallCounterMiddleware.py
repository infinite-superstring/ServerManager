import time
from django.core.cache import cache


class APICallCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 记录API调用数
        if request.path.startswith('/api'):
            self.count_all_api_call()
            self.count_api_path_call(request)
        response = self.get_response(request)
        return response

    def count_api_path_call(self, request):
        # 获取当前时间戳的分钟部分
        current_minute = int(time.time() // 60)
        # 使用请求的路径作为键
        key = f"api_count:{request.path}:{current_minute}"
        # 增加计数
        count = cache.get(key, 0)
        cache.set(key, count + 1, timeout=3600)

    def count_all_api_call(self):
        # 获取当前时间戳的分钟部分
        current_minute = int(time.time() // 60)
        # 使用固定键
        key = f"api_count:{current_minute}"
        # 增加计数
        count = cache.get(key, 0)
        cache.set(key, count + 1, timeout=3600)
