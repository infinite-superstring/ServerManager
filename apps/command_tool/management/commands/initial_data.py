import secrets

from django.core.management.base import BaseCommand
from apps.permission_manager.models import Permission_groups, Permission_Item
from apps.user_manager.models import User
from apps.setting.models import Settings
from util.logger import Log
from util.passwordUtils import GeneratePassword, encrypt_password


class Command(BaseCommand):
    help = 'Creates initial data'

    def handle(self, *args, **options):
        Log.info("开始初始化数据库~")
        PermissionItem = [
            {
                'permission': 'all',
                'description': '所有权限，拥有该权限的组无需指定其他权限',
                'translate': '所有权限'
            },
            {
                'permission': 'visitAllNodes',
                'description': '允许用户访问所有节点',
                'translate': '访问所有节点'
            },
            {
                'permission': 'addNode',
                'description': '允许用户新增节点',
                'translate': '新增节点'
            },
            {
                'permission': 'editNodeGroup',
                'description': '允许用户编排节点组',
                'translate': '编辑节点组'
            },
            {
                'permission': 'clusterExecuteCommand',
                'description': '允许用户执行集群命令',
                'translate': '集群命令'
            },
            {
                'permission': 'clusterTask',
                'description': '允许用户添加/修改/删除集群任务',
                'translate': '集群任务'
            },
            {
                'permission': 'allocateNode',
                'description': '允许用户分配节点',
                'translate': '分配节点'
            },
            {
                'permission': 'changeSettings',
                'description': '允许用户更改LoongArch-Server-Manager设置',
                'translate': '更改设备设置'
            },
            {
                'permission': 'manageUser',
                'description': '允许用户管理LoongArch-Server-Manager用户',
                'translate': '管理用户'
            },
            {
                'permission': 'managePermissionGroup',
                'description': '允许用户管理权限设定',
                'translate': '管理权限组'
            },
            {
                'permission': 'viewAudit',
                'description': '允许用户浏览审计信息',
                'translate': '查看审计数据'
            },
            {
                'permission': 'clearAudit',
                'description': '允许用户清除审计数据',
                'translate': '管理审计数据'
            },
            {
                'permission': 'viewDuty',
                'description': '允许用户查看值班记录',
                'translate': '管理值班记录'
            },
            {
                'permission': 'viewWebStatus',
                'description': '允许用户查看网站监控',
                'translate': '管理网站监控'
            },
            {
                "permission": "viewPatrol",
                "description": "允许用户查看巡检记录",
                "translate": "管理巡检记录",
            },

        ]

        for item in PermissionItem:
            Permission_Item.objects.get_or_create(**item)
        Log.success("权限项初始化完成")

        all = Permission_Item.objects.get(id=1)
        viewDevice = Permission_Item.objects.get(id=2)
        controllingDevice = Permission_Item.objects.get(id=3)
        changeDevicePowerState = Permission_Item.objects.get(id=4)
        changeSettings = Permission_Item.objects.get(id=5)
        manageUsers = Permission_Item.objects.get(id=6)
        managePermissionGroups = Permission_Item.objects.get(id=7)
        viewAudit = Permission_Item.objects.get(id=8)
        editAudit = Permission_Item.objects.get(id=9)

        PermissionGroup = [
            {
                'id': 1,
                'name': '超级管理员(super_admin)',
                'permissions': [
                    all,
                    viewDevice,
                    controllingDevice,
                    changeDevicePowerState,
                    changeSettings,
                    manageUsers,
                    managePermissionGroups,
                    viewAudit,
                    editAudit
                ]
            },
            {
                'id': 2,
                'name': '管理员(admin)',
                'permissions': [
                    changeSettings,
                    manageUsers,
                    managePermissionGroups,
                ]
            }
        ]

        for item in PermissionGroup:
            group, status = Permission_groups.objects.get_or_create(id=item['id'], name=item['name'])
            if status:
                for permission in item['permissions']:
                    group.permissions.add(permission)
        Log.success("权限组初始化完成")

        defaultSetting = [
            {
                'Settings': "base.website_name",
                'value': 'LoongArch-ServerManage'
            },
            {
                'Settings': "base.website_url",
                'value': ""
            },
            {
                'Settings': "base.server_token",
                'value': secrets.token_hex(32)
            },
            {
                'Settings': "base.session_expiry",
                'value': 0
            },
            {
                'Settings': "security.password_level",
                'value': 1
            },
            {
                'Settings': "security.auth_code_resend_interval",
                'value': 60
            },
            {
                'Settings': "security.auth_code_timeout",
                'value': 5
            },
            {
                'Settings': "security.auth_code_length",
                'value': 8
            },
            {
                'Settings': "security.login_error_count",
                'value': 5
            },
            {
                'Settings': "security.login_expiry",
                'value': 5
            },
            {
                'Settings': "node_usage.data_storage_time",
                'value': 180
            },
            {
                'Settings': "node_usage.data_save_interval",
                'value': 5
            },
            {
                'Settings': "node_usage.upload_data_interval",
                'value': 3
            },
            {
                'Settings': "node.timeout",
                'value': 16000
            },
            {
                'Settings': "node.heartbeat_time",
                'value': 3000
            },
            {
                'Settings': "node_default_alarm_setting.enable",
                'value': False
            },
            {
                'Settings': "node_default_alarm_setting.delay_seconds",
                'value': 360
            },
            {
                "Settings": "node_default_alarm_setting.interval",
                'value': 60
            },
            {
                'Settings': "node_default_alarm_setting.cpu__enable",
                'value': True
            },
            {
                'Settings': "node_default_alarm_setting.cpu__threshold",
                'value': 80
            },
            {
                'Settings': "node_default_alarm_setting.memory__enable",
                'value': True
            },
            {
                'Settings': "node_default_alarm_setting.memory__threshold",
                'value': 75
            },
            {
                'Settings': "node_default_alarm_setting.network__enable",
                'value': True
            },
            {
                'Settings': "node_default_alarm_setting.network__send_threshold",
                'value': 104858074
            },
            {
                'Settings': "node_default_alarm_setting.network__receive_threshold",
                'value': 104858074
            },
            {
                'Settings': "message.message_send_type",
                'value': "email"
            },
            {
                'Settings': "message.email_method",
                'value': "stp"
            },
            {
                'Settings': "message.email_host",
                'value': ""
            },
            {
                'Settings': "message.email_port",
                'value': "8080"
            },
            {
                'Settings': "message.email_username",
                'value': ""
            },
            {
                'Settings': "message.email_password",
                'value': ""
            },
            {
                'Settings': "message.email_ssl",
                'value': True
            },
            {
                'Settings': "message.email_from_address",
                'value': ""
            },
            {
                "Settings": "message.email_from_name",
                'value': ""
            },
            #     网站监控设置
            {
                'Settings': "web_status.heartbeat",
                'value': 5
            },
            {
                'Settings': "web_status.timeout",
                'value': 3
            },
            {
                'Settings': 'terminal_audit.enable',
                'value': False
            },
            {
                'Settings': 'terminal_audit.disable_tab_key',
                'value': True
            },
            {
                'Settings': 'terminal_audit.warn_command_list',
                'value': ""
            },
            {
                'Settings': 'terminal_audit.danger_command_list',
                'value': ""
            },
            {
                'Settings': 'terminal_audit.disable_command_list',
                'value': ""
            }
        ]

        for item in defaultSetting:
            Settings.objects.get_or_create(**item)
        Log.success("初始化设置成功")

        defaultPassword = GeneratePassword(16)

        hashed_password, salt = encrypt_password(defaultPassword)

        adminUser = {
            'username': 'admin',
            'realName': 'admin',
            'email': 'admin@localhost.com',
            'password': hashed_password,
            'passwordSalt': salt,
            'permission_id': '1'
        }

        User.objects.get_or_create(
            userName=adminUser['username'],
            realName=adminUser['realName'],
            email=adminUser['email'],
            password=adminUser['password'],
            passwordSalt=adminUser['passwordSalt'],
            permission_id=Permission_Item.objects.filter(id=1).first().id
        )
        Log.success("用户初始化成功")

        print("*" * 10 + "默认账户" + "*" * 10 + "\n" + f"用户名：{adminUser['username']}\n密码：{defaultPassword}")
