from django.db import models


# Create your models here.

# 审计
class Audit(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    time = models.DateTimeField("发生时间", auto_now_add=True)
    action = models.CharField("动作", max_length=256)
    module = models.CharField("模块", max_length=256)
    content = models.CharField("数据", max_length=4096)


# 系统日志
class System_Log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    time = models.DateTimeField("发生时间", auto_now_add=True)
    level = models.IntegerField("日志等级")
    module = models.CharField("模块", max_length=256)
    content = models.CharField("日志内容", max_length=1024)


# 访问日志
class Access_Log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    ip = models.GenericIPAddressField("IP地址", null=True)
    time = models.DateTimeField("操作时间", auto_now_add=True)
    module = models.CharField("访问的模块", max_length=512)


# 文件修改日志
class FileChange_Log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", db_column="用户", on_delete=models.DO_NOTHING)
    time = models.DateTimeField("操作时间", auto_now_add=True)
    action = models.CharField("动作", max_length=512)
    filepath = models.CharField("目标文件", max_length=4096)