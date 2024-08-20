import re


class URL_PathUtil:
    """
    Web路径实用工具
    """
    __path: str

    def __init__(self, path: str):
        self.__path = path

    def is_node_path(self) -> bool:
        """节点"""
        return re.match(r".*/node/.*", self.__path) is not None

    def is_admin_path(self) -> bool:
        """管理"""
        return re.match(r"^/admin/*.*", self.__path) is not None

    def is_api_path(self) -> bool:
        """"""
        return re.match(r".*/api/.*", self.__path) is not None