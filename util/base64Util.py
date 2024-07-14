import base64
import magic


def get_file_size(base64_string):
    """获取文件大小"""
    file_data = base64.b64decode(base64_string)
    file_size = len(file_data)

    return file_size


def get_file_type(base64_string):
    """获取文件类型"""
    file_data = base64.b64decode(base64_string)
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_data)
    return file_type

def is_image_file(base64_string):
    # 检查文件类型是否为图像类型
    return get_file_type(base64_string).startswith('image/')