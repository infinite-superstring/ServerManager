
def is_exist_by_list_index(target: list, index: int, element: any) -> bool:
    """
    判断数组中的某个index是否存在某个元素
    :param target: 目标列表
    :param element: 目标元素
    """
    for i in target:
        print(i)
        if element == i[index]:
            return True
    return False



def is_exist_by_double_list(target: list, element: any) -> bool:
    """
    判断二维数组中是否存在某个元素
    :param target: 目标列表
    :param element: 目标元素
    """
    for i in target:
        if element in i:
            return True
    return False


def is_exist_by_double_list_index(target: list, index: int, element: any) -> bool:
    """
    判断二维数组中的某个index是否存在某个元素
    :param target: 目标列表
    :param element: 目标元素
    """
    for i in target:
        print(i)
        if element in i[index]:
            return True
    return False
