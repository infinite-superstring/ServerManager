from django.db import models


# Create your models here.

class Permission_groups(models.Model):
    """权限组列表"""
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField("权限组名", max_length=30, unique=True)
    creator = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING, null=True)
    createdAt = models.DateTimeField("创建时间", auto_now_add=True)
    permissions = models.ManyToManyField('Permission_Item', related_name='groups')
    disable = models.BooleanField("是否禁用", null=True)


class Permission_Item(models.Model):
    """权限列表"""
    id = models.AutoField("权限项ID", primary_key=True, unique=True)
    permission = models.CharField("权限名", max_length=30, unique=True)
    description = models.CharField("权限项介绍", max_length=100, null=True)
    translate = models.CharField("权限翻译", max_length=30, unique=True, null=True)
