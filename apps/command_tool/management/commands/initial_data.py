import os.path
import secrets
import sys

from django.core.management.base import BaseCommand
from apps.permission_manager.models import Permission_groups, Permission_Item
from apps.user_manager.models import User
from apps.setting.models import Settings
from util.logger import Log
from util.passwordUtils import encrypt_password


class Command(BaseCommand):
    help = 'Creates initial data'

    def add_arguments(self, parser):
        # 添加一个可选参数
        parser.add_argument(
            '--force-init',
            action='store_true',
            help='强制初始化数据库'
        )

    def handle(self, *args, **options):
        init_flag_file_path = os.path.join(os.getcwd(), '.init')
        if not os.path.exists(init_flag_file_path) or '--force-init' in sys.argv:
            Log.info("开始初始化数据库~")
            self.__init_setting()
            self.__init_permission_item()
            self.__init_permission()
            self.__init_user()
            open(init_flag_file_path, 'w').close()
        else:
            Log.warning("您已经初始化过数据库啦，如需强制初始化数据库请添加参数：--force-init")


    def __init_permission_item(self):
        """
        初始化权限项
        """
        PermissionItem = [
            {
                'permission': 'all',
                'description': '所有权限，拥有该权限的组无需指定其他权限',
                'translate': '所有权限'
            },
            {
                'permission': 'viewAllNode',
                'description': '允许用户访问所有节点',
                'translate': '访问所有节点'
            },
            {
                'permission': 'editNode',
                'description': '允许用户编辑节点',
                'translate': '编辑节点'
            },
            {
                'permission': 'editNodeGroup',
                'description': '允许用户编排节点组',
                'translate': '编辑节点组'
            },
            {
                'permission': 'clusterTask',
                'description': '允许用户添加/修改/删除集群任务',
                'translate': '集群任务'
            },
            {
                'permission': 'viewWebStatus',
                'description': '允许用户查看网站监控',
                'translate': '查看网站监控'
            },
            {
                'permission': 'editWebStatus',
                'description': '允许用户添加/修改/删除网站监控',
                'translate': '管理网站监控'
            },
            {
                'permission': 'changeSettings',
                'description': '允许用户更改系统设置',
                'translate': '更改系统设置'
            },
            {
                'permission': 'manageUser',
                'description': '允许用户管理用户',
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
                'permission': 'viewDuty',
                'description': '允许用户查看值班记录',
                'translate': '管理值班记录'
            },
            {
                "permission": "viewPatrol",
                "description": "允许用户查看巡检记录",
                "translate": "查看巡检记录",
            },
            {
                "permission": "editPatrol",
                "description": "允许用户维护巡检记录",
                "translate": "管理巡检记录",
            },

        ]

        for item in PermissionItem:
            Permission_Item.objects.get_or_create(**item)
        Log.success("权限项初始化完成")

    def __init_permission(self):
        """
        初始化权限
        """
        PermissionGroup = [
            {
                'name': '超级管理员(super_admin)',
                'permissions': [
                    'all',
                    'viewAllNode',
                    'editNode',
                    'editNodeGroup',
                    'clusterTask',
                    'viewWebStatus',
                    'editWebStatus',
                    'changeSettings',
                    'manageUser',
                    'managePermissionGroup',
                    'viewAudit',
                    'viewDuty',
                    'viewPatrol',
                    'editPatrol'
                ]
            },
            {
                'name': '管理员(admin)',
                'permissions': [
                    'viewAllNode',
                    'editNode',
                    'editNodeGroup',
                    'clusterTask',
                    'viewWebStatus',
                    'editWebStatus',
                    'viewAudit',
                    'viewDuty',
                    'viewPatrol',
                    'editPatrol'
                ]
            },
            {
                'name': '普通用户(user)',
                'permissions': [
                    'editNode',
                    'clusterTask',
                    'viewWebStatus',
                    'viewPatrol',
                    'editPatrol'
                ]
            }
        ]

        for item in PermissionGroup:
            group, status = Permission_groups.objects.get_or_create(name=item['name'], disable=False)
            if status:
                for permission in item.get('permissions'):
                    if not Permission_Item.objects.filter(permission=permission).exists():
                        Log.warning(f"权限组{group.name}权限配置失败，缺少权限项：{permission}")
                        break
                    group.permissions.add(Permission_Item.objects.get(permission=permission))
        Log.success("权限组初始化完成")

    def __init_setting(self):
        """
        初始化设置
        """
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
                'value': 1
            },
            {
                'Settings': "security.password_level",
                'value': 1
            },
            {
                'Settings': "security.force_otp_bind",
                'value': False
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
            # 节点告警默认设置
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
            # 消息设置
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

    def __init_user(self):
        defaultPassword = "123456"

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
            permission_id=Permission_Item.objects.filter(id=1).first().id,
            isNewUser=False,
        )
        Log.success("用户初始化成功")

        print("*" * 10 + "默认账户" + "*" * 10 + "\n" + f"用户名：{adminUser['username']}\n密码：{defaultPassword}")
