# import models
from typing import Union, List, Dict

from django.db.models import QuerySet

from apps.permission_manager.models import Permission_groups, Permission_Item


def get_all_permission_items():
    """获取所有权限项"""
    return list(Permission_Item.objects.all().values_list('permission', flat=True))


def get_all_permission_item_info():
    """获取所有权限项详细信息"""
    temp: list = []
    for item in Permission_Item.objects.all().values():
        temp.append(item)
    return temp


def get_all_permission_group_name():
    """获取所有权限组名"""
    return list(Permission_groups.objects.all().values_list('name', flat=True))


class groupPermission:
    __group: Permission_groups

    def __init__(self, group: int | Permission_groups):
        """
        :param group: 权限组id
        """
        try:
            if isinstance(group, Permission_groups):
                self.__group = group
            else:
                self.__group = Permission_groups.objects.get(id=group)
        except Permission_groups.DoesNotExist:
            raise RuntimeError("The permission group does not exist")

    def get_group_obj(self) -> Permission_groups:
        """
        获取权限组对象
        :return: app.models.Permission_groups
        """
        return self.__group

    def get_group_name(self) -> str:
        """
        获取权限组名
        :return: str
        """
        return self.__group.name

    def get_permissions_list(self) -> QuerySet:
        """
        获取权限列表
        :return: <QuerySet [str]>
        """
        return self.__group.permissions.all().values_list('permission', flat=True)

    def update_permissions_list(self, permissions: Union[List[str], Dict[str, bool]]):
        """
        更新权限列表
        :param permissions: 权限列表
        :return: None
        """
        temp = []
        if isinstance(permissions, dict):
            for k, v in permissions.items():
                if v:
                    temp.append(k)
        else:
            temp = permissions

        all_permissions_items = get_all_permission_items()
        self.__group.permissions.clear()
        for permission in temp:
            if permission in all_permissions_items:
                self.__group.permissions.add(Permission_Item.objects.get(permission=permission))
            else:
                RuntimeError(f"The permission entry {permission} does not exist")

    def get_permissions_dict(self) -> dict:
        """
        获取权限字典
        :return: dict
        """
        temp = {}
        for p_item in get_all_permission_items():
            temp.update({p_item: self.check_group_permission(p_item)})
        return temp

    def check_group_permission(self, permission_name: str) -> bool:
        """
        检查组内是否有该权限
        :param permission_name: 权限名
        :return: bool
        """
        return permission_name in self.get_permissions_list()

    def is_superuser(self) -> bool:
        return self.check_group_permission('all')

    def is_disable(self) -> bool:
        return self.__group.disable
