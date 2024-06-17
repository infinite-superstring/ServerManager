import time

from loguru import logger as Log

Log.add(
    f"logs/{time.strftime('%Y-%m-%d', time.localtime())}.log",
    rotation="00:00",  # 每天午夜轮换日志文件
    retention="30 days",  # 只保留最近 30 天的日志文件
    level="INFO",  # 只记录 INFO 及以上级别的日志
    filter=lambda record: record["level"].name != "DEBUG"  # 不记录 DEBUG 级别的日志
)
