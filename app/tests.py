from django.test import TestCase
from user_manager.models import *
from setting.models import *
from util.passwordUtils import *
from permission_manager.util.permission import *


# Create your tests here.

class AppTest(TestCase):
    def setUp(self):
        PermissionItem = [
            {
                'id': 1,
                'permission': 'all',
                'description': '所有权限，拥有该权限的组无需指定其他权限',
                'translate': '所有权限'
            },
            {
                'id': 2,
                'permission': 'viewDevice',
                'description': '允许观看设备屏幕，不可控制设备',
                'translate': '观看被控设备'
            },
            {
                'id': 3,
                'permission': 'controllingDevice',
                'description': '允许用户控制设备',
                'translate': '控制被控设备'
            },
            {
                'id': 4,
                'permission': 'changeDevicePowerState',
                'description': '允许用户操作设备按钮，可实现强制关机与重启',
                'translate': '控制被控电源'
            },
            {
                'id': 5,
                'permission': 'changeSettings',
                'description': '允许用户更改LoongArch-Server-Manager设置',
                'translate': '更改设备设置'
            },
            {
                'id': 6,
                'permission': 'manageUsers',
                'description': '允许用户管理LoongArch-Server-Manager用户',
                'translate': '管理用户'
            },
            {
                'id': 7,
                'permission': 'managePermissionGroups',
                'description': '允许用户管理权限设定',
                'translate': '管理权限组'
            },
            {
                'id': 8,
                'permission': 'viewAudit',
                'description': '允许用户浏览审计信息',
                'translate': '查看审计数据'
            },
            {
                'id': 9,
                'permission': 'editAudit',
                'description': '允许用户清除审计数据',
                'translate': '管理审计数据'
            }
        ]

        for item in PermissionItem:
            Permission_Item.objects.get_or_create(**item)

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
                    viewDevice,
                    controllingDevice,
                    changeDevicePowerState,
                    changeSettings,
                    manageUsers,
                    managePermissionGroups,
                    viewAudit,
                ]
            },
            {
                'id': 3,
                'name': '运维(O&M)',
                'permissions': [
                    viewDevice,
                    controllingDevice,
                    changeDevicePowerState,
                    changeSettings,
                    viewAudit,
                ]
            },
            {
                'id': 4,
                'name': '开发(dev)',
                'permissions': [
                    viewDevice,
                    controllingDevice,
                ]
            }
        ]

        for item in PermissionGroup:
            group, status = Permission_groups.objects.get_or_create(id=item['id'], name=item['name'])
            if status:
                for permission in item['permissions']:
                    group.permissions.add(permission)

        DefaultSetting = [
            {
                'Settings': "base.record",
                'value': True
            },
            {
                'Settings': "camera.width",
                'value': 1920
            },
            {
                'Settings': "camera.height",
                'value': 1080
            },
            {
                'Settings': "camera.fps",
                'value': 30
            },
            {
                'Settings': "camera.brightness",
                'value': -14
            },
            {
                'Settings': "camera.exposure",
                'value': -4
            },
            {
                'Settings': "camera.colorfulness",
                'value': 164
            },
            {
                'Settings': "camera.tonal",
                'value': -4
            },
            {
                'Settings': "camera.updateDisplayChange",
                'value': 0.01
            },
            {
                'Settings': "record.fps",
                'value': 15
            },
            {
                'Settings': "record.maxFile",
                'value': 16
            },
            {
                'Settings': "base.sessionExpiry",
                'value': 0
            },
            {
                'Settings': "base.HID_Serial",
                'value': "/dev/ttyS5"
            },
            {
                'Settings': "base.camera",
                'value': 0
            },
            {
                'Settings': "base.USB_Device",
                'value': "/dev/sdb"
            },
            {
                'Settings': "base.USB_MountDirectory",
                'value': "/"
            },
            {
                'Settings': "gpio.mode",
                'value': "OrangePi GPIO"
            },
            {
                'Settings': "gpio.pollingRate",
                'value': 0.5
            },
            {
                'Settings': "gpio.Power_LED",
                'value': 9
            },
            {
                'Settings': "gpio.HDD_LED",
                'value': 8
            },
            {
                'Settings': "gpio.Restart_Btn",
                'value': 5
            },
            {
                'Settings': "gpio.Power_Btn",
                'value': 6
            },
            {
                'Settings': "gpio.UsbDisk_EN",
                'value': 18
            },
            {
                'Settings': "gpio.UsbDisk_Switch",
                'value': 17
            },
        ]

        for item in DefaultSetting:
            Settings.objects.get_or_create(**item)

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

    def test_getGroupPermission(self):
        print(groupPermission(1).get_permissions_list())
        # print(groupPermission(1000).get_permissions_list())

    def test_check_group_permission(self):
        gp = groupPermission(1)
        print(gp.get_permissions_list())
        print(gp.check_group_permission("all"))
        print(gp.check_group_permission("aaaa"))

    def test_get_all_permission_items(self):
        print(get_all_permission_items())

    def test_get_permissions_dict(self):
        gp = groupPermission(3)
        print(gp.get_permissions_dict())

    def test_update_permissions_list(self):
        gp = groupPermission(1)
        gp.update_permissions_list(["changeDevicePowerState", "editAudit"])
        print(gp.get_permissions_dict())

    def test_get_all_permission_item_info(self):
        print(get_all_permission_item_info())

    def test_password_tools(self):
        defaultPassword = GeneratePassword(16)

        hashed_password, salt = encrypt_password(defaultPassword)

        print(verify_password(hashed_password, defaultPassword, salt))
