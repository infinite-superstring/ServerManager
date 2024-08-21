import logging
from util.logger import Log


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取Loguru对应的日志级别
        try:
            level = Log.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到发起日志调用的帧
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        Log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
