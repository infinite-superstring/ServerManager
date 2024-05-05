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

import auth.api.user_auth as auth
import user_manager.api.user_management as user_management
import permission_manager.api.permission as permission_management
import node_manager.api.node_manager as node_manager
import node_manager.api.node_tag as node_tag
import audit.api.auditAndLogger as auditAndLogger
import setting.api.settings as setting
import user_manager.api.userInfo as userInfo

urlpatterns = [
    # 认证
    path('auth/login', auth.AuthLogin),  # 登入（POST）
    path('auth/logout', auth.AuthOutLog),  # 登出（ALL）
    # 用户管理
    path('admin/api/getUserList', user_management.getUserList),  # 获取用户列表（ALL）
    path('admin/api/addUser', user_management.addUser),  # 新增用户（POST）
    path('admin/api/delUser', user_management.delUser),  # 删除用户（POST）
    path('admin/api/getUserPermission', user_management.getUserPermission),  # 获取用户权限（POST）
    path('admin/api/getUserInfo', user_management.getUserInfo),  # 获取用户信息（POST）
    path('admin/api/setUserInfo', user_management.setUserInfo),  # 设置用户信息（POST）
    # 权限管理
    path('admin/api/getPermissionGroups', permission_management.getPermissionGroupsList),  # 获取权限组列表（ALL）
    path('admin/api/getPermissionList', permission_management.getPermissionList),  # 获取权限列表（ALL）
    path('admin/api/addPermissionGroup', permission_management.addPermissionGroup),  # 新增权限组列表 （POST）
    path('admin/api/delPermissionGroup', permission_management.delPermissionGroup),  # 删除权限组 （POST）
    path('admin/api/getPermissionGroupInfo', permission_management.getPermissionGroupInfo),  # 获取权限组信息 （POST）
    path('admin/api/setPermissionGroup', permission_management.setPermissionGroup),  # 设置权限组 （POST）
    # 节点管理器
    path('node_manager/addNode', node_manager.add_node),  # 添加节点(POST)
    path('node_manager/delNode', node_manager.del_node),  # 删除节点(POST)
    path('node_manager/editNode', node_manager.edit_node),  # 编辑节点(POST)
    path('node_manager/getNodeList', node_manager.get_node_list),  # 获取节点列表(POST)
    path('node_manager/getNodeInfo', node_manager.get_node_info),  # 获取节点信息(POST)
    path('node_tag/search_tag', node_tag.search_tag),  # 搜索TAG(POST)
    # 审计
    path('admin/api/auditAndLogger/audit', auditAndLogger.getAudit),  # 获取审计日志（POST）
    path('admin/api/auditAndLogger/accessLog', auditAndLogger.getAccessLog),  # 获取访问日志（POST）
    path('admin/api/auditAndLogger/fileChangeLog', auditAndLogger.getFileChangeLog),  # 获取文件日志（POST）
    path('admin/api/auditAndLogger/systemLog', auditAndLogger.getSystemLog),  # 获取系统日志（POST）
    # 系统设置
    path('admin/api/settings/getSettings', setting.getSetting),  # 获取设置信息
    path('admin/api/settings/editSettings', setting.editSetting),  # 编辑设置信息
    # 个人信息编辑
    path("userInfo/api/getInfo", userInfo.getUserInfo),  # 获取个人信息（ALL）
    path("userInfo/api/editInfo", userInfo.setUserInfo),  # 修改个人信息（POST）
    path('userInfo/api/uploadAvatar', userInfo.uploadAvatar),  # 头像上传（POST）
    path('userInfo/api/getAvatar', userInfo.getAvatar),  # 获取头像（GET）
    path("userInfo/api/setPassword", userInfo.setPassword),  # 设置密码（POST）
    # 静态页面
    re_path('.*', TemplateView.as_view(template_name="index.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
