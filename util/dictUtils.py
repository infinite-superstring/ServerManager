def get_key_by_value(dictionary, value, first=False):
    """根据value获取key值，返回第一个"""
    keys = []
    if first and value not in dictionary.values():
        return None
    for key, val in dictionary.items():
        if val == value:
            keys.append(key)
            if first:
                return key
            else:
                keys.append(key)
    return keys


def append_to_dict(dictionary, data):
    dictionary.update(data)
    return dictionary
