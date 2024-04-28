import time

from loguru import logger as Log

Log.add(f"logs/{time.strftime('%Y-%m-%d', time.localtime())}.log")
