import time

from django.core.cache import cache


def get_hourly_api_call_count():
    """获取一个小时内每分钟所有API的调用次数"""
    current_minute = int(time.time() // 60)
    counts = {}

    # 获取过去一小时内每分钟的调用数
    for i in range(60):
        key = f"api_count:{current_minute - i}"
        count = cache.get(key, 0)
        counts[f"{current_minute - i}"] = count

    return counts


def get_hourly_api_path_call_count(api_path):
    """按API路径获取在一个小时内每分钟调用次数"""
    current_minute = int(time.time() // 60)
    counts = {}

    # 获取过去一小时内每分钟的调用数
    for i in range(60):
        key = f"api_count:{api_path}:{current_minute - i}"
        count = cache.get(key, 0)
        counts[f"{current_minute - i}"] = count

    return counts
