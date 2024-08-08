import os
from enum import Enum

import chardet

from util.logger import Log


class SizeType(Enum):
    B = 1
    KB = 1024
    MB = 1024 ** 2
    GB = 1024 ** 3
    TB = 1024 ** 4


def is_dir(path: str) -> bool:
    """
    判断是否为目录
    :param path: 路径
    :return: 是否为目录
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """
    判断是否为文件
    :param path: 路径
    :return: 是否为文件
    """
    if not path:
        return False
    return os.path.isfile(path)


def file_to_size(file_path: str, size_type: SizeType = SizeType.B) -> int | float:
    """
    获取文件大小
    :param file_path: 文件路径
    :param size_type: 文件大小单位
    :return: 文件大小
    """
    if not os.path.exists(file_path):
        return -1
    if is_dir(file_path):
        return -1
    if is_file(file_path):
        return os.path.getsize(file_path) / size_type.value
    return -1


def read_text_file(file_path: str,
                   encoding: str = 'utf-8',
                   read_lines: int = 0,
                   is_asc: bool = True) -> list[str]:
    """
    读取文本文件
    :param file_path: 文件路径
    :param encoding: 文件编码
    :param read_lines: 读取行数
    :param is_asc: 是否升序
    :return: 文件内容
    """
    # 参数校验
    if not isinstance(file_path, str) or not file_path.strip():
        Log.error('file_path无效')
        return []

    if not isinstance(read_lines, int) or read_lines < 0:
        Log.error('read_lines无效')
        return []

    if not os.path.exists(file_path):
        Log.error('文件不存在')
        return []

    try:
        with open(file_path, 'r', encoding=encoding) as file:
            lines = []
            if is_asc:
                if read_lines > 0:
                    for _ in range(read_lines):
                        line = file.readline()
                        if not line:
                            break
                        lines.append(line)
                else:
                    lines = file.readlines()
            else:
                if read_lines > 0:
                    for line in reversed(list(file)):
                        lines.insert(0, line)
                        if len(lines) == read_lines:
                            break
                else:
                    lines = list(reversed(list(file)))

        return lines

    except UnicodeDecodeError as e:
        Log.error('文件编码错误' + str(e))
        return []
    except IOError as e:
        Log.error('文件读取错误' + str(e))
        return []
    except Exception as e:
        Log.error('未知的错误' + str(e))
        return []


def file_encode(file_path: str) -> str:
    """
    获取文件编码
    """
    if not is_file(file_path):
        return ''
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # 只读取前10000字节进行编码检测
        detected = chardet.detect(raw_data)
        encoding = detected['encoding'] or 'utf-8'  # 如果无法检测出编码，默认使用utf-8
    return encoding
