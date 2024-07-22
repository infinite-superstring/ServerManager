import re

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from apps.user_manager.util.userUtils import get_user_by_id
from util.Response import ResponseJson
from apps.permission_manager.util.permission import groupPermission


class PermissionsMiddleware(MiddlewareMixin):
    """
    权限校验中间件
    """

    def process_request(self, request):
        userId = request.session.get("userID")
        path_info = request.path_info

        # 忽略权限
        Ignore = [
            "/api/auth/login",
            "/api/auth/nodeAuth",
            "/ws/node/node_client",
            "/api/settings/getServerConfig",
            "/api/auth/getUserLoginStatus"
        ]

        # 页面权限表
        accessPermission = {
            # 用户管理
            # "/api/admin/userManager/getUserList": [
            #     "manageUser",
            #     "editNodeGroup"
            # ],
            # "/api/admin/userManager/.*": "manageUser",
            # 权限管理
            # "/api/admin/permissionManager/.*": "managePermissionGroup",
            # 节点管理器
            # (
            #     "/api/node_manager/addNode"
            #     "/api/node_manager/delNode",
            #     "/api/node_manager/editNode",
            #     "/api/node_manager/resetToken"
            #     "/api/node_manager/node_info/save_alarm_setting"
            # ): "editNode",
            # "/api/node_manager/node_tag/search_tag": 'editNode',
            # "/api/node_manager/getNodeList": ['editNode', 'viewAllNode', "editNodeGroup"],
            # "/api/node_manager/getBaseNodeList": ['editNodeGroup', 'editNode', 'viewAllNode'],
            # "/api/node_manager/getNodeInfo": ['editNodeGroup', 'editNode', 'viewAllNode'],
            # 集群/节点组
            # "/api/node_manager/node_group/getGroupList": ["editNodeGroup", 'clusterTask', "clusterExecuteCommand"],
            # (
            #     "/api/node_manager/node_info/createGroup",
            #     "/api/node_manager/node_group/delGroup"
            #     "/api/node_manager/node_group/getGroupById"
            # ): "editNodeGroup",
            # 集群 - 执行
            # "/api/node_manager/cluster/execute/.*": "clusterExecuteCommand",
            # 集群 - 任务
            # "/api/group_task/.*": 'clusterTask',
            # 节点信息
            # "/api/node_manager/node_info/.*": "editNode",
            # 网站监控
            # "/api/webStatus/getList": "viewWebStatus",
            # (
            #     "/api/webStatus/addWeb",
            #     "/api/webStatus/delWeb",
            #     "/api/webStatus/update"
            # ): "editWebStatus",
            # "/api/webStatus/getSiteNames": ['viewWebStatus', "viewAudit"],
            # "/api/webStatus/getLog": ['viewWebStatus', "viewAudit"],
            # 系统设置
            # "/api/admin/settings/.*": "changeSettings",
            # 巡检记录
            # (
            #     "/api/patrol/addARecord",
            #     "/api/patrol/getList"
            # ): "viewPatrol",
            # (
            #     "/api/patrol/updateARecord",
            #     "/api/patrol/deleteRecord"
            # ): "editPatrol",
            # 值班记录
            # "/api/task/getDuty": 'viewDuty',
        }

        # 忽略权限过滤器
        if path_info in Ignore:
            return

        user = get_user_by_id(userId)

        if not user:
            request.session.clear()
            return redirect("/login")

        # 无权限时
        if not user.permission_id and path_info in accessPermission.keys():
            return ResponseJson({"status": -1, "msg": "未授权访问-账户无权限"}, 403)

        gp = groupPermission(user.permission)

        # 权限组被禁用时
        if gp.is_disable() and path_info in accessPermission.keys():
            return ResponseJson({"status": -1, "msg": "未授权访问-组已禁用"}, 403)

        for pattern, permission in accessPermission.items():
            # 处理正则
            if isinstance(pattern, str) and re.match(pattern, path_info):
                return self.__check_permission(gp, permission)
            # 处理元组
            elif isinstance(pattern, tuple):
                for p in pattern:
                    if isinstance(p, str) and re.match(p, path_info):
                        return self.__check_permission(gp, permission)

    def __check_permission(self, gp, permission):
        """检查是否拥有权限"""
        if isinstance(permission, str) and not gp.check_group_permission(permission):
            return ResponseJson({"status": -1, "msg": "未授权访问-无权限访问该API"}, 403)
        elif isinstance(permission, list):
            for p in permission:
                if gp.check_group_permission(p):
                    return
            return ResponseJson({"status": -1, "msg": "未授权访问-无权限访问该API"}, 403)
        return
