"""
URL configuration for LoongArch-ServerManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

import apps.auth.api.user_auth as user_auth
import apps.auth.api.node_auth as node_auth
import apps.user_manager.api.user_management as user_manager
import apps.permission_manager.api.permission as permission_manager
import apps.node_manager.api.node_manager as node_manager
import apps.node_manager.api.node_tag as node_tag
import apps.audit.api.auditAndLogger as auditAndLogger
import apps.setting.api.settings as setting
import apps.user_manager.api.userInfo as userInfo
import apps.message.api.message as message

urlpatterns = [
    # 认证
    path('api/auth/login', user_auth.AuthLogin),  # 用户登入（POST）
    path('api/auth/logout', user_auth.AuthOutLog),  # 用户登出（ALL）
    path('api/auth/nodeAuth', node_auth.node_auth),  # 节点认证（POST）
    # 用户管理
    path('api/admin/userManager/getUserList', user_manager.getUserList),  # 获取用户列表（ALL）
    path('api/admin/userManager/addUser', user_manager.addUser),  # 新增用户（POST）
    path('api/admin/userManager/delUser', user_manager.delUser),  # 删除用户（POST）
    path('api/admin/userManager/getUserPermission', user_manager.getUserPermission),  # 获取用户权限（POST）
    path('api/admin/userManager/getUserInfo', user_manager.getUserInfo),  # 获取用户信息（POST）
    path('api/admin/userManager/setUserInfo', user_manager.setUserInfo),  # 设置用户信息（POST）
    # 权限管理
    path('api/admin/permissionManager/getPermissionGroups', permission_manager.getPermissionGroupsList),  # 获取权限组列表（ALL）
    path('api/admin/permissionManager/getPermissionList', permission_manager.getPermissionList),  # 获取权限列表（ALL）
    path('api/admin/permissionManager/addPermissionGroup', permission_manager.addPermissionGroup),  # 新增权限组列表 （POST）
    path('api/admin/permissionManager/delPermissionGroup', permission_manager.delPermissionGroup),  # 删除权限组 （POST）
    path('api/admin/permissionManager/getPermissionGroupInfo', permission_manager.getPermissionGroupInfo),  # 获取权限组信息 （POST）
    path('api/admin/permissionManager/setPermissionGroup', permission_manager.setPermissionGroup),  # 设置权限组 （POST）
    # 节点管理器
    path('api/node_manager/addNode', node_manager.add_node),  # 添加节点(POST)
    path('api/node_manager/delNode', node_manager.del_node),  # 删除节点(POST)
    path('api/node_manager/editNode', node_manager.edit_node),  # 编辑节点(POST)
    path('api/node_manager/resetToken', node_manager.reset_node_token),  # 重置节点Token(POST)
    path('api/node_manager/getNodeList', node_manager.get_node_list),  # 获取节点列表(POST)
    path('api/node_manager/getNodeInfo', node_manager.get_node_info),  # 获取节点信息(POST)
    path('api/node_manager/node_tag/search_tag', node_tag.search_tag),  # 搜索TAG(POST)
    # 审计
    path('api/admin/auditAndLogger/audit', auditAndLogger.getAudit),  # 获取审计日志（POST）
    path('api/admin/auditAndLogger/accessLog', auditAndLogger.getAccessLog),  # 获取访问日志（POST）
    path('api/admin/auditAndLogger/fileChangeLog', auditAndLogger.getFileChangeLog),  # 获取文件日志（POST）
    path('api/admin/auditAndLogger/systemLog', auditAndLogger.getSystemLog),  # 获取系统日志（POST）
    # 系统设置
    path('api/admin/settings/getSettings', setting.getSetting),  # 获取设置信息
    path('api/admin/settings/editSettings', setting.editSetting),  # 编辑设置信息
    # 个人信息编辑
    path("api/userInfo/getInfo", userInfo.getUserInfo),  # 获取个人信息（ALL）
    path("api/userInfo/editInfo", userInfo.setUserInfo),  # 修改个人信息（POST）
    path('api/userInfo/uploadAvatar', userInfo.uploadAvatar),  # 头像上传（POST）
    path('api/userInfo/getAvatar', userInfo.getAvatar),  # 获取头像（GET）
    path("api/userInfo/setPassword", userInfo.setPassword),  # 设置密码（POST）
    # 消息
    path('api/message/message', message.get_message_list),  # 获取消息列表（GET）
    # 静态页面
    re_path('.*', TemplateView.as_view(template_name="index.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
