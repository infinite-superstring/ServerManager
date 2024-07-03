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
import django_eventstream
from django.urls import path, re_path, include

import apps.auth.api.user_auth as user_auth
import apps.auth.api.node_auth as node_auth
import apps.auth.api.otp as otp
import apps.auth.api.OTP_Bind as otp_bind
import apps.user_manager.api.user_management as user_manager
import apps.permission_manager.api.permission as permission_manager
import apps.node_manager.api.node_manager as node_manager
import apps.node_manager.api.node_tag as node_tag
import apps.node_manager.api.node_group as node_group
import apps.node_manager.api.node_info as node_info
import apps.node_manager.api.node_event as node_event
import apps.node_manager.api.terminal_record as terminal_record
import apps.audit.api.auditAndLogger as auditAndLogger
import apps.setting.api.settings as setting
import apps.user_manager.api.userInfo as userInfo
import apps.message.api.message as message
import apps.dashboard.api.dashboard as dashboard
import apps.patrol.api.patrol as patrol
import apps.task.api.task as task
import apps.web_status.api.webStatus as webStatus

urlpatterns = [
    # 认证
    path('api/auth/login', user_auth.AuthLogin),  # 用户登入（POST）
    path('api/auth/logout', user_auth.AuthOutLog),  # 用户登出（ALL）
    path('api/auth/getUserLoginStatus', user_auth.getLoginStatus),  # 获取用户登录状态 (ALL)
    path('api/auth/nodeAuth', node_auth.node_auth),  # 节点认证（POST）
    path('api/auth/OTP/bind/sendEmailCode', otp_bind.send_email_code),  # 发送邮箱验证码
    path('api/auth/OTP/bind/verifyEmailCode', otp_bind.check_emali_code),  # 检查邮箱验证码
    path('api/auth/OTP/bind/verifyOTP_Code', otp_bind.bind_otp_check),  # 检查
    path('api/auth/OTP/verify/checkOTP', otp.check_otp_input),
    # 用户管理
    path('api/admin/userManager/getUserList', user_manager.getUserList),  # 获取用户列表（POST）
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
    path('api/admin/permissionManager/getPermissionGroupInfo', permission_manager.getPermissionGroupInfo),
    # 获取权限组信息 （POST）
    path('api/admin/permissionManager/setPermissionGroup', permission_manager.setPermissionGroup),  # 设置权限组 （POST）
    # 节点管理器
    path('api/node_manager/addNode', node_manager.add_node),  # 添加节点(POST)
    path('api/node_manager/delNode', node_manager.del_node),  # 删除节点(POST)
    path('api/node_manager/editNode', node_manager.edit_node),  # 编辑节点(POST)
    path('api/node_manager/resetToken', node_manager.reset_node_token),  # 重置节点Token(POST)
    path('api/node_manager/getNodeList', node_manager.get_node_list),  # 获取节点列表(POST)
    path('api/node_manager/getBaseNodeList', node_manager.get_base_node_list),  # 获取基础节点列表(POST)
    path('api/node_manager/getNodeInfo', node_manager.get_node_info),  # 获取节点信息(POST)
    path('api/node_manager/node_tag/search_tag', node_tag.search_tag),  # 搜索TAG(POST)
    path('api/node_manager/node_group/getGroupList', node_group.get_group_list),  # 获取组列表(POST)
    path('api/node_manager/node_group/createGroup', node_group.create_group),  # 创建组(POST)
    path('api/node_manager/node_group/delGroup', node_group.del_group),  # 删除节点组(POST)
    path('api/node_manager/node_group/getGroupById', node_group.get_group_by_id),  # 获取节点组详情
    path('api/node_manager/node_info/get_disk_partition_list', node_info.get_disk_partition_list),  # 获取节点磁盘列表(POST)
    path('api/node_manager/node_info/get_alarm_setting', node_info.get_alarm_setting),  # 获取节点告警设置(POST)
    path('api/node_manager/node_info/save_alarm_setting', node_info.save_alarm_setting),  # 保存节点告警设置(POST)
    path('api/node_manager/node_event/get_node_events', node_event.get_node_events),  # 获取节点事件列表(POST)
    path('api/node_manager/node_event/get_event_info', node_event.get_event_info),  # 获取事件信息
    path('event/node_manager/updateNodeList', include(django_eventstream.urls), {"channels": ["updateNodeList"]}),
    # 审计
    path('api/admin/auditAndLogger/audit', auditAndLogger.getAudit),  # 获取审计日志（POST）
    path('api/admin/auditAndLogger/accessLog', auditAndLogger.getAccessLog),  # 获取访问日志（POST）
    path('api/admin/auditAndLogger/fileChangeLog', auditAndLogger.getFileChangeLog),  # 获取文件日志（POST）
    path('api/admin/auditAndLogger/systemLog', auditAndLogger.getSystemLog),  # 获取系统日志（POST）
    path('api/admin/auditAndLogger/userSessionLog', auditAndLogger.get_user_session_log),  # 获取用户会话记录(POST)
    path('api/admin/auditAndLogger/nodeSessionLog', auditAndLogger.get_node_session_log),  # 获取节点会话记录(POST)
    path('api/admin/auditAndLogger/terminalRecord/loadNodeList', terminal_record.load_node_list),  # 加载节点列表
    path('api/admin/auditAndLogger/terminalRecord/loadUserList', terminal_record.load_terminal_user_list),  # 加载终端用户列表
    path('api/admin/auditAndLogger/terminalRecord/loadSessionList', terminal_record.load_terminal_session_list),  # 加载终端会话列表
    path('api/admin/auditAndLogger/terminalRecord/loadSessionRecord', terminal_record.load_terminal_session_record),  # 加载终端会话记录
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
    path('api/message/getList', message.get_message_list),  # 获取消息列表（GET）
    path('api/message/getById', message.get_by_id),  # 按ID获取消息(GET)
    path('api/message/deleteAll', message.delete_all),  # 删除所有消息(DELETE)
    path('api/message/readAll', message.read_all),  # 已读所有消息(PUT)
    path('api/message/deleteById', message.delete_by_id),  # 按ID删除消息(DELETE)
    path('api/message/getUnread', message.get_unread),  # 获取未读消息数量
    # 巡检记录
    path('api/patrol/addARecord', patrol.addARecord),  # 添加巡检记录(POST)
    path('api/patrol/getList', patrol.getList),  # 获取巡检记录列表(POST)
    path('api/patrol/updateARecord', patrol.updateRecord),  # 更新巡检记录(PUT)
    path('api/patrol/deleteRecord', patrol.deleteRecord),  # 删除巡检记录(DELETE)
    # 仪表盘
    path('api/dashboard/getOverview', dashboard.get_overview),  # 获取总览(ALL)
    path('api/dashboard/getNodeList', dashboard.get_node_list),  # 获取节点列表(POST)
    path('api/dashboard/getStatistics', dashboard.get_statistics),  # 获取统计信息(GET)
    path('api/dashboard/getTasks', dashboard.get_tasks),  # 获取任务列表(GET)
    # 任务
    path('api/task/getCheckInStatus', task.getCheckInStatus),  # 获取签到状态(GET)
    path('api/task/attendanceCheckIn', task.attendanceCheckIn),  # 签到(POST)
    # 任务-值班记录
    path('api/task/getDuty', task.getDuty),  # 获取值班记录(GET)
    # Web状态
    path('api/webStatus/getList', webStatus.getList),  # 获取Web状态列表(GET)
    path('api/webStatus/addWeb', webStatus.addWeb),  # 添加Web状态(POST)
    path('api/webStatus/delWeb/<str:id>', webStatus.delWeb),  # 删除监控的web(DELETE)
    path('api/webStatus/update', webStatus.update),  # 更新Web状态(PUT)
]
