from django.db import models


# Create your models here.

# 用户列表
class User(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    userName = models.CharField("用户名", max_length=32, unique=True)
    realName = models.CharField("姓名", max_length=32, unique=True, null=True)
    email = models.EmailField("电子邮箱", max_length=100, unique=True, null=True)
    createdAt = models.DateTimeField("创建时间", null=True, auto_now_add=True)
    lastLoginTime = models.DateTimeField("上次登录时间", null=True, auto_now=True)
    lastLoginIP = models.GenericIPAddressField("上次登录IP", null=True)
    password = models.CharField("密码(md5)", max_length=128)
    passwordSalt = models.CharField("密码盐", max_length=128, null=False, unique=True)
    avatar = models.CharField("头像hash", max_length=64, null=True)
    permission = models.ForeignKey("permission_manager.Permission_groups", on_delete=models.DO_NOTHING, null=True)
    disable = models.BooleanField("是否禁用", default=False, null=True)
    class Meta:
        db_table = "users"
        db_table_comment = "用户"
