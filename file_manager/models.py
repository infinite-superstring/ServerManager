import uuid

from django.db import models


# Create your models here.

# 临时下载链接
class Temporary_link(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    userID = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    filePath = models.CharField("文件路径", max_length=255)
    createdAt = models.DateTimeField("链接创建时间", auto_now_add=True)
    validTime = models.DateTimeField("有效时间")
    availableCount = models.IntegerField("可用次数", default=1)
    usageCount = models.IntegerField("已使用次数", default=0)
    used = models.BooleanField(default=False)
