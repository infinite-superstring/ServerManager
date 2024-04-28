from util.logger import Log


@Log.catch
def get_max_page(count: int, size: int) -> int:
    """
    获取最大页数
    :param count: 总条数
    :param size: 页大小
    :return: 共x页
    """
    return (count + size - 1) // size


@Log.catch
def get_page_content(model, page: int, size: int):
    """
    获取指定页内容
    :param model: Model实体
    :param page: 页码
    :param size: 页大小
    :return:
    """
    if get_max_page(model.count(), size) >= page:
        pageStart = size * (page - 1)
        pageEnd = pageStart + size
        return model.values()[pageStart:pageEnd]
    else:
        return model.values()[model.count() - size if not model.count() - size < 0 else 0:model.count()]