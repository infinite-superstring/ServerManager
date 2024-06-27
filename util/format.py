def format_bytes(size):
    """
    格式化Bytes长度成可读类型
    """
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}

    while size >= power and n < len(power_labels) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {power_labels[n]}"
