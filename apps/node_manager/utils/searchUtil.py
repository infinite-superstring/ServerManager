import re


def extract_search_info(search_string):
    # 定义标签、组和搜索关键词的正则表达式模式
    tag_pattern = r'tag:(\w+)'
    group_pattern = r'group:(\w+)'

    # 使用正则表达式找到所有的标签、组和搜索关键词
    tags = re.findall(tag_pattern, search_string)
    groups = re.findall(group_pattern, search_string)

    # 提取正常的搜索信息（假定位于字符串开头）
    start_index = len(search_string)
    for tag in tags:
        tag_index = search_string.find(f'tag:{tag}')
        if tag_index != -1 and tag_index < start_index:
            start_index = tag_index
    for group in groups:
        group_index = search_string.find(f'group:{group}')
        if group_index != -1 and group_index < start_index:
            start_index = group_index

    normal_search_info = search_string[:start_index].strip()

    return normal_search_info, tags, groups
